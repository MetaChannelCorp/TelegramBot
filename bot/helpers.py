import re
from config import ALLOWED_USER_IDS

# ─────────────────────────────────────────────
# PLANTILLA
# ─────────────────────────────────────────────
PLANTILLA_MENSAJE = (
    "```\n"
    "CONTACTO 1\n"
    "NOMBRE: \n"
    "APELLIDO: \n"
    "TELÉFONO: \n"
    "EMAIL: \n\n"
    "CONTACTO 2\n"
    "NOMBRE: \n"
    "APELLIDO: \n"
    "TELÉFONO: \n"
    "EMAIL: \n"
    "```\n\n"
    "Deja en blanco o pon `-` los campos que no tengas."
)


# ─────────────────────────────────────────────
# ACCESO
# ─────────────────────────────────────────────
def check_allowed(user_id):
    if not ALLOWED_USER_IDS:
        return True
    return user_id in ALLOWED_USER_IDS


# ─────────────────────────────────────────────
# VALIDACIONES
# ─────────────────────────────────────────────
def validar_email(email):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


def validar_telefono(telefono):
    return bool(re.match(r"^[\d\s\+\-\(\)]{6,20}$", telefono))


# ─────────────────────────────────────────────
# RESÚMENES
# ─────────────────────────────────────────────
def resumen_datos(ctx_data):
    tipo = ctx_data.get("tipo", "contacto")
    lineas = ["📋 *Resumen:*\n"]
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


def resumen_plantilla(contactos, empresa_nombre=None):
    lines = [f"📋 *{len(contactos)} contacto(s) detectado(s):*"]
    if empresa_nombre:
        lines.append(f"🏢 Empresa: *{empresa_nombre}*")
    lines.append("")
    for i, c in enumerate(contactos, 1):
        nombre = f"{c.get('nombre', '—')} {c.get('apellido', '')}".strip()
        lines.append(f"*{i}. {nombre}*")
        if c.get("telefono"):
            lines.append(f"   📞 {c['telefono']}")
        if c.get("email"):
            lines.append(f"   ✉️ {c['email']}")
        lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────
# PARSER DE PLANTILLA
# ─────────────────────────────────────────────
def parsear_plantilla(texto):
    bloques = re.split(
        r"(?:CONTACTO\s*\d+\s*[\n:]?|(?:\n\s*){2,})",
        texto.strip(),
        flags=re.IGNORECASE,
    )
    bloques = [b.strip() for b in bloques if b.strip()]
    contactos = []
    for bloque in bloques:
        datos = {}
        for linea in bloque.splitlines():
            linea = linea.strip()
            if not linea or ":" not in linea:
                continue
            clave, _, valor = linea.partition(":")
            clave = clave.strip().upper()
            valor = valor.strip()
            if not valor or valor in ("-", "—"):
                continue
            if clave in ("NOMBRE", "NAME"):
                datos["nombre"] = valor
            elif clave in ("APELLIDO", "APELLIDOS", "SURNAME"):
                datos["apellido"] = valor
            elif clave in ("TELÉFONO", "TELEFONO", "PHONE", "TLF"):
                datos["telefono"] = valor
            elif clave in ("EMAIL", "CORREO", "MAIL"):
                datos["email"] = valor
        if datos.get("nombre"):
            contactos.append(datos)
    return contactos
