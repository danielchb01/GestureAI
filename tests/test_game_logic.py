# test_game_logic.py - Tests del motor de juego
# Probamos las 9 combinaciones de piedra papel tijera y que la IA funciona

import os
import sys
import unittest

# Para importar desde src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from game_logic import GameEngine


class TestGameEngineInit(unittest.TestCase):
    """Comprobamos que el motor arranca bien."""

    def setUp(self):
        self.engine = GameEngine()

    def test_moves_list(self):
        """Los movimientos tienen que ser Paper, Stone y Scissor."""
        self.assertEqual(set(self.engine.moves), {"Paper", "Stone", "Scissor"})

    def test_rules_dict(self):
        """Las reglas tienen que estar bien puestas."""
        self.assertEqual(self.engine.rules["Stone"], "Scissor")
        self.assertEqual(self.engine.rules["Paper"], "Stone")
        self.assertEqual(self.engine.rules["Scissor"], "Paper")


class TestCheckWinner(unittest.TestCase):
    """Probamos las 9 combinaciones posibles."""

    def setUp(self):
        self.engine = GameEngine()

    # Empates
    def test_empate_stone_stone(self):
        self.assertEqual(self.engine.check_winner("Stone", "Stone"), 0)

    def test_empate_paper_paper(self):
        self.assertEqual(self.engine.check_winner("Paper", "Paper"), 0)

    def test_empate_scissor_scissor(self):
        self.assertEqual(self.engine.check_winner("Scissor", "Scissor"), 0)

    # Cuando gana el jugador
    def test_victoria_stone_vs_scissor(self):
        """Piedra le gana a tijera."""
        self.assertEqual(self.engine.check_winner("Stone", "Scissor"), 1)

    def test_victoria_paper_vs_stone(self):
        """Papel le gana a piedra."""
        self.assertEqual(self.engine.check_winner("Paper", "Stone"), 1)

    def test_victoria_scissor_vs_paper(self):
        """Tijera le gana a papel."""
        self.assertEqual(self.engine.check_winner("Scissor", "Paper"), 1)

    # Cuando pierde el jugador
    def test_derrota_stone_vs_paper(self):
        """Piedra pierde contra papel."""
        self.assertEqual(self.engine.check_winner("Stone", "Paper"), -1)

    def test_derrota_paper_vs_scissor(self):
        """Papel pierde contra tijera."""
        self.assertEqual(self.engine.check_winner("Paper", "Scissor"), -1)

    def test_derrota_scissor_vs_stone(self):
        """Tijera pierde contra piedra."""
        self.assertEqual(self.engine.check_winner("Scissor", "Stone"), -1)


class TestIAMove(unittest.TestCase):
    """Comprobamos que la IA elige bien."""

    def setUp(self):
        self.engine = GameEngine()

    def test_ia_move_valido(self):
        """La IA siempre tiene que sacar un gesto valido."""
        for _ in range(50):
            move = self.engine.get_ia_move()
            self.assertIn(move, ["Paper", "Stone", "Scissor"])

    def test_ia_move_variabilidad(self):
        """La IA no puede sacar siempre lo mismo."""
        moves = set()
        for _ in range(100):
            moves.add(self.engine.get_ia_move())
        # En 100 intentos tiene que haber sacado los 3
        self.assertEqual(len(moves), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
