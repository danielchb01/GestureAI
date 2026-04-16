import random


class GameEngine:
    def __init__(self):
        self.moves = ["Paper", "Stone", "Scissor"]
        self.rules = {
            "Stone": "Scissor",
            "Paper": "Stone",
            "Scissor": "Paper"
        }

    def get_ia_move(self):
        return random.choice(self.moves)

    def check_winner(self, user_move, ia_move):
        """Devuelve: 1 (Gana usuario), -1 (Gana IA), 0 (Empate)"""
        if user_move == ia_move:
            return 0
        if self.rules[user_move] == ia_move:
            return 1
        return -1
