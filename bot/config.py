import os
import logging
from dotenv import load_dotenv

load_dotenv()
# ─────────────────────────────────────────────
# TELEGRAM
# ─────────────────────────────────────────────
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_USER_IDS = [
    int(uid.strip())
    for uid in os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")
    if uid.strip()
]
# ─────────────────────────────────────────────
# ODOO
# ─────────────────────────────────────────────
ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USER = os.getenv("ODOO_USER")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")
# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
# ─────────────────────────────────────────────
# ESTADOS DE LA CONVERSACIÓN
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
    ESPERANDO_PLANTILLA,
    CONFIRMANDO_PLANTILLA,
    SELECCIONANDO_EMPRESA_PLANTILLA,
) = range(11)
