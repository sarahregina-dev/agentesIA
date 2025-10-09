import random
from collections import deque
from .base_agent import BaseAgent

class AgenteBDI(BaseAgent):
    """Agente BDI (Beliefs, Desires, Intentions) - arquitetura cognitiva
    
    - Beliefs (Crenças): O que o agente sabe sobre o ambiente
    - Desires (Desejos): As sujeiras que o agente quer limpar
    - Intentions (Intenções): O plano de ação atual para alcançar um desejo
    """
    
    def __init__(self, nome, ambiente, x, y, grid, obstacles):
        super().__init__(nome, ambiente, x, y, grid, obstacles)
        
        # BELIEFS (Crenças) - conhecimento sobre o ambiente
        self.crencas = {
            'mapa_conhecido': [[None for _ in range(5)] for _ in range(5)],  # O que observou
            'sujeiras_observadas': set(),  # Sujeiras que viu
            'casas_visitadas': set(),
            'obstaculos': set()

        }
        
        # DESIRES (Desejos) - sujeiras que quer limpar (ordenadas por prioridade)
        self.desejos = []
        
        # INTENTIONS (Intenções) - plano atual de ação
        self.intencao_atual = None  # ('limpar_sujeira', (x, y, valor)) ou ('explorar', (x, y))
        self.plano = []  # Lista de movimentos [(dx, dy), ...]
    
    def agir(self):
        """Ciclo BDI: Atualiza crenças → Gera desejos → Forma intenções → Executa"""
        
        # 1. ATUALIZA CRENÇAS (observa o ambiente)
        self.atualizar_crencas()
        
        # 2. GERA DESEJOS (baseado nas crenças)
        self.gerar_desejos()
        
        # 3. FORMA INTENÇÕES (seleciona um desejo e cria plano)
        if not self.intencao_atual or not self.plano:
            self.formar_intencao()
        
        # 4. EXECUTA INTENÇÃO (segue o plano)
        self.executar_intencao()
    
    def atualizar_crencas(self):
        """Atualiza o conhecimento sobre o ambiente (Beliefs)"""
        # Marca posição atual como visitada
        self.crencas['casas_visitadas'].add((self.x, self.y))
        
        # Observa a posição atual e células adjacentes (visão limitada)
        movimentos = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dx, dy in movimentos:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < 5 and 0 <= ny < 5:
                # Atualiza mapa conhecido
                self.crencas['mapa_conhecido'][ny][nx] = self.grid[ny][nx]
                if (nx, ny) in self.obstacles:
                    self.crencas['obstaculos'].add((nx, ny))
                
                # Se observou uma sujeira, adiciona às sujeiras conhecidas
                if self.grid[ny][nx] > 0:
                    distancia = self.distancia(self.x, self.y, nx, ny)
                    self.crencas['sujeiras_observadas'].add((nx, ny, self.grid[ny][nx] / (self.distancia(self.x, self.y, nx, ny) + 2), distancia))
        
        # Remove sujeiras que já foram limpas
        self.crencas['sujeiras_observadas'] = {
            (x, y, v, d) for (x, y, v, d) in self.crencas['sujeiras_observadas']
            if self.grid[y][x] > 0
        }
    
    def gerar_desejos(self):
        """Gera desejos baseado nas crenças (Desires = sujeiras observadas)"""
        # Os desejos são todas as sujeiras que o agente observou
        self.desejos = list(self.crencas['sujeiras_observadas'])
        
        # Ordena desejos por prioridade: valor da sujeira (maior = mais desejável)
        self.desejos.sort(key=lambda s: s[2], reverse=True)
        
    
    def formar_intencao(self):
        """Forma uma intenção (plano) para alcançar um desejo (Intentions)"""
        
        # Se há sujeira na posição atual, limpa imediatamente
        if self.grid[self.y][self.x] > 0:
            self.intencao_atual = ('limpar_aqui', (self.x, self.y, self.grid[self.y][self.x]))
            self.plano = [('aspirar', None)]
            return
        
        # Se tem desejos (sujeiras conhecidas), cria plano para a mais desejada
        if self.desejos:
            # Escolhe a sujeira mais próxima entre as mais valiosas
            sujeira_alvo = self.escolher_sujeira_alvo()
            
            if sujeira_alvo:
                x, y, valor, distancia = sujeira_alvo
                self.intencao_atual = ('limpar_sujeira', sujeira_alvo)
                self.plano = self.criar_plano(x, y)
                print(f"[BDI] 🎯 Intenção: Ir limpar sujeira em ({x}, {y}) - Valor: {valor}")
                return
        
        # Se não tem desejos, explora o ambiente
        casa_inexplorada = self.encontrar_casa_inexplorada()
        if casa_inexplorada:
            x, y = casa_inexplorada
            self.intencao_atual = ('explorar', (x, y, 0))
            self.plano = self.criar_plano(x, y)
            print(f"[BDI] 🔍 Intenção: Explorar casa ({x}, {y})")
        else:
            # Explorou tudo e não tem mais desejos
            self.parar()
    
    def escolher_sujeira_alvo(self):
        """Escolhe a melhor sujeira para limpar (mais próxima entre as valiosas)"""
        if not self.desejos:
            return None
        print(self.desejos)
        for sujeira in self.desejos:
            if self.bateria >= sujeira[3] + 3:
                return sujeira
        
        return None
        
    
    def encontrar_casa_inexplorada(self):
        """Encontra casa mais próxima não visitada"""
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
        """Cria um plano (caminho) usando BFS para evitar obstáculos"""
        inicio = (self.x, self.y)
        destino = (x_destino, y_destino)
        
        # BFS para encontrar caminho mais curto
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
            
            # Tenta todos os movimentos possíveis
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < 5 and 0 <= ny < 5 and 
                    (nx, ny) not in self.crencas['obstaculos'] and 
                    (nx, ny) not in visitados):
                    fila.append(((nx, ny), caminho + [(dx, dy)]))
        
        # Não encontrou caminho
        return []
    
    def executar_intencao(self):
        """Executa o plano da intenção atual"""
        if not self.plano:
            # Plano concluído ou vazio
            self.intencao_atual = None
            return
        
        # Pega próxima ação do plano
        acao, parametro = self.plano.pop(0)
        
        if acao == 'aspirar':
            if self.aspirar():
                print(f"[BDI] ✅ Limpou sujeira em ({self.x}, {self.y})")
            self.intencao_atual = None
            
        elif acao == 'mover':
            dx, dy = parametro
            sucesso = self.mover(dx, dy)
            
            if not sucesso:
                # Movimento falhou, recria o plano
                if self.intencao_atual:
                    tipo, (x, y, v) = self.intencao_atual
                    self.plano = self.criar_plano(x, y)
                    if tipo == 'limpar_sujeira':
                        self.plano.append(('aspirar', None))
    
    def get_cor(self):
        return (255, 0, 255)  # Magenta
    
    def get_letra(self):
        return "B"

