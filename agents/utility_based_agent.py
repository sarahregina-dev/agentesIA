import random
from .base_agent import BaseAgent

class UtilityBasedAgent(BaseAgent):
    """Agente baseado em utilidade - avalia diferentes ações e escolhe a de maior utilidade"""
    
    def __init__(self, nome, ambiente, x, y, grid, obstacles):
        super().__init__(nome, ambiente, x, y, grid, obstacles)
        # Modelo interno do ambiente
        self.modelo_grid = [[0 for _ in range(5)] for _ in range(5)]
        self.modelo_obstacles = []
        self.obstacles = obstacles
       
       
        self.casas_visitadas = set()
        self.casas_visitadas.add((x, y))  
    
    def agir(self):
       
       
        self.atualizar_modelo()
  
       
        self.casas_visitadas.add((self.x, self.y))
        
       
        if self.aspirar():
          
            return
        
       
        sujeira_proxima = self.encontrar_sujeira_mais_proxima()
        if sujeira_proxima:
            x_dest, y_dest, _, _ = sujeira_proxima
            dx, dy = self.caminho_para_posicao(x_dest, y_dest)
            
            if self.mover(dx, dy):
               
                return
        
       
        casa_nao_visitada = self.encontrar_casa_nao_visitada()
        if casa_nao_visitada:
            x_dest, y_dest = casa_nao_visitada
            dx, dy = self.caminho_para_posicao(x_dest, y_dest)
            if self.mover(dx, dy):
              
                return

        self.parar()
    

    def mover(self, dx, dy):
       
        from collections import deque

        destino_x = self.x + dx
        destino_y = self.y + dy

       
        if not (0 <= destino_x < 5 and 0 <= destino_y < 5):
            return False
        if (destino_x, destino_y) in self.modelo_obstacles:

            visitados = set()
            fila = deque()
            fila.append((self.x, self.y, []))  

            while fila:
                x_atual, y_atual, caminho = fila.popleft()
                if (x_atual, y_atual) == (destino_x, destino_y):
                  
                    if caminho:
                        proximo = caminho[0]
                        return super().mover(proximo[0] - self.x, proximo[1] - self.y)
                    else:
                        return False 
                for dx_, dy_ in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x_atual + dx_, y_atual + dy_
                    if (0 <= nx < 5 and 0 <= ny < 5 and
                        (nx, ny) not in self.modelo_obstacles and
                        (nx, ny) not in visitados):
                        visitados.add((nx, ny))
                        fila.append((nx, ny, caminho + [(nx, ny)]))
            return False  
        else:
            
            return super().mover(dx, dy)
    
    def atualizar_modelo(self):
     
        self.modelo_grid[self.y][self.x] = self.grid[self.y][self.x]
        
        movimentos_vizinhos = [(0, 1), (0, -1), (1, 0), (-1, 0)]  
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
        
                    sujeiras.append((x, y, self.modelo_grid[y][x]/( distancia + 2), distancia))

        if sujeiras:
                sujeiras.sort(key=lambda s: s[2], reverse=True) #maior utilidade primeiro
                for index, sujeira in enumerate(sujeiras):
                    if self.bateria >= sujeiras[index][3] + 2:
                        print("sujeira mais proxima", sujeiras[index], "posicao", self.x, self.y)
                        return sujeiras[index]
        return None
    
    def encontrar_casa_nao_visitada(self):
     
        casas_nao_visitadas = []
        
      
        for y in range(5):
            for x in range(5):
             
                if (x, y) not in self.casas_visitadas and (x, y) not in self.modelo_obstacles:
                   
                    distancia = self.distancia(self.x, self.y, x, y)
                    casas_nao_visitadas.append((x, y, distancia))
        
        if casas_nao_visitadas:
            casas_nao_visitadas.sort(key=lambda casa: casa[2], reverse=False) 
           
            if self.bateria >= (casas_nao_visitadas[0][2] + 3):
               
                return (casas_nao_visitadas[0][0], casas_nao_visitadas[0][1])
        
        return None
    
    
    
    def get_cor(self):
        return (128, 0, 128)  # Roxo
    
    def get_letra(self):
        return "U"
