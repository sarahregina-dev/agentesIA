"""
Classe base para todos os tipos de agentes racionais
Define a interface comum e funcionalidades compartilhadas.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from environment import Environment, Acao, TipoSujeira, TipoCelula
import random

class AgenteBase(ABC):
    """Classe base abstrata para todos os agentes"""
    
    def __init__(self, nome: str):
        self.nome = nome
        self.historico_acoes = []
        self.historico_percepcoes = []
        self.estatisticas = {
            'total_acoes': 0,
            'acoes_movimento': 0,
            'acoes_aspirar': 0,
            'acoes_parar': 0,
            'movimentos_invalidos': 0,
            'pontos_coletados': 0,
            'energia_gasta': 0
        }
    
    @abstractmethod
    def decidir_acao(self, percepcao: Dict, ambiente: Environment) -> Acao:
        """
        Decide qual ação tomar baseado na percepção atual
        Deve ser implementado por cada tipo de agente
        """
        pass
    
    def executar_ciclo(self, ambiente: Environment) -> bool:
        """
        Executa um ciclo completo: perceber, decidir, agir
        Retorna True se o agente ainda pode continuar, False caso contrário
        """
        # Perceber
        percepcao = ambiente.perceber()
        self.historico_percepcoes.append(percepcao.copy())
        
        # Decidir ação
        acao = self.decidir_acao(percepcao, ambiente)
        
        # Executar ação
        sucesso, pontos_ganhos = ambiente.executar_acao(acao)
        
        # Atualizar estatísticas
        self._atualizar_estatisticas(acao, sucesso, pontos_ganhos, percepcao)
        
        # Verificar condições de parada
        if acao == Acao.PARAR or ambiente.bateria_esgotada() or ambiente.ambiente_limpo():
            return False
            
        return True
    
    def _atualizar_estatisticas(self, acao: Acao, sucesso: bool, pontos_ganhos: int, percepcao: Dict):
        """Atualiza as estatísticas do agente"""
        self.historico_acoes.append(acao)
        self.estatisticas['total_acoes'] += 1
        self.estatisticas['pontos_coletados'] += pontos_ganhos
        
        if acao == Acao.ASPIRAR:
            self.estatisticas['acoes_aspirar'] += 1
            self.estatisticas['energia_gasta'] += 2
        elif acao in [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]:
            self.estatisticas['acoes_movimento'] += 1
            if not sucesso:
                self.estatisticas['movimentos_invalidos'] += 1
            else:
                self.estatisticas['energia_gasta'] += 1
        elif acao == Acao.PARAR:
            self.estatisticas['acoes_parar'] += 1
    
    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas detalhadas do agente"""
        stats = self.estatisticas.copy()
        stats['nome'] = self.nome
        stats['eficiencia_movimento'] = (
            (stats['acoes_movimento'] - stats['movimentos_invalidos']) / 
            max(stats['acoes_movimento'], 1)
        )
        stats['pontos_por_energia'] = (
            stats['pontos_coletados'] / max(stats['energia_gasta'], 1)
        )
        return stats
    
    def reset(self):
        """Reseta o agente para um novo ambiente"""
        self.historico_acoes = []
        self.historico_percepcoes = []
        self.estatisticas = {
            'total_acoes': 0,
            'acoes_movimento': 0,
            'acoes_aspirar': 0,
            'acoes_parar': 0,
            'movimentos_invalidos': 0,
            'pontos_coletados': 0,
            'energia_gasta': 0
        }

class AgenteReativoSimples(AgenteBase):
    """Agente que reage diretamente às percepções sem memória"""
    
    def __init__(self):
        super().__init__("Agente Reativo Simples")
    
    def decidir_acao(self, percepcao: Dict, ambiente: Environment) -> Acao:
        """Decide ação baseada apenas na percepção atual"""
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
                # Mover na direção da sujeira
                if direcao == 'N':
                    return Acao.NORTE
                elif direcao == 'S':
                    return Acao.SUL
                elif direcao == 'L':
                    return Acao.LESTE
                elif direcao == 'O':
                    return Acao.OESTE
        
        # Se não encontrou sujeira próxima, mover aleatoriamente
        direcoes = [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]
        return random.choice(direcoes)

class AgenteBaseadoModelo(AgenteBase):
    """Agente que mantém um modelo interno do ambiente"""
    
    def __init__(self):
        super().__init__("Agente Baseado em Modelo")
        self.modelo_ambiente = {}
        self.posicoes_visitadas = set()
        self.posicoes_limpas = set()
    
    def decidir_acao(self, percepcao: Dict, ambiente: Environment) -> Acao:
        """Decide ação baseada no modelo interno do ambiente"""
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
        
        # Procurar a posição não visitada mais próxima
        proxima_posicao = self._encontrar_proxima_posicao_nao_visitada(posicao_atual)
        if proxima_posicao:
            return self._calcular_movimento_para(posicao_atual, proxima_posicao)
        
        # Se todas as posições foram visitadas, procurar sujeira conhecida
        posicao_sujeira = self._encontrar_proxima_sujeira_conhecida(posicao_atual)
        if posicao_sujeira:
            return self._calcular_movimento_para(posicao_atual, posicao_sujeira)
        
        # Movimento aleatório se não há objetivo claro
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
    
    def _encontrar_proxima_posicao_nao_visitada(self, posicao_atual: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Encontra a posição não visitada mais próxima"""
        x_atual, y_atual = posicao_atual
        melhor_posicao = None
        menor_distancia = float('inf')
        
        for x in range(5):  # Grid 5x5
            for y in range(5):
                posicao = (x, y)
                if posicao not in self.posicoes_visitadas:
                    # Verificar se não é obstáculo
                    if posicao in self.modelo_ambiente:
                        if self.modelo_ambiente[posicao]['tipo_celula'] == TipoCelula.OBSTACULO:
                            continue
                    distancia = abs(x - x_atual) + abs(y - y_atual)
                    if distancia < menor_distancia:
                        menor_distancia = distancia
                        melhor_posicao = posicao
        
        return melhor_posicao
    
    def _encontrar_proxima_sujeira_conhecida(self, posicao_atual: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Encontra a posição com sujeira conhecida mais próxima"""
        x_atual, y_atual = posicao_atual
        melhor_posicao = None
        menor_distancia = float('inf')
        
        for posicao, celula in self.modelo_ambiente.items():
            if (celula['sujeira'] != TipoSujeira.LIMPO and 
                posicao not in self.posicoes_limpas):
                x, y = posicao
                distancia = abs(x - x_atual) + abs(y - y_atual)
                if distancia < menor_distancia:
                    menor_distancia = distancia
                    melhor_posicao = posicao
        
        return melhor_posicao
    
    def _calcular_movimento_para(self, posicao_atual: Tuple[int, int], posicao_destino: Tuple[int, int]) -> Acao:
        """Calcula o movimento necessário para ir de uma posição para outra"""
        x_atual, y_atual = posicao_atual
        x_dest, y_dest = posicao_destino
        
        if x_dest > x_atual:
            return Acao.LESTE
        elif x_dest < x_atual:
            return Acao.OESTE
        elif y_dest > y_atual:
            return Acao.SUL
        elif y_dest < y_atual:
            return Acao.NORTE
        
        return Acao.PARAR
    
    def reset(self):
        """Reseta o agente para um novo ambiente"""
        super().reset()
        self.modelo_ambiente = {}
        self.posicoes_visitadas = set()
        self.posicoes_limpas = set()
