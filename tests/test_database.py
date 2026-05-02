"""
test_database.py — Tests unitarios para el módulo de persistencia SQLite.

Descripción:
    Verifica que la base de datos se crea correctamente, que los
    registros se insertan y leen sin errores, que las validaciones
    funcionan, y que las estadísticas se calculan bien.
"""

import os
import sys
import unittest
import tempfile

# Añadir src al path para poder importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from database import DatabaseManager


class TestDatabaseCreation(unittest.TestCase):
    """Tests de creación e inicialización de la base de datos."""

    def setUp(self):
        """Crea una BD temporal para cada test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_partidas.db")
        self.db = DatabaseManager(db_path=self.db_path)

    def tearDown(self):
        """Cierra la conexión y limpia ficheros temporales."""
        self.db.cerrar()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_db_file_created(self):
        """Verifica que el fichero .db se crea en disco."""
        self.assertTrue(os.path.exists(self.db_path))

    def test_table_exists(self):
        """Verifica que la tabla 'partidas' existe."""
        cursor = self.db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='partidas'"
        )
        result = cursor.fetchone()
        self.assertIsNotNone(result)

    def test_table_columns(self):
        """Verifica que la tabla tiene las columnas esperadas."""
        cursor = self.db.conn.execute("PRAGMA table_info(partidas)")
        columns = [row[1] for row in cursor.fetchall()]
        expected = ["id", "timestamp", "gesto_usuario", "gesto_ia",
                    "resultado", "confianza", "score_acumulado"]
        self.assertEqual(columns, expected)


class TestGuardarPartida(unittest.TestCase):
    """Tests de inserción de partidas."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_partidas.db")
        self.db = DatabaseManager(db_path=self.db_path)

    def tearDown(self):
        self.db.cerrar()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_insertar_victoria(self):
        """Inserta una victoria y verifica que se guardó."""
        row_id = self.db.guardar_partida(
            gesto_usuario="Stone",
            gesto_ia="Scissor",
            resultado="victoria",
            confianza=0.95,
            score_acumulado=1
        )
        self.assertEqual(row_id, 1)

    def test_insertar_derrota(self):
        """Inserta una derrota y verifica."""
        row_id = self.db.guardar_partida(
            gesto_usuario="Paper",
            gesto_ia="Scissor",
            resultado="derrota",
            confianza=0.87,
            score_acumulado=-1
        )
        self.assertEqual(row_id, 1)

    def test_insertar_empate(self):
        """Inserta un empate y verifica."""
        row_id = self.db.guardar_partida(
            gesto_usuario="Paper",
            gesto_ia="Paper",
            resultado="empate",
            confianza=0.92,
            score_acumulado=0
        )
        self.assertEqual(row_id, 1)

    def test_insertar_multiples(self):
        """Inserta varias partidas y verifica los IDs secuenciales."""
        for i in range(5):
            row_id = self.db.guardar_partida(
                gesto_usuario="Stone",
                gesto_ia="Paper",
                resultado="derrota",
                confianza=0.80,
                score_acumulado=-i
            )
            self.assertEqual(row_id, i + 1)

    def test_confianza_redondeada(self):
        """Verifica que la confianza se redondea a 4 decimales."""
        self.db.guardar_partida(
            gesto_usuario="Stone",
            gesto_ia="Scissor",
            resultado="victoria",
            confianza=0.123456789
        )
        historial = self.db.obtener_historial()
        self.assertAlmostEqual(historial[0]["confianza"], 0.1235, places=4)


class TestValidaciones(unittest.TestCase):
    """Tests de validación de parámetros."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_partidas.db")
        self.db = DatabaseManager(db_path=self.db_path)

    def tearDown(self):
        self.db.cerrar()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_gesto_usuario_invalido(self):
        """Rechaza un gesto de usuario no válido."""
        with self.assertRaises(ValueError):
            self.db.guardar_partida(
                gesto_usuario="Lizard",
                gesto_ia="Stone",
                resultado="victoria"
            )

    def test_gesto_ia_invalido(self):
        """Rechaza un gesto de IA no válido."""
        with self.assertRaises(ValueError):
            self.db.guardar_partida(
                gesto_usuario="Stone",
                gesto_ia="Spock",
                resultado="victoria"
            )

    def test_resultado_invalido(self):
        """Rechaza un resultado no válido."""
        with self.assertRaises(ValueError):
            self.db.guardar_partida(
                gesto_usuario="Stone",
                gesto_ia="Paper",
                resultado="tablas"
            )

    def test_confianza_negativa(self):
        """Rechaza confianza negativa."""
        with self.assertRaises(ValueError):
            self.db.guardar_partida(
                gesto_usuario="Stone",
                gesto_ia="Paper",
                resultado="derrota",
                confianza=-0.5
            )

    def test_confianza_mayor_que_uno(self):
        """Rechaza confianza mayor que 1."""
        with self.assertRaises(ValueError):
            self.db.guardar_partida(
                gesto_usuario="Stone",
                gesto_ia="Paper",
                resultado="derrota",
                confianza=1.5
            )


class TestObtenerHistorial(unittest.TestCase):
    """Tests de lectura del historial."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_partidas.db")
        self.db = DatabaseManager(db_path=self.db_path)
        # Insertar datos de prueba
        self.db.guardar_partida("Stone", "Scissor", "victoria", 0.95, 1)
        self.db.guardar_partida("Paper", "Scissor", "derrota", 0.88, 0)
        self.db.guardar_partida("Paper", "Paper", "empate", 0.91, 0)

    def tearDown(self):
        self.db.cerrar()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_historial_devuelve_lista(self):
        """El historial devuelve una lista."""
        historial = self.db.obtener_historial()
        self.assertIsInstance(historial, list)

    def test_historial_cantidad(self):
        """El historial contiene 3 registros."""
        historial = self.db.obtener_historial()
        self.assertEqual(len(historial), 3)

    def test_historial_ordenado_desc(self):
        """El historial viene ordenado de más reciente a más antiguo."""
        historial = self.db.obtener_historial()
        self.assertEqual(historial[0]["id"], 3)
        self.assertEqual(historial[2]["id"], 1)

    def test_historial_con_limite(self):
        """El límite restringe el número de resultados."""
        historial = self.db.obtener_historial(limite=2)
        self.assertEqual(len(historial), 2)

    def test_historial_contiene_campos(self):
        """Cada registro tiene todos los campos esperados."""
        historial = self.db.obtener_historial()
        campos = {"id", "timestamp", "gesto_usuario", "gesto_ia",
                  "resultado", "confianza", "score_acumulado"}
        self.assertEqual(set(historial[0].keys()), campos)


class TestEstadisticas(unittest.TestCase):
    """Tests de cálculo de estadísticas."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_partidas.db")
        self.db = DatabaseManager(db_path=self.db_path)
        # 3 victorias, 1 derrota, 1 empate
        self.db.guardar_partida("Stone", "Scissor", "victoria", 0.95, 1)
        self.db.guardar_partida("Paper", "Stone", "victoria", 0.88, 2)
        self.db.guardar_partida("Scissor", "Paper", "victoria", 0.91, 3)
        self.db.guardar_partida("Stone", "Paper", "derrota", 0.80, 2)
        self.db.guardar_partida("Paper", "Paper", "empate", 0.92, 2)

    def tearDown(self):
        self.db.cerrar()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_total_partidas(self):
        stats = self.db.obtener_estadisticas()
        self.assertEqual(stats["total_partidas"], 5)

    def test_victorias(self):
        stats = self.db.obtener_estadisticas()
        self.assertEqual(stats["victorias"], 3)

    def test_derrotas(self):
        stats = self.db.obtener_estadisticas()
        self.assertEqual(stats["derrotas"], 1)

    def test_empates(self):
        stats = self.db.obtener_estadisticas()
        self.assertEqual(stats["empates"], 1)

    def test_porcentaje_victorias(self):
        stats = self.db.obtener_estadisticas()
        self.assertEqual(stats["porcentaje_victorias"], 60.0)

    def test_mejor_racha(self):
        """La mejor racha es 3 (las primeras 3 victorias seguidas)."""
        stats = self.db.obtener_estadisticas()
        self.assertEqual(stats["mejor_racha"], 3)

    def test_estadisticas_sin_datos(self):
        """Estadísticas con BD vacía devuelven valores por defecto."""
        db_vacia_path = os.path.join(self.temp_dir, "vacia.db")
        db_vacia = DatabaseManager(db_path=db_vacia_path)
        stats = db_vacia.obtener_estadisticas()
        self.assertEqual(stats["total_partidas"], 0)
        self.assertEqual(stats["porcentaje_victorias"], 0.0)
        db_vacia.cerrar()
        os.remove(db_vacia_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
