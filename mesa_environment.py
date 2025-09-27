"""
Ambiente Mesa para o Robô Aspirador Inteligente
Implementa visualização gráfica usando a biblioteca Mesa
"""

import random
from typing import List, Tuple, Dict, Optional
from enum import Enum
import mesa
import mesa.space
import mesa.time
import mesa.visualization
import mesa.DataCollector

class TipoSujeira(Enum):
    """Tipos de sujeira com seus respectivos pontos"""
    LIMPO = 0
    POEIRA = 1
    LIQUIDO = 2
    DETRITOS = 3

class TipoCelula(Enum):
    """Tipos de células no ambiente"""
    VAZIA = "vazia"
    OBSTACULO = "obstaculo"

class Acao(Enum):
    """Ações possíveis do agente"""
    NORTE = "norte"
    SUL = "sul"
    LESTE = "leste"
    OESTE = "oeste"
    ASPIRAR = "aspirar"
    PARAR = "parar"

class Celula(mesa.Agent):
    """Representa uma célula do grid"""
    
    def __init__(self, unique_id, model, pos, tipo_sujeira=TipoSujeira.LIMPO, tipo_celula=TipoCelula.VAZIA):
        super().__init__(unique_id, model)
        self.pos = pos
        self.tipo_sujeira = tipo_sujeira
        self.tipo_celula = tipo_celula
        self.pontos = tipo_sujeira.value
    
    def limpar(self):
        """Remove a sujeira da célula"""
        pontos_ganhos = self.pontos
        self.tipo_sujeira = TipoSujeira.LIMPO
        self.pontos = 0
        return pontos_ganhos
    
    def step(self):
        """Não faz nada por si só"""
        pass

class Aspirador(mesa.Agent):
    """Agente aspirador que pode ser de diferentes tipos"""
    
    def __init__(self, unique_id, model, tipo_agente):
        super().__init__(unique_id, model)
        self.tipo_agente = tipo_agente
        self.bateria = 30
        self.bateria_inicial = 30
        self.pontos_coletados = 0
        self.historico_acoes = []
        self.estatisticas = {
            'total_acoes': 0,
            'acoes_movimento': 0,
            'acoes_aspirar': 0,
            'acoes_parar': 0,
            'movimentos_invalidos': 0,
            'energia_gasta': 0
        }
        
        # Modelo interno (para agentes que precisam)
        self.modelo_ambiente = {}
        self.posicoes_visitadas = set()
        self.posicoes_limpas = set()
        
        # Para agentes BDI
        self.crencas = {}
        self.desejos = []
        self.intencoes = []
        self.estado_emocional = "neutral"
    
    def step(self):
        """Executa um ciclo do agente"""
        if self.bateria <= 0:
            return
        
        # Perceber ambiente
        percepcao = self._perceber()
        
        # Decidir ação
        acao = self._decidir_acao(percepcao)
        
        # Executar ação
        self._executar_acao(acao)
        
        # Verificar condições de parada
        if acao == Acao.PARAR or self.bateria <= 0 or self._ambiente_limpo():
            return
    
    def _perceber(self) -> Dict:
        """Coleta informações do ambiente"""
        x, y = self.pos
        
        percepcao = {
            'posicao': self.pos,
            'bateria': self.bateria,
            'celula_atual': self._obter_celula(x, y),
            'vizinhos': {}
        }
        
        # Adicionar informações dos vizinhos
        direcoes = {
            'norte': (x, y - 1),
            'sul': (x, y + 1),
            'leste': (x + 1, y),
            'oeste': (x - 1, y)
        }
        
        for direcao, (nx, ny) in direcoes.items():
            if self.model._posicao_valida(nx, ny):
                percepcao['vizinhos'][direcao] = self._obter_celula(nx, ny)
            else:
                percepcao['vizinhos'][direcao] = None
        
        return percepcao
    
    def _obter_celula(self, x: int, y: int) -> Optional[Dict]:
        """Obtém informações de uma célula"""
        if not self.model._posicao_valida(x, y):
            return None
        
        celula = self.model.grid.get_cell_list_contents((x, y))
        if celula and isinstance(celula[0], Celula):
            c = celula[0]
            return {
                'tipo_celula': c.tipo_celula,
                'sujeira': c.tipo_sujeira,
                'pontos': c.pontos
            }
        return None
    
    def _decidir_acao(self, percepcao: Dict) -> Acao:
        """Decide qual ação tomar baseado no tipo de agente"""
        if self.tipo_agente == "reativo":
            return self._decisao_reativa(percepcao)
        elif self.tipo_agente == "modelo":
            return self._decisao_modelo(percepcao)
        elif self.tipo_agente == "objetivos":
            return self._decisao_objetivos(percepcao)
        elif self.tipo_agente == "utilidade":
            return self._decisao_utilidade(percepcao)
        elif self.tipo_agente == "bdi":
            return self._decisao_bdi(percepcao)
        else:
            return Acao.PARAR
    
    def _decisao_reativa(self, percepcao: Dict) -> Acao:
        """Decisão do agente reativo simples"""
        celula_atual = percepcao['celula_atual']
        
        # Se há sujeira na posição atual, aspirar
        if celula_atual and celula_atual['sujeira'] != TipoSujeira.LIMPO:
            return Acao.ASPIRAR
        
        # Se não há bateria suficiente, parar
        if percepcao['bateria'] <= 2:
            return Acao.PARAR
        
        # Procurar sujeira nas células vizinhas
        vizinhos = percepcao['vizinhos']
        for direcao, vizinho in vizinhos.items():
            if vizinho and vizinho['sujeira'] != TipoSujeira.LIMPO:
                return Acao(direcao)
        
        # Movimento aleatório
        direcoes = [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]
        return random.choice(direcoes)
    
    def _decisao_modelo(self, percepcao: Dict) -> Acao:
        """Decisão do agente baseado em modelo"""
        self._atualizar_modelo_interno(percepcao)
        
        celula_atual = percepcao['celula_atual']
        
        # Se há sujeira na posição atual, aspirar
        if celula_atual and celula_atual['sujeira'] != TipoSujeira.LIMPO:
            return Acao.ASPIRAR
        
        # Se não há bateria suficiente, parar
        if percepcao['bateria'] <= 2:
            return Acao.PARAR
        
        # Procurar a posição não visitada mais próxima
        proxima_posicao = self._encontrar_proxima_posicao_nao_visitada()
        if proxima_posicao:
            return self._calcular_movimento_para(percepcao['posicao'], proxima_posicao)
        
        # Movimento aleatório
        direcoes = [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]
        return random.choice(direcoes)
    
    def _decisao_objetivos(self, percepcao: Dict) -> Acao:
        """Decisão do agente baseado em objetivos"""
        self._atualizar_modelo_interno(percepcao)
        
        celula_atual = percepcao['celula_atual']
        
        # Se há sujeira na posição atual, aspirar
        if celula_atual and celula_atual['sujeira'] != TipoSujeira.LIMPO:
            return Acao.ASPIRAR
        
        # Se não há bateria suficiente, parar
        if percepcao['bateria'] <= 2:
            return Acao.PARAR
        
        # Encontrar sujeira de maior valor
        posicao_sujeira = self._encontrar_sujeira_maior_valor()
        if posicao_sujeira:
            return self._calcular_movimento_para(percepcao['posicao'], posicao_sujeira)
        
        # Movimento aleatório
        direcoes = [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]
        return random.choice(direcoes)
    
    def _decisao_utilidade(self, percepcao: Dict) -> Acao:
        """Decisão do agente baseado em utilidade"""
        self._atualizar_modelo_interno(percepcao)
        
        celula_atual = percepcao['celula_atual']
        
        # Se há sujeira na posição atual, aspirar
        if celula_atual and celula_atual['sujeira'] != TipoSujeira.LIMPO:
            return Acao.ASPIRAR
        
        # Se não há bateria suficiente, parar
        if percepcao['bateria'] <= 2:
            return Acao.PARAR
        
        # Calcular utilidade de cada ação
        acoes_possiveis = [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]
        melhor_acao = max(acoes_possiveis, key=lambda acao: self._calcular_utilidade(acao, percepcao))
        return melhor_acao
    
    def _decisao_bdi(self, percepcao: Dict) -> Acao:
        """Decisão do agente BDI"""
        self._atualizar_crencas(percepcao)
        self._atualizar_estado_emocional(percepcao)
        self._atualizar_desejos()
        self._selecionar_intencoes()
        
        celula_atual = percepcao['celula_atual']
        
        # Se há sujeira na posição atual, aspirar
        if celula_atual and celula_atual['sujeira'] != TipoSujeira.LIMPO:
            return Acao.ASPIRAR
        
        # Se não há bateria suficiente, parar
        if percepcao['bateria'] <= 2:
            return Acao.PARAR
        
        # Executar intenções
        if self.intencoes:
            return self.intencoes.pop(0)
        
        # Movimento aleatório
        direcoes = [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]
        return random.choice(direcoes)
    
    def _executar_acao(self, acao: Acao):
        """Executa uma ação"""
        custo_energia = 0
        pontos_ganhos = 0
        
        if acao == Acao.ASPIRAR:
            custo_energia = 2
            x, y = self.pos
            celula = self.model.grid.get_cell_list_contents((x, y))
            if celula and isinstance(celula[0], Celula):
                pontos_ganhos = celula[0].limpar()
                
        elif acao in [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]:
            custo_energia = 1
            nova_posicao = self._calcular_nova_posicao(acao)
            if nova_posicao and self._pode_mover_para(nova_posicao):
                self.model.grid.move_agent(self, nova_posicao)
            else:
                self.estatisticas['movimentos_invalidos'] += 1
                return
        
        # Atualizar estatísticas
        self.bateria -= custo_energia
        self.pontos_coletados += pontos_ganhos
        self.historico_acoes.append(acao)
        self.estatisticas['total_acoes'] += 1
        self.estatisticas['energia_gasta'] += custo_energia
        
        if acao == Acao.ASPIRAR:
            self.estatisticas['acoes_aspirar'] += 1
        elif acao in [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]:
            self.estatisticas['acoes_movimento'] += 1
        elif acao == Acao.PARAR:
            self.estatisticas['acoes_parar'] += 1
    
    def _calcular_nova_posicao(self, acao: Acao) -> Optional[Tuple[int, int]]:
        """Calcula a nova posição baseada na ação"""
        x, y = self.pos
        if acao == Acao.NORTE:
            return (x, y - 1)
        elif acao == Acao.SUL:
            return (x, y + 1)
        elif acao == Acao.LESTE:
            return (x + 1, y)
        elif acao == Acao.OESTE:
            return (x - 1, y)
        return None
    
    def _pode_mover_para(self, posicao: Tuple[int, int]) -> bool:
        """Verifica se pode mover para uma posição"""
        x, y = posicao
        if not self.model._posicao_valida(x, y):
            return False
        
        celula = self.model.grid.get_cell_list_contents((x, y))
        if celula and isinstance(celula[0], Celula):
            return celula[0].tipo_celula != TipoCelula.OBSTACULO
        
        return True
    
    def _ambiente_limpo(self) -> bool:
        """Verifica se o ambiente está limpo"""
        for x in range(5):
            for y in range(5):
                celula = self.model.grid.get_cell_list_contents((x, y))
                if celula and isinstance(celula[0], Celula):
                    if celula[0].tipo_sujeira != TipoSujeira.LIMPO:
                        return False
        return True
    
    # Métodos auxiliares para diferentes tipos de agentes
    def _atualizar_modelo_interno(self, percepcao: Dict):
        """Atualiza o modelo interno do ambiente"""
        posicao_atual = percepcao['posicao']
        self.posicoes_visitadas.add(posicao_atual)
        
        celula_atual = percepcao['celula_atual']
        if celula_atual:
            self.modelo_ambiente[posicao_atual] = celula_atual.copy()
            if celula_atual['sujeira'] == TipoSujeira.LIMPO:
                self.posicoes_limpas.add(posicao_atual)
        
        for direcao, vizinho in percepcao['vizinhos'].items():
            if vizinho:
                posicao_vizinho = self._calcular_posicao_vizinho(posicao_atual, direcao)
                if posicao_vizinho:
                    self.modelo_ambiente[posicao_vizinho] = vizinho.copy()
    
    def _calcular_posicao_vizinho(self, posicao_atual: Tuple[int, int], direcao: str) -> Optional[Tuple[int, int]]:
        """Calcula a posição do vizinho"""
        x, y = posicao_atual
        if direcao == 'norte':
            return (x, y - 1)
        elif direcao == 'sul':
            return (x, y + 1)
        elif direcao == 'leste':
            return (x + 1, y)
        elif direcao == 'oeste':
            return (x - 1, y)
        return None
    
    def _encontrar_proxima_posicao_nao_visitada(self) -> Optional[Tuple[int, int]]:
        """Encontra a próxima posição não visitada"""
        x_atual, y_atual = self.pos
        melhor_posicao = None
        menor_distancia = float('inf')
        
        for x in range(5):
            for y in range(5):
                posicao = (x, y)
                if posicao not in self.posicoes_visitadas:
                    if posicao in self.modelo_ambiente:
                        if self.modelo_ambiente[posicao]['tipo_celula'] == TipoCelula.OBSTACULO:
                            continue
                    distancia = abs(x - x_atual) + abs(y - y_atual)
                    if distancia < menor_distancia:
                        menor_distancia = distancia
                        melhor_posicao = posicao
        
        return melhor_posicao
    
    def _encontrar_sujeira_maior_valor(self) -> Optional[Tuple[int, int]]:
        """Encontra a sujeira de maior valor"""
        melhor_posicao = None
        maior_valor = 0
        
        for posicao, celula in self.modelo_ambiente.items():
            if (celula['sujeira'] != TipoSujeira.LIMPO and 
                posicao not in self.posicoes_limpas):
                if celula['pontos'] > maior_valor:
                    maior_valor = celula['pontos']
                    melhor_posicao = posicao
        
        return melhor_posicao
    
    def _calcular_movimento_para(self, origem: Tuple[int, int], destino: Tuple[int, int]) -> Acao:
        """Calcula o movimento necessário"""
        x_orig, y_orig = origem
        x_dest, y_dest = destino
        
        if x_dest > x_orig:
            return Acao.LESTE
        elif x_dest < x_orig:
            return Acao.OESTE
        elif y_dest > y_orig:
            return Acao.SUL
        elif y_dest < y_orig:
            return Acao.NORTE
        
        return Acao.PARAR
    
    def _calcular_utilidade(self, acao: Acao, percepcao: Dict) -> float:
        """Calcula a utilidade de uma ação"""
        if acao not in [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]:
            return 0.0
        
        nova_posicao = self._calcular_nova_posicao(acao)
        if not nova_posicao:
            return -1.0
        
        utilidade = 0.0
        
        # Utilidade baseada na sujeira
        if nova_posicao in self.modelo_ambiente:
            celula = self.modelo_ambiente[nova_posicao]
            utilidade += celula['pontos'] * 1.0
        
        # Bonus por exploração
        if nova_posicao not in self.posicoes_visitadas:
            utilidade += 0.5
        
        # Penalidade por energia
        utilidade -= 0.2
        
        return utilidade
    
    def _atualizar_crencas(self, percepcao: Dict):
        """Atualiza as crenças do agente BDI"""
        posicao_atual = percepcao['posicao']
        self.posicoes_visitadas.add(posicao_atual)
        
        celula_atual = percepcao['celula_atual']
        if celula_atual:
            self.crencas[posicao_atual] = celula_atual.copy()
            if celula_atual['sujeira'] == TipoSujeira.LIMPO:
                self.posicoes_limpas.add(posicao_atual)
        
        for direcao, vizinho in percepcao['vizinhos'].items():
            if vizinho:
                posicao_vizinho = self._calcular_posicao_vizinho(posicao_atual, direcao)
                if posicao_vizinho:
                    self.crencas[posicao_vizinho] = vizinho.copy()
    
    def _atualizar_estado_emocional(self, percepcao: Dict):
        """Atualiza o estado emocional do agente BDI"""
        bateria_baixa = percepcao['bateria'] < 10
        sujeira_proxima = any(
            vizinho and vizinho['sujeira'] != TipoSujeira.LIMPO 
            for vizinho in percepcao['vizinhos'].values()
        )
        
        if bateria_baixa:
            self.estado_emocional = "desperate"
        elif sujeira_proxima:
            self.estado_emocional = "focused"
        else:
            self.estado_emocional = "neutral"
    
    def _atualizar_desejos(self):
        """Atualiza os desejos do agente BDI"""
        self.desejos = []
        
        for posicao, celula in self.crencas.items():
            if celula['sujeira'] != TipoSujeira.LIMPO and posicao not in self.posicoes_limpas:
                self.desejos.append({
                    'tipo': 'limpar',
                    'posicao': posicao,
                    'prioridade': celula['pontos'],
                    'valor': celula['pontos']
                })
        
        self.desejos.sort(key=lambda d: d['prioridade'], reverse=True)
    
    def _selecionar_intencoes(self):
        """Seleciona intenções baseadas nos desejos"""
        self.intencoes = []
        
        if not self.desejos:
            return
        
        if self.estado_emocional == "desperate":
            desejo = max([d for d in self.desejos if d['tipo'] == 'limpar'], 
                        key=lambda d: d['valor'], default=None)
        elif self.estado_emocional == "focused":
            desejo = next((d for d in self.desejos if d['tipo'] == 'limpar'), None)
        else:
            desejo = self.desejos[0] if self.desejos else None
        
        if desejo and desejo['tipo'] == 'limpar':
            self._criar_plano_limpeza(self.pos, desejo['posicao'])
    
    def _criar_plano_limpeza(self, origem: Tuple[int, int], destino: Tuple[int, int]):
        """Cria um plano para limpar uma posição"""
        x_orig, y_orig = origem
        x_dest, y_dest = destino
        
        while x_orig != x_dest:
            if x_orig < x_dest:
                self.intencoes.append(Acao.LESTE)
                x_orig += 1
            else:
                self.intencoes.append(Acao.OESTE)
                x_orig -= 1
        
        while y_orig != y_dest:
            if y_orig < y_dest:
                self.intencoes.append(Acao.SUL)
                y_orig += 1
            else:
                self.intencoes.append(Acao.NORTE)
                y_orig -= 1
        
        self.intencoes.append(Acao.ASPIRAR)

class AmbienteAspirador(mesa.Model):
    """Modelo principal do ambiente aspirador"""
    
    def __init__(self, width=5, height=5, tipo_agente="reativo", seed=None):
        super().__init__()
        self.width = width
        self.height = height
        self.tipo_agente = tipo_agente
        self.grid = mesa.space.SingleGrid(width, height, torus=False)
        self.schedule = mesa.time.SimultaneousActivation(self)
        
        # Inicializar ambiente
        random.seed(seed)
        self._inicializar_ambiente()
        
        # Criar agente aspirador
        aspirador = Aspirador(1, self, tipo_agente)
        self.schedule.add(aspirador)
        self.grid.place_agent(aspirador, (0, 0))
        
        # Coletar dados
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Pontos_Coletados": self._calcular_pontos_coletados,
                "Bateria_Atual": self._calcular_bateria_atual,
                "Percentual_Limpo": self._calcular_percentual_limpo,
                "Total_Acoes": self._calcular_total_acoes,
            },
            agent_reporters={
                "Pontos": "pontos_coletados",
                "Bateria": "bateria",
                "Tipo_Agente": "tipo_agente"
            }
        )
    
    def _inicializar_ambiente(self):
        """Inicializa o ambiente com sujeira e obstáculos"""
        # Definir obstáculos fixos
        obstaculos = [(1, 1), (2, 3), (3, 1), (4, 4)]
        
        for x in range(self.width):
            for y in range(self.height):
                if (x, y) in obstaculos:
                    # Criar obstáculo
                    celula = Celula(f"obst_{x}_{y}", self, (x, y), TipoSujeira.LIMPO, TipoCelula.OBSTACULO)
                    self.grid.place_agent(celula, (x, y))
                else:
                    # Gerar sujeira aleatória
                    tipo_sujeira = random.choices(
                        [TipoSujeira.LIMPO, TipoSujeira.POEIRA, TipoSujeira.LIQUIDO, TipoSujeira.DETRITOS],
                        weights=[30, 40, 20, 10]
                    )[0]
                    
                    celula = Celula(f"cel_{x}_{y}", self, (x, y), tipo_sujeira, TipoCelula.VAZIA)
                    self.grid.place_agent(celula, (x, y))
    
    def _posicao_valida(self, x: int, y: int) -> bool:
        """Verifica se uma posição está dentro dos limites"""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def step(self):
        """Executa um passo da simulação"""
        self.schedule.step()
        self.datacollector.collect(self)
    
    def _calcular_pontos_coletados(self) -> int:
        """Calcula pontos coletados por todos os agentes"""
        total = 0
        for agent in self.schedule.agents:
            if isinstance(agent, Aspirador):
                total += agent.pontos_coletados
        return total
    
    def _calcular_bateria_atual(self) -> int:
        """Calcula bateria atual dos agentes"""
        total = 0
        for agent in self.schedule.agents:
            if isinstance(agent, Aspirador):
                total += agent.bateria
        return total
    
    def _calcular_percentual_limpo(self) -> float:
        """Calcula percentual do ambiente limpo"""
        total_celulas = 0
        celulas_limpas = 0
        
        for x in range(self.width):
            for y in range(self.height):
                celula = self.grid.get_cell_list_contents((x, y))
                if celula and isinstance(celula[0], Celula):
                    total_celulas += 1
                    if celula[0].tipo_sujeira == TipoSujeira.LIMPO:
                        celulas_limpas += 1
        
        return (celulas_limpas / max(total_celulas, 1)) * 100
    
    def _calcular_total_acoes(self) -> int:
        """Calcula total de ações executadas"""
        total = 0
        for agent in self.schedule.agents:
            if isinstance(agent, Aspirador):
                total += agent.estatisticas['total_acoes']
        return total

def obter_agente_por_tipo(tipo: str) -> Aspirador:
    """Retorna um agente do tipo especificado"""
    return Aspirador(1, None, tipo)
