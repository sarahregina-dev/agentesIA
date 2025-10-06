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
        
        # Inicia o processo do agente
        self.ambiente.process(self.executar())
    
    def executar(self):
        """Processo principal do agente"""
        while self.executando and self.bateria > 0:
            # Executa a lógica específica do agente
            self.agir()
            
            # Consome bateria
            # self.bateria -= 1
            
            # Timeout para próxima ação
            yield self.ambiente.timeout(1)
    
    def parar(self):
        """Para o agente e encerra sua execução"""
        self.executando = False
        print(f"Agente {self.nome} foi parado por falta de ações")
            
    
    @abstractmethod
    def agir(self):
        """Método abstrato que cada agente deve implementar"""
        pass
    
    def mover(self, dx, dy):
        """Move o agente para uma nova posição"""
        novo_x = self.x + dx
        novo_y = self.y + dy
        
        # Verifica limites do grid
        if 0 <= novo_x < 5 and 0 <= novo_y < 5:
            # Verifica se não há obstáculo
            if (novo_x, novo_y) not in self.obstacles:
                self.x = novo_x
                self.y = novo_y
                self.historico_posicoes.append((self.x, self.y))
                self.bateria -= 1
                return True
        return False
    
    def aspirar(self, model_grid = None):
        """Aspira a sujeira na posição atual"""
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
    
    def desenhar(self, tela):
        """Desenha o agente na tela"""
        # Determina a cor do agente
        cor = self.get_cor()
        
        # Desenha o agente como um círculo
        centro_x = self.x * 80 + 40
        centro_y = self.y * 80 + 40
        pygame.draw.circle(tela, cor, (centro_x, centro_y), 15)
        
        # Desenha uma borda preta
        pygame.draw.circle(tela, (0, 0, 0), (centro_x, centro_y), 15, 2)
        
        # Desenha a letra identificadora
        fonte = pygame.font.SysFont("arial", 12, bold=True)
        texto = fonte.render(self.get_letra(), True, (255, 255, 255))
        tela.blit(texto, (centro_x - 6, centro_y - 6))
    
    @abstractmethod
    def get_cor(self):
        """Retorna a cor do agente"""
        pass
    
    @abstractmethod
    def get_letra(self):
        """Retorna a letra identificadora do agente"""
        pass
    
    def distancia(self, x1, y1, x2, y2):
        """Calcula distância absoluta (Manhattan) entre duas posições"""
        return abs(x1 - x2) + abs(y1 - y2)
    
    def encontrar_sujeira_mais_proxima(self):
        """Encontra a sujeira mais próxima"""
        sujeiras = []
        for y in range(5):
            for x in range(5):
                if self.grid[y][x] > 0:
                    distancia = self.distancia(self.x, self.y, x, y)
                    sujeiras.append((x, y, self.grid[y][x], distancia))
        
        if sujeiras:
            # Ordena por distância
            sujeiras.sort(key=lambda s: s[3])
           
            return sujeiras[0]
        return None
    
    def caminho_para_posicao(self, x_destino, y_destino):
        """Calcula um caminho simples para uma posição"""
        # Movimento simples: primeiro horizontal, depois vertical
        if self.x < x_destino:
            return (1, 0)  # Direita
        elif self.x > x_destino:
            return (-1, 0)  # Esquerda
        elif self.y < y_destino:
            return (0, 1)  # Baixo
        elif self.y > y_destino:
            return (0, -1)  # Cima
        else:
            return (0, 0)  # Já está na posição
