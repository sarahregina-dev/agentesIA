import random
from .base_agent import BaseAgent

class ModelBasedAgent(BaseAgent):
    """Agente baseado em modelo - mantém um modelo interno do ambiente"""
    
    def __init__(self, nome, ambiente, x, y, grid, obstacles):
        super().__init__(nome, ambiente, x, y, grid, obstacles)
        # Modelo interno do ambiente
        self.modelo_grid = [[0 for _ in range(5)] for _ in range(5)]
        self.modelo_obstacles = obstacles.copy()
        self.ultima_acao = None
    
    def agir(self):
        """Lógica do agente baseado em modelo"""
        # Atualiza modelo com informações da posição atual
        self.atualizar_modelo()
        
        # Primeiro tenta aspirar na posição atual
        if self.aspirar():
            self.ultima_acao = "aspirar"
            return
        
        # Procura sujeira no modelo
        sujeira_proxima = self.encontrar_sujeira_mais_proxima()
        if sujeira_proxima:
            x_dest, y_dest, _, _ = sujeira_proxima
            dx, dy = self.caminho_para_posicao(x_dest, y_dest)
            if self.mover(dx, dy):
                self.ultima_acao = "mover"
                return
        
        # Se não encontrou sujeira, explora aleatoriamente
        movimentos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(movimentos)
        
        for dx, dy in movimentos:
            if self.mover(dx, dy):
                self.ultima_acao = "explorar"
                break
    
    def atualizar_modelo(self):
        """Atualiza o modelo interno com informações atuais"""
        # Atualiza a posição atual no modelo
        self.modelo_grid[self.y][self.x] = self.grid[self.y][self.x]
        
        # Observa células adjacentes
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                novo_x = self.x + dx
                novo_y = self.y + dy
                if 0 <= novo_x < 5 and 0 <= novo_y < 5:
                    self.modelo_grid[novo_y][novo_x] = self.grid[novo_y][novo_x]
    
    def get_cor(self):
        return (0, 255, 0)  # Verde
    
    def get_letra(self):
        return "M"
