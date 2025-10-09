import random
from collections import deque
from .base_agent import BaseAgent

class AgenteBDI(BaseAgent):
   
    
    def __init__(self, nome, ambiente, x, y, grid, obstacles):
        super().__init__(nome, ambiente, x, y, grid, obstacles)
        

        self.crencas = {
            'mapa_conhecido': [[None for _ in range(5)] for _ in range(5)],  
            'sujeiras_observadas': set(),  
            'casas_visitadas': set(),
            'obstaculos': set()

        }
        
       
        self.desejos = []
        
       
        self.intencao_atual = None 
        self.plano = []  
    
    def agir(self):
        
        self.atualizar_crencas()
        
        
        self.gerar_desejos()
        
        
        if not self.intencao_atual or not self.plano:
            self.formar_intencao()
        
        
        self.executar_intencao()
    
    def atualizar_crencas(self):
       
       
        self.crencas['casas_visitadas'].add((self.x, self.y))
        
        
        movimentos = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dx, dy in movimentos:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < 5 and 0 <= ny < 5:
                
                self.crencas['mapa_conhecido'][ny][nx] = self.grid[ny][nx]
                if (nx, ny) in self.obstacles:
                    self.crencas['obstaculos'].add((nx, ny))
                
               
                if self.grid[ny][nx] > 0:
                    distancia = self.distancia(self.x, self.y, nx, ny)
                    self.crencas['sujeiras_observadas'].add((nx, ny, self.grid[ny][nx] / (self.distancia(self.x, self.y, nx, ny) + 2), distancia))
        
       
        self.crencas['sujeiras_observadas'] = {
            (x, y, v, d) for (x, y, v, d) in self.crencas['sujeiras_observadas']
            if self.grid[y][x] > 0
        }
    
    def gerar_desejos(self):
       
       
        self.desejos = list(self.crencas['sujeiras_observadas'])
        
       
        self.desejos.sort(key=lambda s: s[2], reverse=True)
        
    
    def formar_intencao(self):

        if self.grid[self.y][self.x] > 0:
            self.intencao_atual = ('limpar_aqui', (self.x, self.y, self.grid[self.y][self.x]))
            self.plano = [('aspirar', None)]
            return
        
       
        if self.desejos:
           
            sujeira_alvo = self.escolher_sujeira_alvo()
            
            if sujeira_alvo:
                x, y, valor, distancia = sujeira_alvo
                self.intencao_atual = ('limpar_sujeira', sujeira_alvo)
                self.plano = self.criar_plano(x, y)
                print(f"[BDI]  Intenção: Ir limpar sujeira em ({x}, {y}) - Valor: {valor}")
                return
        
       
        casa_inexplorada = self.encontrar_casa_inexplorada()
        if casa_inexplorada:
            x, y = casa_inexplorada
            self.intencao_atual = ('explorar', (x, y, 0))
            self.plano = self.criar_plano(x, y)
            print(f"[BDI]  Intenção: Explorar casa ({x}, {y})")
        else:
           
            self.parar()
    
    def escolher_sujeira_alvo(self):
       
        if not self.desejos:
            return None
        print(self.desejos)
        for sujeira in self.desejos:
            if self.bateria >= (sujeira[3] + 3):
                return sujeira
        
        return None
        
    
    def encontrar_casa_inexplorada(self):
       
        casas = []
        
        for y in range(5):
            for x in range(5):
                if ((x, y) not in self.crencas['casas_visitadas'] and 
                    (x, y) not in self.crencas['obstaculos']):
                    dist = self.distancia(self.x, self.y, x, y)
                    casas.append((x, y, dist))
        
        if casas:
            casas.sort(key=lambda c: c[2] , reverse=False)
            if self.bateria >= casas[0][2] + 3:
                return (casas[0][0], casas[0][1])
        
        return None
    
    def criar_plano(self, x_destino, y_destino):
       
        inicio = (self.x, self.y)
        destino = (x_destino, y_destino)
        
       
        visitados = set()
        fila = deque()
        fila.append((inicio, []))
        
        while fila:
            (x, y), caminho = fila.popleft()
            
            if (x, y) == destino:
                return [('mover', direcao) for direcao in caminho]
            
            if (x, y) in visitados:
                continue
            
            visitados.add((x, y))
            
           
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < 5 and 0 <= ny < 5 and 
                    (nx, ny) not in self.crencas['obstaculos'] and 
                    (nx, ny) not in visitados):
                    fila.append(((nx, ny), caminho + [(dx, dy)]))
        
       
        return []
    
    def executar_intencao(self):

        if not self.plano:
           
            self.intencao_atual = None
            return
        
       
        acao, parametro = self.plano.pop(0)
        
        if acao == 'aspirar':
            if self.aspirar():
                print(f"[BDI]  Limpou sujeira em ({self.x}, {self.y})")
            self.intencao_atual = None
            
        elif acao == 'mover':
            dx, dy = parametro
            sucesso = self.mover(dx, dy)
            
            if not sucesso:
               
                if self.intencao_atual:
                    tipo, (x, y, v) = self.intencao_atual
                    self.plano = self.criar_plano(x, y)
                    if tipo == 'limpar_sujeira':
                        self.plano.append(('aspirar', None))
    
    def get_cor(self):
        return (255, 0, 255)  
    
    def get_letra(self):
        return "B"

