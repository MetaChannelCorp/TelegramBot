import os
import logging
import re
import xmlrpc.client
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

load_dotenv()

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_USER_IDS = [
    int(uid.strip())
    for uid in os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")
    if uid.strip()
]

ODOO_URL      = os.getenv("ODOO_URL")
ODOO_DB       = os.getenv("ODOO_DB")
ODOO_USER     = os.getenv("ODOO_USER")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# ESTADOS de la conversación
# ─────────────────────────────────────────────

(
    TIPO_CONTACTO,
    NOMBRE_EMPRESA,
    NOMBRE,
    APELLIDO,
    TELEFONO,
    EMAIL,
    EMPRESA_VINCULADA,
    CONFIRMAR,
) = range(8)

# ─────────────────────────────────────────────
# CLIENTE ODOO
# ─────────────────────────────────────────────

class OdooClient:
    def __init__(self, url, db, user, password):
        self.url      = url
        self.db       = db
        self.user     = user
        self.password = password
        self.uid      = None
        self._models  = None

    def _connect(self):
        common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.uid = common.authenticate(self.db, self.user, self.password, {})
        if not self.uid:
            raise ConnectionError("No se pudo autenticar en Odoo.")
        self._models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def _ensure_connected(self):
        if not self.uid:
            self._connect()

    def test_connection(self):
        try:
            self._connect()
            return True
        except Exception as e:
            logger.error(f"Error de conexión Odoo: {e}")
            return False

    def buscar_empresa(self, nombre):
        self._ensure_connected()
        ids = self._models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "search",
            [[["is_company", "=", True], ["name", "ilike", nombre]]],
            {"limit": 5},
        )
        if not ids:
            return []
        return self._models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "read",
            [ids], {"fields": ["id", "name"]},
        )

    def crear_empresa(self, nombre):
        self._ensure_connected()
        partner_id = self._models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "create",
            [{"name": nombre, "is_company": True}],
        )
        logger.info(f"Empresa creada: {nombre} (ID={partner_id})")
        return partner_id

    def crear_contacto(self, datos):
        self._ensure_connected()
        nombre_completo = datos.get("nombre", "").strip()
        apellido = datos.get("apellido", "").strip()
        if apellido:
            nombre_completo = f"{nombre_completo} {apellido}"
        vals = {
            "name":       nombre_completo,
            "is_company": False,
        }
        if datos.get("telefono"):
            vals["phone"] = datos["telefono"]
        if datos.get("email"):
            vals["email"] = datos["email"]
        if datos.get("empresa_id"):
            vals["parent_id"] = datos["empresa_id"]
        partner_id = self._models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "create", [vals],
        )
        logger.info(f"Contacto creado: {nombre_completo} (ID={partner_id})")
        return partner_id

    def listar_contactos_recientes(self, limite=5):
        self._ensure_connected()
        ids = self._models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "search",
            [[["is_company", "=", False]]],
            {"limit": limite, "order": "id desc"},
        )
        if not ids:
            return []
        return self._models.execute_kw(
            self.db, self.uid, self.password,
            "res.partner", "read",
            [ids], {"fields": ["id", "name", "phone", "email", "parent_id"]},
        )

odoo = OdooClient(ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def check_allowed(user_id):
    if not ALLOWED_USER_IDS:
        return True
    return user_id in ALLOWED_USER_IDS

def validar_email(email):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

def validar_telefono(telefono):
    return bool(re.match(r"^[\d\s\+\-\(\)]{6,20}$", telefono))

def resumen_datos(ctx_data):
    tipo = ctx_data.get("tipo", "contacto")
    lineas = [f"📋 *Resumen:*\n"]
    if tipo == "empresa":
        lineas.append(f"🏢 Empresa: {ctx_data.get('nombre_empresa', '—')}")
    else:
        nombre = ctx_data.get("nombre", "—")
        apellido = ctx_data.get("apellido", "")
        lineas.append(f"👤 Nombre: {nombre} {apellido}".strip())
        if ctx_data.get("telefono"):
            lineas.append(f"📞 Teléfono: {ctx_data['telefono']}")
        if ctx_data.get("email"):
            lineas.append(f"✉️ Email: {ctx_data['email']}")
        if ctx_data.get("empresa_nombre"):
            lineas.append(f"🏢 Empresa: {ctx_data['empresa_nombre']}")
    return "\n".join(lineas)

# ─────────────────────────────────────────────
# COMANDOS GENERALES
# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_allowed(update.effective_user.id):
        await update.message.reply_text("🚫 No tienes acceso a este bot.")
        return
    await update.message.reply_text(
        "👋 *Hola, soy tu asistente de CRM para Odoo.*\n\n"
        "📌 *Comandos disponibles:*\n"
        "/nuevo — Añadir contacto o empresa\n"
        "/recientes — Ver últimos contactos\n"
        "/estado — Comprobar conexión con Odoo\n"
        "/cancelar — Cancelar operación actual",
        parse_mode="Markdown",
    )

async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_allowed(update.effective_user.id):
        return
    msg = await update.message.reply_text("⏳ Comprobando conexión con Odoo...")
    if odoo.test_connection():
        await msg.edit_text(
            f"✅ *Conexión exitosa con Odoo*\n\n"
            f"🌐 URL: {ODOO_URL}\n"
            f"🗄️ Base de datos: {ODOO_DB}\n"
            f"👤 Usuario: {ODOO_USER}",
            parse_mode="Markdown",
        )
    else:
        await msg.edit_text("❌ No se pudo conectar a Odoo. Verifica que Docker está corriendo.")

async def recientes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_allowed(update.effective_user.id):
        return
    try:
        contactos = odoo.listar_contactos_recientes(5)
        if not contactos:
            await update.message.reply_text("📭 No hay contactos en el CRM todavía.")
            return
        lines = ["📋 *Últimos 5 contactos:*\n"]
        for c in contactos:
            empresa = c["parent_id"][1] if c.get("parent_id") else "—"
            lines.append(
                f"• *{c['name']}*\n"
                f"  📞 {c.get('phone') or '—'}  ✉️ {c.get('email') or '—'}\n"
                f"  🏢 {empresa}"
            )
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al consultar Odoo: {e}")

# ─────────────────────────────────────────────
# CONVERSACIÓN — /nuevo
# ─────────────────────────────────────────────

async def nuevo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not check_allowed(update.effective_user.id):
        return ConversationHandler.END
    context.user_data.clear()
    teclado = [[
        InlineKeyboardButton("👤 Contacto", callback_data="tipo_contacto"),
        InlineKeyboardButton("🏢 Empresa",  callback_data="tipo_empresa"),
    ]]
    await update.message.reply_text(
        "¿Qué quieres añadir al CRM?",
        reply_markup=InlineKeyboardMarkup(teclado),
    )
    return TIPO_CONTACTO

async def elegir_tipo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    tipo = "empresa" if query.data == "tipo_empresa" else "contacto"
    context.user_data["tipo"] = tipo
    if tipo == "empresa":
        await query.edit_message_text("🏢 ¿Cuál es el nombre de la empresa?")
        return NOMBRE_EMPRESA
    else:
        await query.edit_message_text("👤 ¿Cuál es el *nombre* del contacto?", parse_mode="Markdown")
        return NOMBRE

async def recibir_nombre_empresa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["nombre_empresa"] = update.message.text.strip()
    teclado = [[
        InlineKeyboardButton("✅ Confirmar", callback_data="confirmar_si"),
        InlineKeyboardButton("❌ Cancelar",  callback_data="confirmar_no"),
    ]]
    await update.message.reply_text(
        resumen_datos(context.user_data) + "\n\n¿Confirmas?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(teclado),
    )
    return CONFIRMAR

async def recibir_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["nombre"] = update.message.text.strip()
    await update.message.reply_text("¿Cuál es el *apellido*? (escribe `-` para omitirlo)", parse_mode="Markdown")
    return APELLIDO

async def recibir_apellido(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    texto = update.message.text.strip()
    context.user_data["apellido"] = "" if texto == "-" else texto
    await update.message.reply_text("📞 ¿Cuál es el *teléfono*? (escribe `-` para omitirlo)", parse_mode="Markdown")
    return TELEFONO

async def recibir_telefono(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    texto = update.message.text.strip()
    if texto != "-":
        if not validar_telefono(texto):
            await update.message.reply_text("⚠️ Teléfono no válido. Inténtalo de nuevo o escribe `-` para omitirlo.")
            return TELEFONO
        context.user_data["telefono"] = texto
    await update.message.reply_text("✉️ ¿Cuál es el *email*? (escribe `-` para omitirlo)", parse_mode="Markdown")
    return EMAIL

async def recibir_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    texto = update.message.text.strip()
    if texto != "-":
        if not validar_email(texto):
            await update.message.reply_text("⚠️ Email no válido. Inténtalo de nuevo o escribe `-` para omitirlo.")
            return EMAIL
        context.user_data["email"] = texto
    await update.message.reply_text("🏢 ¿A qué empresa pertenece? Escribe el nombre para buscarla o `-` si es independiente.")
    return EMPRESA_VINCULADA

async def recibir_empresa_vinculada(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    texto = update.message.text.strip()
    if texto == "-":
        return await mostrar_confirmacion(update, context)
    try:
        empresas = odoo.buscar_empresa(texto)
    except Exception as e:
        await update.message.reply_text(f"❌ Error buscando empresas: {e}")
        return EMPRESA_VINCULADA
    if not empresas:
        teclado = [[
            InlineKeyboardButton("➕ Crearla ahora", callback_data=f"empresa_nueva|{texto}"),
            InlineKeyboardButton("⏩ Sin empresa",   callback_data="empresa_ninguna"),
        ]]
        await update.message.reply_text(
            f"No encontré ninguna empresa llamada *{texto}*.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(teclado),
        )
        return EMPRESA_VINCULADA
    botones = [
        [InlineKeyboardButton(f"🏢 {e['name']}", callback_data=f"empresa_id|{e['id']}|{e['name']}")]
        for e in empresas
    ]
    botones.append([InlineKeyboardButton("⏩ Sin empresa", callback_data="empresa_ninguna")])
    await update.message.reply_text(
        f"Encontré estas empresas para *{texto}*:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(botones),
    )
    return EMPRESA_VINCULADA

async def callback_empresa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "empresa_ninguna":
        pass
    elif data.startswith("empresa_nueva|"):
        nombre_empresa = data.split("|", 1)[1]
        try:
            emp_id = odoo.crear_empresa(nombre_empresa)
            context.user_data["empresa_id"]     = emp_id
            context.user_data["empresa_nombre"] = nombre_empresa
            await query.edit_message_text(f"✅ Empresa *{nombre_empresa}* creada.", parse_mode="Markdown")
        except Exception as e:
            await query.edit_message_text(f"❌ Error creando empresa: {e}")
            return EMPRESA_VINCULADA
    elif data.startswith("empresa_id|"):
        _, emp_id, emp_nombre = data.split("|", 2)
        context.user_data["empresa_id"]     = int(emp_id)
        context.user_data["empresa_nombre"] = emp_nombre
    teclado = [[
        InlineKeyboardButton("✅ Confirmar", callback_data="confirmar_si"),
        InlineKeyboardButton("❌ Cancelar",  callback_data="confirmar_no"),
    ]]
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=resumen_datos(context.user_data) + "\n\n¿Confirmas?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(teclado),
    )
    return CONFIRMAR

async def mostrar_confirmacion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    teclado = [[
        InlineKeyboardButton("✅ Confirmar", callback_data="confirmar_si"),
        InlineKeyboardButton("❌ Cancelar",  callback_data="confirmar_no"),
    ]]
    await update.message.reply_text(
        resumen_datos(context.user_data) + "\n\n¿Confirmas?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(teclado),
    )
    return CONFIRMAR

async def confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == "confirmar_no":
        await query.edit_message_text("❌ Operación cancelada.")
        context.user_data.clear()
        return ConversationHandler.END
    try:
        tipo = context.user_data.get("tipo")
        if tipo == "empresa":
            nombre = context.user_data["nombre_empresa"]
            emp_id = odoo.crear_empresa(nombre)
            await query.edit_message_text(
                f"✅ *Empresa creada en Odoo*\n\n🏢 {nombre}\n🆔 ID: {emp_id}",
                parse_mode="Markdown",
            )
        else:
            contacto_id = odoo.crear_contacto(context.user_data)
            nombre_completo = f"{context.user_data.get('nombre', '')} {context.user_data.get('apellido', '')}".strip()
            await query.edit_message_text(
                f"✅ *Contacto creado en Odoo*\n\n👤 {nombre_completo}\n🆔 ID: {contacto_id}",
                parse_mode="Markdown",
            )
    except Exception as e:
        logger.error(f"Error guardando en Odoo: {e}")
        await query.edit_message_text(f"❌ Error al guardar en Odoo:\n`{e}`", parse_mode="Markdown")
    context.user_data.clear()
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("❌ Operación cancelada. Usa /nuevo para empezar de nuevo.")
    return ConversationHandler.END

async def mensaje_desconocido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("No entendí ese mensaje. Usa /nuevo para añadir un contacto, o /start para ver los comandos.")

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("nuevo", nuevo)],
        states={
            TIPO_CONTACTO:      [CallbackQueryHandler(elegir_tipo, pattern="^tipo_")],
            NOMBRE_EMPRESA:     [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_nombre_empresa)],
            NOMBRE:             [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_nombre)],
            APELLIDO:           [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_apellido)],
            TELEFONO:           [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_telefono)],
            EMAIL:              [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_email)],
            EMPRESA_VINCULADA:  [
                MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_empresa_vinculada),
                CallbackQueryHandler(callback_empresa, pattern="^empresa_"),
            ],
            CONFIRMAR:          [CallbackQueryHandler(confirmar, pattern="^confirmar_")],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
        allow_reentry=True,
    )
    app.add_handler(CommandHandler("start",     start))
    app.add_handler(CommandHandler("estado",    estado))
    app.add_handler(CommandHandler("recientes", recientes))
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_desconocido))
    print("✅ Bot en marcha. Abre Telegram y escribe /start")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
