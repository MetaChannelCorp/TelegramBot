import os
import xmlrpc.client
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ODOO_URL       = os.getenv("ODOO_URL")
ODOO_DB        = os.getenv("ODOO_DB")
ODOO_USER      = os.getenv("ODOO_USER")
ODOO_PASSWORD  = os.getenv("ODOO_PASSWORD")

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
        if uid:
            await update.message.reply_text(
                f"✅ Conexión exitosa con Odoo\n\n"
                f"🌐 URL: {ODOO_URL}\n"
                f"🗄️ Base de datos: {ODOO_DB}\n"
                f"👤 Usuario: {ODOO_USER} (UID={uid})"
            )
        else:
            await update.message.reply_text("❌ Credenciales incorrectas")
    except Exception as e:
        await update.message.reply_text(f"❌ No se pudo conectar a Odoo:\n{e}")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("hello",  hello))
app.add_handler(CommandHandler("estado", estado))
app.run_polling()
