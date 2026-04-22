import logging
import xmlrpc.client

logger = logging.getLogger(__name__)


class OdooClient:
    def __init__(self, url, db, user, password):
        self.url = url
        self.db = db
        self.user = user
        self.password = password
        self.uid = None
        self._models = None

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
            self.db,
            self.uid,
            self.password,
            "res.partner",
            "search",
            [[["is_company", "=", True], ["name", "ilike", nombre]]],
            {"limit": 5},
        )
        if not ids:
            return []
        return self._models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "res.partner",
            "read",
            [ids],
            {"fields": ["id", "name"]},
        )

    def crear_empresa(self, nombre):
        self._ensure_connected()
        existentes = self._models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "res.partner",
            "search",
            [[["is_company", "=", True], ["name", "=", nombre]]],
            {"limit": 1},
        )
        if existentes:
            logger.info(f"Empresa ya existente: {nombre} (ID: {existentes[0]})")
            return existentes[0]
        partner_id = self._models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "res.partner",
            "create",
            [{"name": nombre, "is_company": True}],
        )
        logger.info(f"Empresa creada: {nombre} (ID: {partner_id})")
        return partner_id

    def crear_contacto(self, datos):
        self._ensure_connected()
        nombre_completo = datos.get("nombre", "").strip()
        apellido = datos.get("apellido", "").strip()
        if apellido:
            nombre_completo = f"{nombre_completo} {apellido}"
        vals = {"name": nombre_completo, "is_company": False}
        if datos.get("telefono"):
            vals["phone"] = datos["telefono"]
        if datos.get("email"):
            vals["email"] = datos["email"]
        if datos.get("empresa_id"):
            vals["parent_id"] = datos["empresa_id"]
        partner_id = self._models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "res.partner",
            "create",
            [vals],
        )
        logger.info(f"Contacto creado: {nombre_completo} (ID: {partner_id})")
        return partner_id

    def listar_contactos_recientes(self, limite=5):
        self._ensure_connected()
        ids = self._models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "res.partner",
            "search",
            [[["is_company", "=", False]]],
            {"limit": limite, "order": "id desc"},
        )
        if not ids:
            return []
        return self._models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "res.partner",
            "read",
            [ids],
            {"fields": ["id", "name", "phone", "email", "parent_id"]},
        )
