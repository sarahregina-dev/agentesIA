"""
Implementação dos agentes baseados em objetivos, utilidade e BDI
"""

from typing import Dict, List, Optional, Tuple, Set
from collections import deque
import heapq
import math
import random
from agent_base import AgenteBase
from environment import Environment, Acao, TipoSujeira, TipoCelula

class AgenteBaseadoObjetivos(AgenteBase):
    """Agente que usa planejamento para alcançar objetivos específicos"""
    
    def __init__(self):
        super().__init__("Agente Baseado em Objetivos")
        self.modelo_ambiente = {}
        self.objetivos = []
        self.plano_atual = []
        self.posicoes_visitadas = set()
        self.posicoes_limpas = set()
    
    def decidir_acao(self, percepcao: Dict, ambiente: Environment) -> Acao:
        """Decide ação baseada em objetivos e planejamento"""
        posicao_atual = percepcao['posicao']
        celula_atual = percepcao['celula_atual']
        
        # Atualizar modelo interno
        self._atualizar_modelo(percepcao)
        
        # Se há sujeira na posição atual, aspirar
        if celula_atual and celula_atual['sujeira'] != TipoSujeira.LIMPO:
            return Acao.ASPIRAR
        
        # Se não há bateria suficiente, parar
        if percepcao['bateria'] <= 2:
            return Acao.PARAR
        
        # Se não há plano ou o plano foi concluído, criar novo plano
        if not self.plano_atual:
            self._criar_plano(posicao_atual, percepcao['bateria'])
        
        # Executar próximo passo do plano
        if self.plano_atual:
            proxima_acao = self.plano_atual.pop(0)
            return proxima_acao
        
        # Fallback: movimento aleatório
        direcoes = [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]
        return random.choice(direcoes)
    
    def _atualizar_modelo(self, percepcao: Dict):
        """Atualiza o modelo interno do ambiente"""
        posicao_atual = percepcao['posicao']
        self.posicoes_visitadas.add(posicao_atual)
        
        # Atualizar informações da posição atual
        celula_atual = percepcao['celula_atual']
        if celula_atual:
            self.modelo_ambiente[posicao_atual] = celula_atual.copy()
            if celula_atual['sujeira'] == TipoSujeira.LIMPO:
                self.posicoes_limpas.add(posicao_atual)
        
        # Atualizar informações dos vizinhos
        for direcao, vizinho in percepcao['vizinhos'].items():
            if vizinho:
                posicao_vizinho = self._calcular_posicao_vizinho(posicao_atual, direcao)
                if posicao_vizinho:
                    self.modelo_ambiente[posicao_vizinho] = vizinho.copy()
    
    def _calcular_posicao_vizinho(self, posicao_atual: Tuple[int, int], direcao: str) -> Optional[Tuple[int, int]]:
        """Calcula a posição do vizinho baseado na direção"""
        x, y = posicao_atual
        if direcao == 'N':
            return (x, y - 1)
        elif direcao == 'S':
            return (x, y + 1)
        elif direcao == 'L':
            return (x + 1, y)
        elif direcao == 'O':
            return (x - 1, y)
        return None
    
    def _criar_plano(self, posicao_atual: Tuple[int, int], bateria_atual: int):
        """Cria um plano para limpar o ambiente de forma eficiente"""
        self.plano_atual = []
        
        # Encontrar todas as posições com sujeira
        posicoes_sujeira = []
        for posicao, celula in self.modelo_ambiente.items():
            if (celula['sujeira'] != TipoSujeira.LIMPO and 
                posicao not in self.posicoes_limpas):
                posicoes_sujeira.append(posicao)
        
        if not posicoes_sujeira:
            # Se não há sujeira conhecida, explorar posições não visitadas
            self._plano_exploracao(posicao_atual)
            return
        
        # Ordenar posições de sujeira por prioridade (valor da sujeira / distância)
        posicoes_priorizadas = []
        for posicao in posicoes_sujeira:
            celula = self.modelo_ambiente[posicao]
            distancia = abs(posicao[0] - posicao_atual[0]) + abs(posicao[1] - posicao_atual[1])
            prioridade = celula['sujeira'].value / max(distancia, 1)
            posicoes_priorizadas.append((prioridade, posicao, celula['sujeira'].value))
        
        posicoes_priorizadas.sort(reverse=True)
        
        # Criar caminho para as posições mais importantes
        posicao_destino = None
        for _, pos, valor in posicoes_priorizadas:
            custo_estimado = self._calcular_custo_caminho(posicao_atual, pos)
            if custo_estimado <= bateria_atual - 2:  # Reservar energia para aspirar
                posicao_destino = pos
                break
        
        if posicao_destino:
            self._criar_caminho_para(posicao_atual, posicao_destino)
        else:
            # Se não consegue chegar a nenhuma sujeira, explorar
            self._plano_exploracao(posicao_atual)
    
    def _plano_exploracao(self, posicao_atual: Tuple[int, int]):
        """Cria um plano para explorar posições não visitadas"""
        posicoes_nao_visitadas = []
        for x in range(5):
            for y in range(5):
                posicao = (x, y)
                if posicao not in self.posicoes_visitadas:
                    if posicao in self.modelo_ambiente:
                        if self.modelo_ambiente[posicao]['tipo_celula'] != TipoCelula.OBSTACULO:
                            posicoes_nao_visitadas.append(posicao)
        
        if posicoes_nao_visitadas:
            # Escolher a posição não visitada mais próxima
            posicao_destino = min(posicoes_nao_visitadas, 
                                key=lambda p: abs(p[0] - posicao_atual[0]) + abs(p[1] - posicao_atual[1]))
            self._criar_caminho_para(posicao_atual, posicao_destino)
    
    def _calcular_custo_caminho(self, origem: Tuple[int, int], destino: Tuple[int, int]) -> int:
        """Calcula o custo estimado para ir de origem a destino"""
        return abs(destino[0] - origem[0]) + abs(destino[1] - origem[1])
    
    def _criar_caminho_para(self, origem: Tuple[int, int], destino: Tuple[int, int]):
        """Cria um caminho simples de origem a destino"""
        x_orig, y_orig = origem
        x_dest, y_dest = destino
        
        # Movimento horizontal primeiro, depois vertical
        while x_orig != x_dest:
            if x_orig < x_dest:
                self.plano_atual.append(Acao.LESTE)
                x_orig += 1
            else:
                self.plano_atual.append(Acao.OESTE)
                x_orig -= 1
        
        while y_orig != y_dest:
            if y_orig < y_dest:
                self.plano_atual.append(Acao.SUL)
                y_orig += 1
            else:
                self.plano_atual.append(Acao.NORTE)
                y_orig -= 1
        
        # Adicionar ação de aspirar ao final
        self.plano_atual.append(Acao.ASPIRAR)
    
    def reset(self):
        """Reseta o agente para um novo ambiente"""
        super().reset()
        self.modelo_ambiente = {}
        self.objetivos = []
        self.plano_atual = []
        self.posicoes_visitadas = set()
        self.posicoes_limpas = set()

class AgenteBaseadoUtilidade(AgenteBase):
    """Agente que maximiza utilidade considerando custos e benefícios"""
    
    def __init__(self):
        super().__init__("Agente Baseado em Utilidade")
        self.modelo_ambiente = {}
        self.posicoes_visitadas = set()
        self.posicoes_limpas = set()
        self.fatores_utilidade = {
            'peso_sujeira': 1.0,      # Peso do valor da sujeira
            'peso_distancia': 0.5,    # Peso da distância (penalidade)
            'peso_exploracao': 0.3,   # Peso da exploração
            'peso_bateria': 0.8       # Peso da conservação de bateria
        }
    
    def decidir_acao(self, percepcao: Dict, ambiente: Environment) -> Acao:
        """Decide ação baseada em cálculo de utilidade"""
        posicao_atual = percepcao['posicao']
        celula_atual = percepcao['celula_atual']
        
        # Atualizar modelo interno
        self._atualizar_modelo(percepcao)
        
        # Se há sujeira na posição atual, aspirar
        if celula_atual and celula_atual['sujeira'] != TipoSujeira.LIMPO:
            return Acao.ASPIRAR
        
        # Se não há bateria suficiente, parar
        if percepcao['bateria'] <= 2:
            return Acao.PARAR
        
        # Calcular utilidade de cada ação possível
        acoes_possiveis = self._obter_acoes_possiveis(posicao_atual, percepcao['bateria'])
        
        if not acoes_possiveis:
            return Acao.PARAR
        
        # Escolher ação com maior utilidade
        melhor_acao = max(acoes_possiveis, key=lambda acao: self._calcular_utilidade(acao, posicao_atual, percepcao))
        return melhor_acao
    
    def _atualizar_modelo(self, percepcao: Dict):
        """Atualiza o modelo interno do ambiente"""
        posicao_atual = percepcao['posicao']
        self.posicoes_visitadas.add(posicao_atual)
        
        # Atualizar informações da posição atual
        celula_atual = percepcao['celula_atual']
        if celula_atual:
            self.modelo_ambiente[posicao_atual] = celula_atual.copy()
            if celula_atual['sujeira'] == TipoSujeira.LIMPO:
                self.posicoes_limpas.add(posicao_atual)
        
        # Atualizar informações dos vizinhos
        for direcao, vizinho in percepcao['vizinhos'].items():
            if vizinho:
                posicao_vizinho = self._calcular_posicao_vizinho(posicao_atual, direcao)
                if posicao_vizinho:
                    self.modelo_ambiente[posicao_vizinho] = vizinho.copy()
    
    def _calcular_posicao_vizinho(self, posicao_atual: Tuple[int, int], direcao: str) -> Optional[Tuple[int, int]]:
        """Calcula a posição do vizinho baseado na direção"""
        x, y = posicao_atual
        if direcao == 'N':
            return (x, y - 1)
        elif direcao == 'S':
            return (x, y + 1)
        elif direcao == 'L':
            return (x + 1, y)
        elif direcao == 'O':
            return (x - 1, y)
        return None
    
    def _obter_acoes_possiveis(self, posicao_atual: Tuple[int, int], bateria_atual: int) -> List[Acao]:
        """Retorna lista de ações possíveis baseadas na posição e bateria"""
        acoes = []
        
        # Verificar movimentos possíveis
        direcoes = [
            (Acao.NORTE, (posicao_atual[0], posicao_atual[1] - 1)),
            (Acao.SUL, (posicao_atual[0], posicao_atual[1] + 1)),
            (Acao.LESTE, (posicao_atual[0] + 1, posicao_atual[1])),
            (Acao.OESTE, (posicao_atual[0] - 1, posicao_atual[1]))
        ]
        
        for acao, nova_posicao in direcoes:
            if self._pode_mover_para(nova_posicao) and bateria_atual >= 1:
                acoes.append(acao)
        
        return acoes
    
    def _pode_mover_para(self, posicao: Tuple[int, int]) -> bool:
        """Verifica se pode mover para uma posição"""
        x, y = posicao
        if not (0 <= x < 5 and 0 <= y < 5):
            return False
        
        if posicao in self.modelo_ambiente:
            return self.modelo_ambiente[posicao]['tipo_celula'] != TipoCelula.OBSTACULO
        
        return True
    
    def _calcular_utilidade(self, acao: Acao, posicao_atual: Tuple[int, int], percepcao: Dict) -> float:
        """Calcula a utilidade de uma ação"""
        utilidade = 0.0
        
        if acao in [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]:
            # Calcular nova posição após o movimento
            nova_posicao = self._calcular_nova_posicao(posicao_atual, acao)
            
            # Utilidade baseada na sujeira na nova posição
            if nova_posicao in self.modelo_ambiente:
                celula = self.modelo_ambiente[nova_posicao]
                utilidade += celula['sujeira'].value * self.fatores_utilidade['peso_sujeira']
            
            # Penalidade por distância (preferir movimentos que se aproximam de sujeira)
            sujeira_mais_proxima = self._encontrar_sujeira_mais_proxima(nova_posicao)
            if sujeira_mais_proxima:
                distancia = abs(sujeira_mais_proxima[0] - nova_posicao[0]) + abs(sujeira_mais_proxima[1] - nova_posicao[1])
                utilidade -= distancia * self.fatores_utilidade['peso_distancia']
            
            # Bonus por exploração de posições não visitadas
            if nova_posicao not in self.posicoes_visitadas:
                utilidade += self.fatores_utilidade['peso_exploracao']
            
            # Penalidade por gasto de energia
            utilidade -= self.fatores_utilidade['peso_bateria']
        
        return utilidade
    
    def _calcular_nova_posicao(self, posicao_atual: Tuple[int, int], acao: Acao) -> Tuple[int, int]:
        """Calcula a nova posição após uma ação de movimento"""
        x, y = posicao_atual
        if acao == Acao.NORTE:
            return (x, y - 1)
        elif acao == Acao.SUL:
            return (x, y + 1)
        elif acao == Acao.LESTE:
            return (x + 1, y)
        elif acao == Acao.OESTE:
            return (x - 1, y)
        return posicao_atual
    
    def _encontrar_sujeira_mais_proxima(self, posicao: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Encontra a posição com sujeira mais próxima"""
        melhor_posicao = None
        menor_distancia = float('inf')
        
        for pos, celula in self.modelo_ambiente.items():
            if celula['sujeira'] != TipoSujeira.LIMPO and pos not in self.posicoes_limpas:
                distancia = abs(pos[0] - posicao[0]) + abs(pos[1] - posicao[1])
                if distancia < menor_distancia:
                    menor_distancia = distancia
                    melhor_posicao = pos
        
        return melhor_posicao
    
    def reset(self):
        """Reseta o agente para um novo ambiente"""
        super().reset()
        self.modelo_ambiente = {}
        self.posicoes_visitadas = set()
        self.posicoes_limpas = set()

class AgenteBDI(AgenteBase):
    """Agente BDI (Beliefs, Desires, Intentions) com arquitetura cognitiva"""
    
    def __init__(self):
        super().__init__("Agente BDI")
        self.crencas = {}  # Modelo do ambiente (beliefs)
        self.desejos = []  # Objetivos (desires)
        self.intencoes = []  # Planos atuais (intentions)
        self.posicoes_visitadas = set()
        self.posicoes_limpas = set()
        self.estado_emocional = "neutral"  # Estados: neutral, focused, desperate
        
    def decidir_acao(self, percepcao: Dict, ambiente: Environment) -> Acao:
        """Decide ação baseada na arquitetura BDI"""
        posicao_atual = percepcao['posicao']
        celula_atual = percepcao['celula_atual']
        
        # Atualizar crenças
        self._atualizar_crencas(percepcao)
        
        # Atualizar estado emocional baseado na situação
        self._atualizar_estado_emocional(percepcao)
        
        # Se há sujeira na posição atual, aspirar
        if celula_atual and celula_atual['sujeira'] != TipoSujeira.LIMPO:
            return Acao.ASPIRAR
        
        # Se não há bateria suficiente, parar
        if percepcao['bateria'] <= 2:
            return Acao.PARAR
        
        # Atualizar desejos baseados nas crenças
        self._atualizar_desejos()
        
        # Selecionar intenções baseadas nos desejos
        self._selecionar_intencoes()
        
        # Executar ação baseada nas intenções
        if self.intencoes:
            proxima_acao = self.intencoes.pop(0)
            return proxima_acao
        
        # Fallback: movimento aleatório
        direcoes = [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]
        return random.choice(direcoes)
    
    def _atualizar_crencas(self, percepcao: Dict):
        """Atualiza as crenças sobre o ambiente"""
        posicao_atual = percepcao['posicao']
        self.posicoes_visitadas.add(posicao_atual)
        
        # Atualizar informações da posição atual
        celula_atual = percepcao['celula_atual']
        if celula_atual:
            self.crencas[posicao_atual] = celula_atual.copy()
            if celula_atual['sujeira'] == TipoSujeira.LIMPO:
                self.posicoes_limpas.add(posicao_atual)
        
        # Atualizar informações dos vizinhos
        for direcao, vizinho in percepcao['vizinhos'].items():
            if vizinho:
                posicao_vizinho = self._calcular_posicao_vizinho(posicao_atual, direcao)
                if posicao_vizinho:
                    self.crencas[posicao_vizinho] = vizinho.copy()
    
    def _calcular_posicao_vizinho(self, posicao_atual: Tuple[int, int], direcao: str) -> Optional[Tuple[int, int]]:
        """Calcula a posição do vizinho baseado na direção"""
        x, y = posicao_atual
        if direcao == 'N':
            return (x, y - 1)
        elif direcao == 'S':
            return (x, y + 1)
        elif direcao == 'L':
            return (x + 1, y)
        elif direcao == 'O':
            return (x - 1, y)
        return None
    
    def _atualizar_estado_emocional(self, percepcao: Dict):
        """Atualiza o estado emocional baseado na situação"""
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
        """Atualiza os desejos baseados nas crenças atuais"""
        self.desejos = []
        
        # Desejo de limpar sujeira
        for posicao, celula in self.crencas.items():
            if celula['sujeira'] != TipoSujeira.LIMPO and posicao not in self.posicoes_limpas:
                prioridade = celula['sujeira'].value
                self.desejos.append({
                    'tipo': 'limpar',
                    'posicao': posicao,
                    'prioridade': prioridade,
                    'valor': celula['sujeira'].value
                })
        
        # Desejo de explorar posições não visitadas
        for x in range(5):
            for y in range(5):
                posicao = (x, y)
                if posicao not in self.posicoes_visitadas:
                    if posicao in self.crencas:
                        if self.crencas[posicao]['tipo_celula'] != TipoCelula.OBSTACULO:
                            self.desejos.append({
                                'tipo': 'explorar',
                                'posicao': posicao,
                                'prioridade': 1,
                                'valor': 0
                            })
        
        # Ordenar desejos por prioridade
        self.desejos.sort(key=lambda d: d['prioridade'], reverse=True)
    
    def _selecionar_intencoes(self):
        """Seleciona intenções baseadas nos desejos e estado emocional"""
        self.intencoes = []
        
        if not self.desejos:
            return
        
        # Baseado no estado emocional, selecionar estratégia
        if self.estado_emocional == "desperate":
            # Focar em limpar sujeira de maior valor rapidamente
            desejo = max([d for d in self.desejos if d['tipo'] == 'limpar'], 
                        key=lambda d: d['valor'], default=None)
        elif self.estado_emocional == "focused":
            # Focar em sujeira próxima
            desejo = next((d for d in self.desejos if d['tipo'] == 'limpar'), None)
        else:
            # Estratégia balanceada
            desejo = self.desejos[0] if self.desejos else None
        
        if desejo:
            # Encontrar posição atual
            posicao_atual = next(
                pos for pos, celula in self.crencas.items() 
                if celula.get('agente_presente', False)
            ) if any(celula.get('agente_presente', False) for celula in self.crencas.values()) else (0, 0)
            
            # Criar plano para alcançar o desejo
            if desejo['tipo'] == 'limpar':
                self._criar_plano_limpeza(posicao_atual, desejo['posicao'])
            elif desejo['tipo'] == 'explorar':
                self._criar_plano_exploracao(posicao_atual, desejo['posicao'])
    
    def _criar_plano_limpeza(self, origem: Tuple[int, int], destino: Tuple[int, int]):
        """Cria um plano para limpar uma posição específica"""
        x_orig, y_orig = origem
        x_dest, y_dest = destino
        
        # Movimento horizontal primeiro
        while x_orig != x_dest:
            if x_orig < x_dest:
                self.intencoes.append(Acao.LESTE)
                x_orig += 1
            else:
                self.intencoes.append(Acao.OESTE)
                x_orig -= 1
        
        # Movimento vertical
        while y_orig != y_dest:
            if y_orig < y_dest:
                self.intencoes.append(Acao.SUL)
                y_orig += 1
            else:
                self.intencoes.append(Acao.NORTE)
                y_orig -= 1
        
        # Adicionar ação de aspirar
        self.intencoes.append(Acao.ASPIRAR)
    
    def _criar_plano_exploracao(self, origem: Tuple[int, int], destino: Tuple[int, int]):
        """Cria um plano para explorar uma posição"""
        self._criar_plano_limpeza(origem, destino)
    
    def reset(self):
        """Reseta o agente para um novo ambiente"""
        super().reset()
        self.crencas = {}
        self.desejos = []
        self.intencoes = []
        self.posicoes_visitadas = set()
        self.posicoes_limpas = set()
        self.estado_emocional = "neutral"
