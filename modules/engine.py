import os
from stockfish import Stockfish

class EngineManager:
    def __init__(self):
        self.engine = None
        self.stockfish_path = os.path.join(os.getcwd(), "stockfish.exe")
        self.check_binary()

    def check_binary(self):
        if not os.path.exists(self.stockfish_path):
            raise FileNotFoundError("stockfish.exe not found in root directory")

    def init_engine(self):
        try:
            if self.engine:
                del self.engine
            self.engine = Stockfish(path=self.stockfish_path)
            self.engine.set_depth(15)
            self.engine.set_skill_level(20)
            return True
        except:
            return False

    def get_best_move(self, fen, skill, depth):
        if not self.engine: return None
        self.engine.set_skill_level(skill)
        self.engine.set_depth(depth)
        self.engine.set_fen_position(fen)
        return self.engine.get_best_move()

    def get_evaluation(self, fen):
        if not self.engine: return None
        self.engine.set_fen_position(fen)
        return self.engine.get_evaluation()
    
    def restart(self):
        return self.init_engine()