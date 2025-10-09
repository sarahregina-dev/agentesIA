import pygame
import random
import math
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Classe base para todos os agentes"""
    
    def __init__(self, nome, ambiente, x, y, grid, obstacles):
        self.nome = nome
        self.ambiente = ambiente
        self.x = x
        self.y = y
        self.grid = grid
        self.obstacles = obstacles
        self.bateria = 30
        self.pontuacao = 0
        self.executando = True
        self.historico_posicoes = [(x, y)]
        
     
        self.ambiente.process(self.executar())
    
    def executar(self):
     
        while self.executando and self.bateria > 0:
        
            self.agir()
         
            yield self.ambiente.timeout(1)
    
    def parar(self):
       
        self.executando = False
        print(f"Agente {self.nome} foi parado por falta de ações")
            
    
    @abstractmethod
    def agir(self):
   
        pass
    
    def mover(self, dx, dy):
      
        novo_x = self.x + dx
        novo_y = self.y + dy
        
      
        if 0 <= novo_x < 5 and 0 <= novo_y < 5:
         
            if (novo_x, novo_y) not in self.obstacles:
                self.x = novo_x
                self.y = novo_y
                self.historico_posicoes.append((self.x, self.y))
                self.bateria -= 1
                return True
        return False
    
    def aspirar(self, model_grid = None):
      
        if self.grid[self.y][self.x] > 0:
            if self.bateria > 2:
                valor_sujeira = self.grid[self.y][self.x]
                self.pontuacao += valor_sujeira
                self.grid[self.y][self.x] = 0
                self.bateria -= 2
                return True
            else:
                self.parar()
        return False
    
    def desenhar(self, tela, margem=0):
      
        import constantes
        
   
        cor = self.get_cor()
        
    
        cell_size = constantes.CELL_SIZE
        raio_agente = int(cell_size * 0.20)
        tamanho_fonte = int(cell_size * 0.20)
        
    
        centro_x = margem + self.x * cell_size + cell_size // 2
        centro_y = margem + self.y * cell_size + cell_size // 2
        
    
        pygame.draw.circle(tela, (100, 100, 100), (centro_x + 2, centro_y + 2), raio_agente)
        
     
        pygame.draw.circle(tela, cor, (centro_x, centro_y), raio_agente)
        
    
        pygame.draw.circle(tela, (230, 230, 230), (centro_x, centro_y), raio_agente, 3)
        
     
        fonte = pygame.font.SysFont("arial", tamanho_fonte, bold=True)
        texto = fonte.render(self.get_letra(), True, (255, 255, 255))
        tela.blit(texto, (centro_x - texto.get_width() // 2, centro_y - texto.get_height() // 2))
    
    @abstractmethod
    def get_cor(self):
        
        pass
    
    @abstractmethod
    def get_letra(self):
        pass
    
    def distancia(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    
    def encontrar_sujeira_mais_proxima(self):
        sujeiras = []
        for y in range(5):
            for x in range(5):
                if self.grid[y][x] > 0:
                    distancia = self.distancia(self.x, self.y, x, y)
                    sujeiras.append((x, y, self.grid[y][x], distancia))
        
        if sujeiras:
            sujeiras.sort(key=lambda s: s[3])
           
            return sujeiras[0]
        return None
    
    def caminho_para_posicao(self, x_destino, y_destino):
     
        if self.x < x_destino:
            return (1, 0) 
        elif self.x > x_destino:
            return (-1, 0) 
        elif self.y < y_destino:
            return (0, 1)
        elif self.y > y_destino:
            return (0, -1) 
        else:
            return (0, 0)  
