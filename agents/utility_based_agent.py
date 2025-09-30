import random
from .base_agent import BaseAgent

class UtilityBasedAgent(BaseAgent):
    """Agente baseado em utilidade - avalia diferentes ações e escolhe a de maior utilidade"""
    
    def __init__(self, nome, ambiente, x, y, grid, obstacles):
        super().__init__(nome, ambiente, x, y, grid, obstacles)
        self.historico_utilidades = []
    
    def agir(self):
        """Lógica do agente baseado em utilidade"""
        # Primeiro tenta aspirar na posição atual
        if self.aspirar():
            return
        
        # Avalia todas as ações possíveis
        acoes = self.avaliar_acoes()
        
        # Escolhe a ação com maior utilidade
        if acoes:
            melhor_acao = max(acoes, key=lambda a: a['utilidade'])
            self.executar_acao(melhor_acao)
    
    def avaliar_acoes(self):
        """Avalia todas as ações possíveis e retorna suas utilidades"""
        acoes = []
        
        # Ação: aspirar (já foi tentada)
        # Ação: mover para cada direção
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            novo_x = self.x + dx
            novo_y = self.y + dy
            
            if 0 <= novo_x < 5 and 0 <= novo_y < 5 and (novo_x, novo_y) not in self.obstacles:
                utilidade = self.calcular_utilidade_movimento(novo_x, novo_y)
                acoes.append({
                    'tipo': 'mover',
                    'dx': dx,
                    'dy': dy,
                    'utilidade': utilidade
                })
        
        return acoes
    
    def calcular_utilidade_movimento(self, x, y):
        """Calcula a utilidade de se mover para uma posição"""
        utilidade = 0
        
        # Utilidade baseada na sujeira na posição
        if self.grid[y][x] > 0:
            utilidade += self.grid[y][x] * 10  # Valor da sujeira
        
        # Utilidade baseada na proximidade de outras sujeiras
        sujeiras_proximas = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                novo_x = x + dx
                novo_y = y + dy
                if 0 <= novo_x < 5 and 0 <= novo_y < 5:
                    if self.grid[novo_y][novo_x] > 0:
                        sujeiras_proximas += 1
        
        utilidade += sujeiras_proximas * 2
        
        # Penalidade por já ter visitado a posição
        if (x, y) in self.historico_posicoes:
            utilidade -= 1
        
        # Utilidade baseada na distância do centro (exploração)
        distancia_centro = abs(x - 2) + abs(y - 2)
        utilidade += (4 - distancia_centro) * 0.5
        
        return utilidade
    
    def executar_acao(self, acao):
        """Executa a ação escolhida"""
        if acao['tipo'] == 'mover':
            self.mover(acao['dx'], acao['dy'])
    
    def get_cor(self):
        return (128, 0, 128)  # Roxo
    
    def get_letra(self):
        return "U"
