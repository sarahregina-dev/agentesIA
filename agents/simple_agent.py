import random
from .base_agent import BaseAgent

class SimpleAgent(BaseAgent):
    """Agente reativo simples"""
    
    def agir(self):
        
        if self.aspirar():
            return
        
      
        movimento = self.perceber_sujeira()
        if movimento:
            dx, dy = movimento
            if self.mover(dx, dy):
                return
            
    
        movimentos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(movimentos)
        
        for dx, dy in movimentos:
            if self.mover(dx, dy):
                break
    
    def get_cor(self):
        return (0, 0, 255)  
    
    def get_letra(self):
        return "S"

    def perceber_sujeira(self):
      
        movimentos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in movimentos:
            if 0 <= self.x + dx < 5 and 0 <= self.y + dy < 5:
                if self.grid[self.y + dy][self.x + dx] > 0:
                    return (dx, dy)
        return None