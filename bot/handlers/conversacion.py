from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import (
    ODOO_URL,
    ODOO_DB,
    ODOO_USER,
    ODOO_PASSWORD,
    TIPO_CONTACTO,
    NOMBRE_EMPRESA,
    NOMBRE,
    APELLIDO,
    TELEFONO,
    EMAIL,
    EMPRESA_VINCULADA,
    CONFIRMAR,
    ESPERANDO_PLANTILLA,
    CONFIRMANDO_PLANTILLA,
    SELECCIONANDO_EMPRESA_PLANTILLA,
)
from helpers import (
    check_allowed,
    validar_email,
    validar_telefono,
    resumen_datos,
    resumen_plantilla,
    parsear_plantilla,
    PLANTILLA_MENSAJE,
)
from odoo_client import OdooClient

odoo = OdooClient(ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD)


# ─────────────────────────────────────────────
# ENTRADA — /nuevo
# ─────────────────────────────────────────────
async def nuevo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not check_allowed(update.effective_user.id):
        return ConversationHandler.END
    context.user_data.clear()
    teclado = [
        [
            InlineKeyboardButton("👤 Contacto", callback_data="tipo_contacto"),
            InlineKeyboardButton("🏢 Empresa", callback_data="tipo_empresa"),
            InlineKeyboardButton("📋 Plantilla", callback_data="tipo_plantilla"),
        ]
    ]
    await update.message.reply_text(
        "¿Qué quieres añadir al CRM?",
        reply_markup=InlineKeyboardMarkup(teclado),
    )
    return TIPO_CONTACTO


async def elegir_tipo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    tipo = query.data.replace("tipo_", "")
    context.user_data["tipo"] = tipo
    if tipo == "plantilla":
        await query.edit_message_text(
            "📋 *Modo plantilla*\n\n"
            "¿A qué empresa pertenecen estos contactos?\n"
            "Escribe el nombre para buscarla:",
            parse_mode="Markdown",
        )
        return SELECCIONANDO_EMPRESA_PLANTILLA
    elif tipo == "empresa":
        await query.edit_message_text("🏢 ¿Cuál es el nombre de la empresa?")
        return NOMBRE_EMPRESA
    else:
        await query.edit_message_text(
            "👤 ¿Cuál es el *nombre* del contacto?", parse_mode="Markdown"
        )
        return NOMBRE


# ─────────────────────────────────────────────
# MODO PLANTILLA — selección de empresa previa
# ─────────────────────────────────────────────
async def buscar_empresa_plantilla(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    texto = update.message.text.strip()
    try:
        empresas = odoo.buscar_empresa(texto)
    except Exception as e:
        await update.message.reply_text(f"❌ Error buscando empresas: {e}")
        return SELECCIONANDO_EMPRESA_PLANTILLA
    if not empresas:
        teclado = [
            [
                InlineKeyboardButton(
                    "➕ Crear empresa", callback_data=f"emp_pre_nueva|{texto}"
                ),
                InlineKeyboardButton("🔍 Buscar otra", callback_data="emp_pre_buscar"),
            ]
        ]
        await update.message.reply_text(
            f"No encontré ninguna empresa llamada *{texto}*. ¿Qué hacemos?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(teclado),
        )
        return SELECCIONANDO_EMPRESA_PLANTILLA
    botones = [
        [
            InlineKeyboardButton(
                f"🏢 {e['name']}", callback_data=f"emp_pre|{e['id']}|{e['name']}"
            )
        ]
        for e in empresas
    ]
    await update.message.reply_text(
        f"Encontré estas empresas para *{texto}*:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(botones),
    )
    return SELECCIONANDO_EMPRESA_PLANTILLA


async def callback_seleccionar_empresa_plantilla(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "emp_pre_buscar":
        await query.edit_message_text(
            "🔍 Escribe el nombre de la empresa para buscarla:"
        )
        return SELECCIONANDO_EMPRESA_PLANTILLA
    elif data.startswith("emp_pre_nueva|"):
        nombre_empresa = data.split("|", 1)[1]
        try:
            emp_id = odoo.crear_empresa(nombre_empresa)
            context.user_data["empresa_plantilla_id"] = emp_id
            context.user_data["empresa_plantilla_nombre"] = nombre_empresa
            await query.edit_message_text(
                f"✅ Empresa *{nombre_empresa}* creada.\n\n"
                f"Ahora copia, rellena y envíame los contactos:\n\n{PLANTILLA_MENSAJE}",
                parse_mode="Markdown",
            )
            return ESPERANDO_PLANTILLA
        except Exception as e:
            await query.edit_message_text(f"❌ Error creando empresa: {e}")
            return SELECCIONANDO_EMPRESA_PLANTILLA
    elif data.startswith("emp_pre|"):
        _, emp_id, emp_nombre = data.split("|", 2)
        context.user_data["empresa_plantilla_id"] = int(emp_id)
        context.user_data["empresa_plantilla_nombre"] = emp_nombre
        await query.edit_message_text(
            f"✅ Empresa seleccionada: *{emp_nombre}*\n\n"
            f"Ahora copia, rellena y envíame los contactos:\n\n{PLANTILLA_MENSAJE}",
            parse_mode="Markdown",
        )
        return ESPERANDO_PLANTILLA


# ─────────────────────────────────────────────
# MODO PLANTILLA — recepción y confirmación
# ─────────────────────────────────────────────
async def recibir_plantilla(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contactos = parsear_plantilla(update.message.text)
    if not contactos:
        await update.message.reply_text(
            "⚠️ No pude detectar ningún contacto. Asegúrate de usar el formato correcto con NOMBRE: al menos."
        )
        return ESPERANDO_PLANTILLA
    emp_id = context.user_data.get("empresa_plantilla_id")
    emp_nombre = context.user_data.get("empresa_plantilla_nombre")
    for c in contactos:
        if emp_id:
            c["empresa_id"] = emp_id
            c["empresa_nombre"] = emp_nombre
    context.user_data["plantilla_contactos"] = contactos
    return await mostrar_resumen_plantilla(update, context)


async def mostrar_resumen_plantilla(
    update_or_query, context: ContextTypes.DEFAULT_TYPE
) -> int:
    contactos = context.user_data["plantilla_contactos"]
    emp_nombre = context.user_data.get("empresa_plantilla_nombre")
    teclado = [
        [
            InlineKeyboardButton(
                "✅ Guardar todos", callback_data="plantilla_confirmar"
            ),
            InlineKeyboardButton("❌ Cancelar", callback_data="plantilla_cancelar"),
        ]
    ]
    msg = (
        resumen_plantilla(contactos, emp_nombre)
        + "\n¿Confirmas y guardas todos en Odoo?"
    )
    if hasattr(update_or_query, "message") and update_or_query.message:
        await update_or_query.message.reply_text(
            msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(teclado)
        )
    else:
        await context.bot.send_message(
            chat_id=update_or_query.effective_chat.id,
            text=msg,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(teclado),
        )
    return CONFIRMANDO_PLANTILLA


async def confirmar_plantilla(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == "plantilla_cancelar":
        await query.edit_message_text("❌ Operación cancelada.")
        context.user_data.clear()
        return ConversationHandler.END
    contactos = context.user_data["plantilla_contactos"]
    creados, errores = [], []
    for c in contactos:
        try:
            cid = odoo.crear_contacto(c)
            nombre = f"{c.get('nombre', '')} {c.get('apellido', '')}".strip()
            creados.append(f"✅ {nombre} (ID: {cid})")
        except Exception as e:
            nombre = f"{c.get('nombre', '')} {c.get('apellido', '')}".strip()
            errores.append(f"❌ {nombre}: {e}")
    lines = [f"*Resultado — {len(creados)}/{len(contactos)} contactos guardados:*\n"]
    lines.extend(creados)
    if errores:
        lines.append("\n*Errores:*")
        lines.extend(errores)
    await query.edit_message_text("\n".join(lines), parse_mode="Markdown")
    context.user_data.clear()
    return ConversationHandler.END


# ─────────────────────────────────────────────
# MODO GUIADO — empresa
# ─────────────────────────────────────────────
async def recibir_nombre_empresa(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["nombre_empresa"] = update.message.text.strip()
    teclado = [
        [
            InlineKeyboardButton("✅ Confirmar", callback_data="confirmar_si"),
            InlineKeyboardButton("❌ Cancelar", callback_data="confirmar_no"),
        ]
    ]
    await update.message.reply_text(
        resumen_datos(context.user_data) + "\n\n¿Confirmas?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(teclado),
    )
    return CONFIRMAR


# ─────────────────────────────────────────────
# MODO GUIADO — contacto
# ─────────────────────────────────────────────
async def recibir_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["nombre"] = update.message.text.strip()
    await update.message.reply_text(
        "¿Cuál es el *apellido*? (escribe `-` para omitirlo)", parse_mode="Markdown"
    )
    return APELLIDO


async def recibir_apellido(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    texto = update.message.text.strip()
    context.user_data["apellido"] = "" if texto == "-" else texto
    await update.message.reply_text(
        "📞 ¿Cuál es el *teléfono*? (escribe `-` para omitirlo)", parse_mode="Markdown"
    )
    return TELEFONO


async def recibir_telefono(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    texto = update.message.text.strip()
    if texto != "-":
        if not validar_telefono(texto):
            await update.message.reply_text(
                "⚠️ Teléfono no válido. Inténtalo de nuevo o escribe `-`."
            )
            return TELEFONO
        context.user_data["telefono"] = texto
    await update.message.reply_text(
        "✉️ ¿Cuál es el *email*? (escribe `-` para omitirlo)", parse_mode="Markdown"
    )
    return EMAIL


async def recibir_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    texto = update.message.text.strip()
    if texto != "-":
        if not validar_email(texto):
            await update.message.reply_text(
                "⚠️ Email no válido. Inténtalo de nuevo o escribe `-`."
            )
            return EMAIL
        context.user_data["email"] = texto
    await update.message.reply_text(
        "🏢 ¿A qué empresa pertenece? Escribe el nombre para buscarla o `-` si es independiente."
    )
    return EMPRESA_VINCULADA


async def recibir_empresa_vinculada(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    texto = update.message.text.strip()
    if texto == "-":
        return await mostrar_confirmacion(update, context)
    try:
        empresas = odoo.buscar_empresa(texto)
    except Exception as e:
        await update.message.reply_text(f"❌ Error buscando empresas: {e}")
        return EMPRESA_VINCULADA
    if not empresas:
        teclado = [
            [
                InlineKeyboardButton(
                    "➕ Crearla ahora", callback_data=f"empresa_nueva|{texto}"
                ),
                InlineKeyboardButton("⏩ Sin empresa", callback_data="empresa_ninguna"),
            ]
        ]
        await update.message.reply_text(
            f"No encontré ninguna empresa llamada *{texto}*.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(teclado),
        )
        return EMPRESA_VINCULADA
    botones = [
        [
            InlineKeyboardButton(
                f"🏢 {e['name']}", callback_data=f"empresa_id|{e['id']}|{e['name']}"
            )
        ]
        for e in empresas
    ]
    botones.append(
        [InlineKeyboardButton("⏩ Sin empresa", callback_data="empresa_ninguna")]
    )
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
            context.user_data["empresa_id"] = emp_id
            context.user_data["empresa_nombre"] = nombre_empresa
            await query.edit_message_text(
                f"✅ Empresa *{nombre_empresa}* creada.", parse_mode="Markdown"
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Error creando empresa: {e}")
            return EMPRESA_VINCULADA
    elif data.startswith("empresa_id|"):
        _, emp_id, emp_nombre = data.split("|", 2)
        context.user_data["empresa_id"] = int(emp_id)
        context.user_data["empresa_nombre"] = emp_nombre
    teclado = [
        [
            InlineKeyboardButton("✅ Confirmar", callback_data="confirmar_si"),
            InlineKeyboardButton("❌ Cancelar", callback_data="confirmar_no"),
        ]
    ]
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=resumen_datos(context.user_data) + "\n\n¿Confirmas?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(teclado),
    )
    return CONFIRMAR


async def mostrar_confirmacion(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    teclado = [
        [
            InlineKeyboardButton("✅ Confirmar", callback_data="confirmar_si"),
            InlineKeyboardButton("❌ Cancelar", callback_data="confirmar_no"),
        ]
    ]
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
                f"✅ *Empresa creada en Odoo*\n\n🏢 {nombre}\n🆔 {emp_id}",
                parse_mode="Markdown",
            )
        else:
            contacto_id = odoo.crear_contacto(context.user_data)
            nombre_completo = f"{context.user_data.get('nombre', '')} {context.user_data.get('apellido', '')}".strip()
            await query.edit_message_text(
                f"✅ *Contacto creado en Odoo*\n\n👤 {nombre_completo}\n🆔 {contacto_id}",
                parse_mode="Markdown",
            )
    except Exception as e:
        await query.edit_message_text(
            f"❌ Error al guardar en Odoo:\n`{e}`", parse_mode="Markdown"
        )
    context.user_data.clear()
    return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Operación cancelada. Usa /nuevo para empezar de nuevo."
    )
    return ConversationHandler.END
