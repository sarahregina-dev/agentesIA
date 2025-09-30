import random
from .base_agent import BaseAgent

class SimpleAgent(BaseAgent):
    """Agente reativo simples - apenas reage ao ambiente atual"""
    
    def agir(self):
        """Lógica do agente simples"""
        # Primeiro tenta aspirar na posição atual
        if self.aspirar():
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
