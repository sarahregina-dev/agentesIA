import random
from .base_agent import BaseAgent

class SimpleAgent(BaseAgent):
    """Agente reativo simples - apenas reage ao ambiente atual"""
    
    def agir(self):
        """Lógica do agente simples"""
        # Primeiro tenta aspirar na posição atual
        if self.aspirar():
            return
        
        # Tenta se mover para uma sujeira vizinha
        movimento = self.perceber_sujeira()
        if movimento:
            dx, dy = movimento
            if self.mover(dx, dy):
                return
            
        # Se não há sujeira, move aleatoriamente
        movimentos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(movimentos)
        
        for dx, dy in movimentos:
            if self.mover(dx, dy):
                break
    
    def get_cor(self):
        return (0, 0, 255)  # Azul
    
    def get_letra(self):
        return "S"

    def perceber_sujeira(self):
        """Percebe a sujeira na posição vizinha"""
        movimentos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in movimentos:
            if 0 <= self.x + dx < 5 and 0 <= self.y + dy < 5:
                if self.grid[self.y + dy][self.x + dx] > 0:
                    return (dx, dy)
        return None