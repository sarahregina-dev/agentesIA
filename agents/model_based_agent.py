import random
from .base_agent import BaseAgent

class ModelBasedAgent(BaseAgent):
    """Agente baseado em modelo - mantém um modelo interno do ambiente"""
    
    def __init__(self, nome, ambiente, x, y, grid, obstacles):
        super().__init__(nome, ambiente, x, y, grid, obstacles)
      
        self.modelo_grid = [[0 for _ in range(5)] for _ in range(5)]
        self.modelo_obstacles = []
       
        self.ultima_acao = None
      
        self.casas_visitadas = set()
        self.casas_visitadas.add((x, y))  
    
    def agir(self):
       
        self.atualizar_modelo()
        
      
        self.casas_visitadas.add((self.x, self.y))
        
      
        if self.aspirar():
            self.ultima_acao = "aspirar"
            return
        
       
        sujeira_proxima = self.encontrar_sujeira_mais_proxima()
        if sujeira_proxima:
            x_dest, y_dest, _, _ = sujeira_proxima
            dx, dy = self.caminho_para_posicao(x_dest, y_dest)
            if self.mover(dx, dy):
                self.ultima_acao = "mover_para_sujeira"
                return
        
      
        casa_nao_visitada = self.encontrar_casa_nao_visitada()
        if casa_nao_visitada:
            x_dest, y_dest = casa_nao_visitada
            dx, dy = self.caminho_para_posicao(x_dest, y_dest)
            if self.mover(dx, dy):
                self.ultima_acao = "explorar_nao_visitada"
                return
        
       
        movimentos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        dx, dy = random.choice(movimentos)
        
        if self.mover(dx, dy):
            self.ultima_acao = "explorar_aleatorio"
            return
    
    def atualizar_modelo(self):
        """Atualiza o modelo interno com informações atuais"""
        # Atualiza a posição atual no modelo
        self.modelo_grid[self.y][self.x] = self.grid[self.y][self.x]
        
        # Observa apenas as 4 casas imediatamente próximas (norte, sul, leste, oeste)
        movimentos_vizinhos = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # norte, sul, leste, oeste
        for dx, dy in movimentos_vizinhos:
            novo_x = self.x + dx
            novo_y = self.y + dy
            if (novo_x, novo_y) in self.obstacles:
                self.modelo_obstacles.append((novo_x, novo_y))
            if 0 <= novo_x < 5 and 0 <= novo_y < 5:
                self.modelo_grid[novo_y][novo_x] = self.grid[novo_y][novo_x]
    
    def encontrar_sujeira_mais_proxima(self):
    
        sujeiras = []
        for y in range(5):
            for x in range(5):
                if self.modelo_grid[y][x] > 0:
                    distancia = self.distancia(self.x, self.y, x, y)
                    sujeiras.append((x, y, self.modelo_grid[y][x], distancia))
        if sujeiras:
            sujeiras.sort(key=lambda s: s[3])
            print(sujeiras[0])
            return sujeiras[0]
        return None
    
    def encontrar_casa_nao_visitada(self):
      
        casas_nao_visitadas = []
        
       
        for y in range(5):
            for x in range(5):
                if (x, y) not in self.casas_visitadas and (x, y) not in self.modelo_obstacles:
                    distancia = self.distancia(self.x, self.y, x, y)
                    casas_nao_visitadas.append((x, y, distancia))
        
        if casas_nao_visitadas:
           
            casas_nao_visitadas.sort(key=lambda casa: casa[2])
            return (casas_nao_visitadas[0][0], casas_nao_visitadas[0][1])
        
        return None
    
    def get_cor(self):
        return (0, 255, 0)  
    
    def get_letra(self):
        return "M"
