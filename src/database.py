# database.py - Aqui se guarda todo lo de las partidas en SQLite
# Basicamente conecta con la BD y mete los resultados de cada ronda

import os
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Rutas para la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "..", "data")
DB_PATH = os.path.join(DB_DIR, "partidas.db")


class DatabaseManager:
    """Clase para manejar la base de datos de partidas."""

    # Query para crear la tabla si no existe
    _CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS partidas (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp         TEXT    NOT NULL,
            gesto_usuario     TEXT    NOT NULL,
            gesto_ia          TEXT    NOT NULL,
            resultado         TEXT    NOT NULL,
            confianza         REAL    DEFAULT 0.0,
            score_acumulado   INTEGER DEFAULT 0
        );
    """

    def __init__(self, db_path: str = DB_PATH):
        """Abre la conexion con la BD. Si no existe la crea."""
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = None
        self._connect()
        self._create_table()
        logger.info("DatabaseManager inicializado en %s", self.db_path)

    def _connect(self):
        """Se conecta a SQLite."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.execute("PRAGMA foreign_keys=ON;")
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            logger.error("Error al conectar con SQLite: %s", e)
            raise

    def _create_table(self):
        """Crea la tabla partidas si no existe todavia."""
        try:
            with self.conn:
                self.conn.execute(self._CREATE_TABLE)
        except sqlite3.Error as e:
            logger.error("Error al crear tabla: %s", e)
            raise

    def guardar_partida(self, gesto_usuario: str, gesto_ia: str,
                        resultado: str, confianza: float = 0.0,
                        score_acumulado: int = 0) -> int:
        """
        Guarda una partida en la base de datos.
        Devuelve el ID del registro que se acaba de meter.
        """
        # Comprobamos que los datos son correctos antes de meterlos
        gestos_validos = {"Stone", "Paper", "Scissor"}
        resultados_validos = {"victoria", "derrota", "empate"}

        if gesto_usuario not in gestos_validos:
            raise ValueError(
                f"gesto_usuario inválido: '{gesto_usuario}'. "
                f"Esperado: {gestos_validos}"
            )
        if gesto_ia not in gestos_validos:
            raise ValueError(
                f"gesto_ia inválido: '{gesto_ia}'. "
                f"Esperado: {gestos_validos}"
            )
        if resultado not in resultados_validos:
            raise ValueError(
                f"resultado inválido: '{resultado}'. "
                f"Esperado: {resultados_validos}"
            )
        if not 0.0 <= confianza <= 1.0:
            raise ValueError(
                f"confianza fuera de rango: {confianza}. Esperado: 0.0-1.0"
            )

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with self.conn:
                cursor = self.conn.execute(
                    """INSERT INTO partidas
                       (timestamp, gesto_usuario, gesto_ia, resultado,
                        confianza, score_acumulado)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (timestamp, gesto_usuario, gesto_ia, resultado,
                     round(confianza, 4), score_acumulado)
                )
            row_id = cursor.lastrowid
            logger.info(
                "Partida #%d guardada: %s vs %s -> %s (conf=%.2f)",
                row_id, gesto_usuario, gesto_ia, resultado, confianza
            )
            return row_id
        except sqlite3.Error as e:
            logger.error("Error al guardar partida: %s", e)
            raise

    def obtener_historial(self, limite: int = 100) -> list[dict]:
        """Devuelve las ultimas partidas (por defecto las 100 ultimas)."""
        try:
            cursor = self.conn.execute(
                "SELECT * FROM partidas ORDER BY id DESC LIMIT ?",
                (limite,)
            )
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error("Error al obtener historial: %s", e)
            return []

    def obtener_estadisticas(self) -> dict:
        """Saca las estadisticas generales: victorias, derrotas, rachas, etc."""
        stats = {
            "total_partidas": 0,
            "victorias": 0,
            "derrotas": 0,
            "empates": 0,
            "porcentaje_victorias": 0.0,
            "gesto_mas_usado": "N/A",
            "mejor_racha": 0
        }

        try:
            # Contamos cuantas de cada tipo hay
            cursor = self.conn.execute(
                """SELECT resultado, COUNT(*) as cnt
                   FROM partidas GROUP BY resultado"""
            )
            for row in cursor.fetchall():
                res = row["resultado"]
                cnt = row["cnt"]
                stats["total_partidas"] += cnt
                if res == "victoria":
                    stats["victorias"] = cnt
                elif res == "derrota":
                    stats["derrotas"] = cnt
                elif res == "empate":
                    stats["empates"] = cnt

            if stats["total_partidas"] > 0:
                stats["porcentaje_victorias"] = round(
                    (stats["victorias"] / stats["total_partidas"]) * 100, 2
                )

            # Miramos que gesto usa mas el jugador
            cursor = self.conn.execute(
                """SELECT gesto_usuario, COUNT(*) as cnt
                   FROM partidas GROUP BY gesto_usuario
                   ORDER BY cnt DESC LIMIT 1"""
            )
            row = cursor.fetchone()
            if row:
                stats["gesto_mas_usado"] = row["gesto_usuario"]

            # Calculamos la mejor racha de victorias seguidas
            cursor = self.conn.execute(
                "SELECT resultado FROM partidas ORDER BY id ASC"
            )
            racha_actual = 0
            mejor_racha = 0
            for row in cursor.fetchall():
                if row["resultado"] == "victoria":
                    racha_actual += 1
                    mejor_racha = max(mejor_racha, racha_actual)
                else:
                    racha_actual = 0
            stats["mejor_racha"] = mejor_racha

        except sqlite3.Error as e:
            logger.error("Error al calcular estadísticas: %s", e)

        return stats

    def obtener_distribucion_gestos(self) -> list[dict]:
        """Devuelve cuantas veces ha usado cada gesto el jugador."""
        try:
            cursor = self.conn.execute(
                """SELECT gesto_usuario as gesto, COUNT(*) as cantidad
                   FROM partidas GROUP BY gesto_usuario
                   ORDER BY cantidad DESC"""
            )
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error("Error al obtener distribución de gestos: %s", e)
            return []

    def obtener_resultados_por_fecha(self) -> list[dict]:
        """Agrupa los resultados por dia para poder hacer graficas temporales."""
        try:
            cursor = self.conn.execute(
                """SELECT
                       DATE(timestamp) as fecha,
                       SUM(CASE WHEN resultado='victoria' THEN 1 ELSE 0 END) as victorias,
                       SUM(CASE WHEN resultado='derrota'  THEN 1 ELSE 0 END) as derrotas,
                       SUM(CASE WHEN resultado='empate'   THEN 1 ELSE 0 END) as empates
                   FROM partidas
                   GROUP BY DATE(timestamp)
                   ORDER BY fecha ASC"""
            )
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error("Error al obtener resultados por fecha: %s", e)
            return []

    def cerrar(self):
        """Cierra la conexion con la BD."""
        if self.conn:
            try:
                self.conn.close()
                logger.info("Conexión SQLite cerrada.")
            except sqlite3.Error as e:
                logger.error("Error al cerrar conexión: %s", e)

    def __del__(self):
        self.cerrar()
