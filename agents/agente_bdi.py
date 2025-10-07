import random
from .base_agent import BaseAgent

class AgenteBDI(BaseAgent):
    """Agente BDI (Beliefs, Desires, Intentions) - arquitetura cognitiva"""
    
    def __init__(self, nome, ambiente, x, y, grid, obstacles):
        super().__init__(nome, ambiente, x, y, grid, obstacles)
        # Crenças (Beliefs) - conhecimento sobre o ambiente
        self.crencas = {
            'posicao_atual': (x, y),
            'sujeiras_conhecidas': set(),  # Mudado para set para evitar duplicatas
            'obstaculos_conhecidos': obstacles.copy(),
            'casas_visitadas': set(),
            'casas_observadas': set(),
        }
        
        # Desejos (Desires) - objetivos do agente
        self.desejos = ['explorar_ambiente', 'limpar_ambiente']
        
        # Intenções (Intentions) - planos ativos
        self.intencoes = []
        self.plano_atual = []
        self.objetivo_atual = None
        self.rota_otimizada = []  # Rota para pegar todas as sujeiras
        self.fase_exploracao = True
    
    def agir(self):
        """Lógica do agente BDI"""
        # Atualiza crenças
        self.atualizar_crencas()
        
        # Primeiro tenta aspirar na posição atual
        # if self.aspirar():
        #     self.remover_intencao_objetivo()
        #     return
        
        # Revisa desejos baseado nas crenças
        self.revisar_desejos()
        
        # Seleciona intenções baseado nos desejos
        self.selecionar_intencoes()
        
        # Executa intenções
        self.executar_intencoes()
    
    def atualizar_crencas(self):
        """Atualiza as crenças do agente"""
        self.crencas['posicao_atual'] = (self.x, self.y)
       
        self.crencas['casas_visitadas'].add((self.x, self.y))
        
        # Observa posição atual e vizinhos (4 direções)
        movimentos_vizinhos = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in movimentos_vizinhos:
            novo_x = self.x + dx
            novo_y = self.y + dy
            if 0 <= novo_x < 5 and 0 <= novo_y < 5:
                self.crencas['casas_observadas'].add((novo_x, novo_y))
                # Atualiza conhecimento sobre sujeiras
                if self.grid[novo_y][novo_x] > 0:
                    self.crencas['sujeiras_conhecidas'].add((novo_x, novo_y, self.grid[novo_y][novo_x]))
        
        # Remove sujeiras que já foram limpas
        self.crencas['sujeiras_conhecidas'] = {
            (x, y, valor) for (x, y, valor) in self.crencas['sujeiras_conhecidas']
            if self.grid[y][x] > 0
        }
        
    
    def revisar_desejos(self):
        """Revisa os desejos baseado nas crenças atuais"""
        # Verifica se tem sujeiras conhecidas e consegue pegar TODAS com a bateria disponível
        if self.crencas['sujeiras_conhecidas']:
            # Tenta calcular rota que pegue TODAS as sujeiras
            rota_completa = self.calcular_rota_completa()
            
            if rota_completa is not None:
                rota, custo_total = rota_completa
                if self.bateria - custo_total <= 4:
                    # idealmente pegar todas! Muda para fase de limpeza
                    self.desejos = ['limpar_ambiente']
                else:
                    # Bateria de sobra, continua explorando
                    self.desejos = ['explorar_ambiente']
         
        else:
            # Ainda não conhece nenhuma sujeira
            self.desejos = ['explorar_ambiente']
    

    def selecionar_intencoes(self):
        """Seleciona intenções baseado nos desejos"""
        if not self.intencoes:  # Se não tem intenções ativas
            if 'explorar_ambiente' in self.desejos:
                # Encontra casa não visitada mais próxima
                casa_nao_visitada = self.encontrar_casa_nao_visitada()
                if casa_nao_visitada:
                    x_dest, y_dest = casa_nao_visitada
                    self.objetivo_atual = (x_dest, y_dest, 0)
                    self.criar_plano_bdi(x_dest, y_dest)
                    self.intencoes.append('explorar')
                else:
                    # Se não há mais casas para explorar, muda para fase de limpeza
                    self.fase_exploracao = False
                    
            elif 'limpar_rota_otimizada' in self.desejos:
                # Usa a rota já calculada que pega TODAS as sujeiras
                if not self.rota_otimizada:
                    rota = self.calcular_rota_completa()
                    if rota:
                        self.rota_otimizada = rota
                
                if self.rota_otimizada:
                    self.intencoes.append('seguir_rota_otimizada')
                else:
                    # Não conseguiu calcular rota, continua explorando
                    self.fase_exploracao = True
    
    def criar_plano_bdi(self, x_destino, y_destino):
        """Cria um plano para chegar ao destino desviando de obstáculos (BFS)"""
        from collections import deque

        self.plano_atual = []
        inicio = (self.x, self.y)
        destino = (x_destino, y_destino)
        obstacles = set(self.obstacles)

        # BFS para encontrar o caminho mais curto evitando obstáculos
        visitados = set()
        fila = deque()
        fila.append((inicio, []))  # ((x, y), caminho até aqui)

        achou = False
        while fila:
            (x_atual, y_atual), caminho = fila.popleft()
            if (x_atual, y_atual) == destino:
                self.plano_atual = caminho
                achou = True
                break
            if (x_atual, y_atual) in visitados:
                continue
            visitados.add((x_atual, y_atual))
            # Movimentos possíveis: direita, esquerda, baixo, cima
            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                nx, ny = x_atual + dx, y_atual + dy
                if 0 <= nx < 5 and 0 <= ny < 5 and (nx, ny) not in obstacles and (nx, ny) not in visitados:
                    fila.append(((nx, ny), caminho + [(dx, dy)]))
        if not achou:
            # Não encontrou caminho, plano vazio
            self.plano_atual = []
    
    def executar_intencoes(self):
        """Executa as intenções ativas"""
        if 'explorar' in self.intencoes:
            if self.plano_atual:
                dx, dy = self.plano_atual.pop(0)
                if not self.mover(dx, dy):
                    # Se não conseguiu mover, recria o plano
                    if self.objetivo_atual:
                        x_dest, y_dest, _ = self.objetivo_atual
                        self.criar_plano_bdi(x_dest, y_dest)
            else:
                # Plano concluído
                self.remover_intencao_objetivo()
                
        elif 'seguir_rota_otimizada' in self.intencoes:
            if self.rota_otimizada:
                # Pega próximo destino da rota
                x_dest, y_dest, valor = self.rota_otimizada[0]
                
                # Se já está na posição, aspira
                if self.x == x_dest and self.y == y_dest:
                    if self.aspirar():
                        print(f"[BDI] Limpou sujeira em ({x_dest}, {y_dest}) - Valor: {valor}")
                    # Remove da rota
                    self.rota_otimizada.pop(0)
                else:
                    # Cria plano para ir até a sujeira
                    if not self.plano_atual:
                        self.criar_plano_bdi(x_dest, y_dest)
                    
                    if self.plano_atual:
                        dx, dy = self.plano_atual.pop(0)
                        if not self.mover(dx, dy):
                            # Se não conseguiu mover, recria o plano
                            self.criar_plano_bdi(x_dest, y_dest)
            else:
                # Rota concluída
                print(f"[BDI] Rota otimizada concluída! Bateria restante: {self.bateria}")
                self.remover_intencao_objetivo()
    
    def remover_intencao_objetivo(self):
        """Remove a intenção atual quando o objetivo é alcançado"""
        self.intencoes.clear()
        self.objetivo_atual = None
        self.plano_atual = []
    
    def encontrar_casa_nao_visitada(self):
        """Encontra a casa não visitada mais próxima"""
        casas_nao_visitadas = []
        
        for y in range(5):
            for x in range(5):
                if (x, y) not in self.crencas['casas_visitadas'] and (x, y) not in self.obstacles:
                    distancia = self.distancia(self.x, self.y, x, y)
                    casas_nao_visitadas.append((x, y, distancia))
        
        if casas_nao_visitadas:
            # Ordena por distância (mais próxima primeiro)
            casas_nao_visitadas.sort(key=lambda casa: casa[2])
            # Verifica se tem bateria suficiente
            if self.bateria >= casas_nao_visitadas[0][2] + 5:  # +5 margem de segurança
                return (casas_nao_visitadas[0][0], casas_nao_visitadas[0][1])
        
        return None
    
    def calcular_rota_completa(self):
        """Calcula rota para pegar TODAS as sujeiras conhecidas (Vizinho Mais Próximo)
        Retorna a rota se conseguir pegar todas, ou None se não tiver bateria suficiente"""
        
        if not self.crencas['sujeiras_conhecidas']:
            return None
        
        # Converte set para lista
        sujeiras_disponiveis = list(self.crencas['sujeiras_conhecidas'])
        total_sujeiras = len(sujeiras_disponiveis)
        
        # Algoritmo do Vizinho Mais Próximo (sem utilidade, só distância)
        rota = []
        bateria_simulada = self.bateria
        pos_atual = (self.x, self.y)
        
        while sujeiras_disponiveis:
            melhor_sujeira = None
            melhor_distancia = float('inf')
            melhor_indice = -1
            
            # Encontra a sujeira mais próxima da posição atual
            for i, (x, y, valor) in enumerate(sujeiras_disponiveis):
                distancia = self.distancia(pos_atual[0], pos_atual[1], x, y)
                
                if distancia < melhor_distancia:
                    melhor_distancia = distancia
                    melhor_sujeira = (x, y, valor)
                    melhor_indice = i
            
            # Calcula custo para ir até essa sujeira
            if melhor_sujeira:
                x, y, valor = melhor_sujeira
                custo = melhor_distancia + 2  # Distância + custo de aspirar
                
                # Adiciona à rota
                rota.append((x, y, valor))
                bateria_simulada -= custo
                pos_atual = (x, y)
                
                # Remove da lista de disponíveis
                sujeiras_disponiveis.pop(melhor_indice)
        
        # Verifica se conseguiu incluir TODAS as sujeiras
        if len(rota) == total_sujeiras:
            # Verifica se tem bateria suficiente (com margem de segurança)
            custo_total = self.bateria - bateria_simulada
            
            
                # SUCESSO! Consegue pegar todas as sujeiras
            total_valor = sum(valor for _, _, valor in rota)
                
            print(f"\n[BDI] ✅ Rota COMPLETA calculada!")
            print(f"  → Sujeiras: {len(rota)}/{total_sujeiras} (TODAS!)")
            print(f"  → Valor total: {total_valor} pontos")
            print(f"  → Bateria atual: {self.bateria}")
            print(f"  → Custo estimado: {custo_total}")
            print(f"  → Bateria restante estimada: {bateria_simulada}")
            print(f"  📋 Sequência (vizinho mais próximo):")
            for i, (x, y, valor) in enumerate(rota):
                    dist = self.distancia(self.x if i == 0 else rota[i-1][0], 
                                         self.y if i == 0 else rota[i-1][1], x, y)
                    print(f"     {i+1}. ({x}, {y}) - Valor: {valor} - Dist: {dist}")
            print()
                
            return rota, custo_total
       
        else:
            # Não conseguiu incluir todas as sujeiras
            return None
    
    def get_cor(self):
        return (255, 0, 255)  # Magenta
    
    def get_letra(self):
        return "B"
