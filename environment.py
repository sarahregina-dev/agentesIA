"""
Ambiente do Robô Aspirador Inteligente
Grid 5x5 com diferentes tipos de sujeira, obstáculos e bateria limitada.
"""

import random
from typing import List, Tuple, Dict, Optional
from enum import Enum

class TipoSujeira(Enum):
    """Tipos de sujeira com seus respectivos pontos"""
    POEIRA = 1
    LIQUIDO = 2
    DETRITOS = 3
    LIMPO = 0

class TipoCelula(Enum):
    """Tipos de células no ambiente"""
    VAZIA = " "
    OBSTACULO = "█"
    ASPIRADOR = "🤖"

class Acao(Enum):
    """Ações possíveis do agente"""
    NORTE = "N"
    SUL = "S"
    LESTE = "L"
    OESTE = "O"
    ASPIRAR = "ASPIRAR"
    PARAR = "PARAR"

class Environment:
    """Ambiente do robô aspirador inteligente"""
    
    def __init__(self, tamanho_grid: int = 5, bateria_inicial: int = 30, seed: Optional[int] = None):
        self.tamanho_grid = tamanho_grid
        self.bateria_inicial = bateria_inicial
        self.bateria_atual = bateria_inicial
        self.posicao_agente = (0, 0)  # Posição inicial do agente
        self.pontuacao_total = 0
        
        # Inicializar grid com valores aleatórios
        random.seed(seed)
        self._inicializar_grid()
        
    def _inicializar_grid(self):
        """Inicializa o grid com sujeira e obstáculos aleatórios"""
        self.grid = {}
        
        # Definir alguns obstáculos fixos para tornar o ambiente mais interessante
        obstaculos_fixos = [(1, 1), (2, 3), (3, 1), (4, 4)]
        
        for x in range(self.tamanho_grid):
            for y in range(self.tamanho_grid):
                if (x, y) in obstaculos_fixos:
                    self.grid[(x, y)] = {
                        'tipo_celula': TipoCelula.OBSTACULO,
                        'sujeira': TipoSujeira.LIMPO
                    }
                else:
                    # Gerar sujeira aleatória
                    tipo_sujeira = random.choices(
                        [TipoSujeira.LIMPO, TipoSujeira.POEIRA, TipoSujeira.LIQUIDO, TipoSujeira.DETRITOS],
                        weights=[30, 40, 20, 10]  # Probabilidades
                    )[0]
                    
                    self.grid[(x, y)] = {
                        'tipo_celula': TipoCelula.VAZIA,
                        'sujeira': tipo_sujeira
                    }
    
    def perceber(self) -> Dict:
        """Retorna a percepção do agente (posição atual + células vizinhas)"""
        x, y = self.posicao_agente
        
        percepcao = {
            'posicao': self.posicao_agente,
            'bateria': self.bateria_atual,
            'celula_atual': self.grid.get((x, y), None),
            'vizinhos': {}
        }
        
        # Adicionar informações dos vizinhos (N, S, L, O)
        direcoes = {
            'N': (x, y - 1),
            'S': (x, y + 1),
            'L': (x + 1, y),
            'O': (x - 1, y)
        }
        
        for direcao, (nx, ny) in direcoes.items():
            if self._posicao_valida(nx, ny):
                percepcao['vizinhos'][direcao] = self.grid.get((nx, ny), None)
            else:
                percepcao['vizinhos'][direcao] = None
                
        return percepcao
    
    def executar_acao(self, acao: Acao) -> Tuple[bool, int]:
        """
        Executa uma ação do agente
        Retorna: (sucesso, pontos_ganhos)
        """
        if self.bateria_atual <= 0:
            return False, 0
            
        custo_energia = 0
        pontos_ganhos = 0
        
        if acao == Acao.ASPIRAR:
            custo_energia = 2
            x, y = self.posicao_agente
            celula = self.grid.get((x, y))
            if celula and celula['sujeira'] != TipoSujeira.LIMPO:
                pontos_ganhos = celula['sujeira'].value
                celula['sujeira'] = TipoSujeira.LIMPO
                
        elif acao in [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]:
            custo_energia = 1
            nova_posicao = self._calcular_nova_posicao(acao)
            if nova_posicao and self._pode_mover_para(nova_posicao):
                self.posicao_agente = nova_posicao
            else:
                return False, 0  # Movimento inválido
                
        elif acao == Acao.PARAR:
            custo_energia = 0
            
        if self.bateria_atual >= custo_energia:
            self.bateria_atual -= custo_energia
            self.pontuacao_total += pontos_ganhos
            return True, pontos_ganhos
        else:
            return False, 0
    
    def _calcular_nova_posicao(self, acao: Acao) -> Optional[Tuple[int, int]]:
        """Calcula a nova posição baseada na ação de movimento"""
        x, y = self.posicao_agente
        
        if acao == Acao.NORTE:
            return (x, y - 1)
        elif acao == Acao.SUL:
            return (x, y + 1)
        elif acao == Acao.LESTE:
            return (x + 1, y)
        elif acao == Acao.OESTE:
            return (x - 1, y)
        else:
            return None
    
    def _posicao_valida(self, x: int, y: int) -> bool:
        """Verifica se uma posição está dentro dos limites do grid"""
        return 0 <= x < self.tamanho_grid and 0 <= y < self.tamanho_grid
    
    def _pode_mover_para(self, posicao: Tuple[int, int]) -> bool:
        """Verifica se o agente pode mover para uma posição"""
        x, y = posicao
        if not self._posicao_valida(x, y):
            return False
            
        celula = self.grid.get((x, y))
        return celula and celula['tipo_celula'] != TipoCelula.OBSTACULO
    
    def ambiente_limpo(self) -> bool:
        """Verifica se todo o ambiente está limpo"""
        for x in range(self.tamanho_grid):
            for y in range(self.tamanho_grid):
                celula = self.grid.get((x, y))
                if celula and celula['sujeira'] != TipoSujeira.LIMPO:
                    return False
        return True
    
    def bateria_esgotada(self) -> bool:
        """Verifica se a bateria está esgotada"""
        return self.bateria_atual <= 0
    
    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas do ambiente"""
        total_celulas = self.tamanho_grid ** 2
        celulas_limpas = 0
        sujeira_por_tipo = {tipo: 0 for tipo in TipoSujeira}
        
        for x in range(self.tamanho_grid):
            for y in range(self.tamanho_grid):
                celula = self.grid.get((x, y))
                if celula:
                    sujeira = celula['sujeira']
                    sujeira_por_tipo[sujeira] += 1
                    if sujeira == TipoSujeira.LIMPO:
                        celulas_limpas += 1
        
        return {
            'total_celulas': total_celulas,
            'celulas_limpas': celulas_limpas,
            'percentual_limpo': (celulas_limpas / total_celulas) * 100,
            'sujeira_por_tipo': sujeira_por_tipo,
            'bateria_atual': self.bateria_atual,
            'bateria_gasta': self.bateria_inicial - self.bateria_atual,
            'pontuacao_total': self.pontuacao_total,
            'posicao_agente': self.posicao_agente
        }
    
    def imprimir_grid(self):
        """Imprime o grid do ambiente"""
        print(f"\nBateria: {self.bateria_atual}/{self.bateria_inicial} | Pontos: {self.pontuacao_total}")
        print("  0 1 2 3 4")
        
        for y in range(self.tamanho_grid):
            linha = f"{y} "
            for x in range(self.tamanho_grid):
                if (x, y) == self.posicao_agente:
                    linha += "🤖 "
                else:
                    celula = self.grid.get((x, y))
                    if celula:
                        if celula['tipo_celula'] == TipoCelula.OBSTACULO:
                            linha += "█ "
                        else:
                            sujeira = celula['sujeira']
                            if sujeira == TipoSujeira.LIMPO:
                                linha += "· "
                            elif sujeira == TipoSujeira.POEIRA:
                                linha += "· "
                            elif sujeira == TipoSujeira.LIQUIDO:
                                linha += "~ "
                            else:  # DETRITOS
                                linha += "♦ "
                    else:
                        linha += "? "
            print(linha)
        print("Legenda: 🤖=Aspirador, █=Obstáculo, ·=Limpo/Poeira, ~=Líquido, ♦=Detritos")
