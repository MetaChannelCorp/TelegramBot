from telegram import Update
from telegram.ext import ContextTypes
from config import ODOO_URL, ODOO_DB, ODOO_USER
from helpers import check_allowed
from odoo_client import OdooClient

odoo = OdooClient(ODOO_URL, ODOO_DB, ODOO_USER, __import__("config").ODOO_PASSWORD)


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
            f"👤 Usuario: {ODOO_USER}\n"
            f"🗄️ Base de datos: {ODOO_DB}",
            parse_mode="Markdown",
        )
    else:
        await msg.edit_text("❌ No se pudo conectar a Odoo.")

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

async def mensaje_desconocido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "No entendí ese mensaje. Usa /nuevo para añadir un contacto, o /start para ver los comandos."
    )
