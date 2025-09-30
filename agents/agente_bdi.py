import random
from .base_agent import BaseAgent

class AgenteBDI(BaseAgent):
    """Agente BDI (Beliefs, Desires, Intentions) - arquitetura cognitiva"""
    
    def __init__(self, nome, ambiente, x, y, grid, obstacles):
        super().__init__(nome, ambiente, x, y, grid, obstacles)
        # Crenças (Beliefs) - conhecimento sobre o ambiente
        self.crencas = {
            'posicao_atual': (x, y),
            'bateria_baixa': False,
            'sujeiras_conhecidas': [],
            'obstaculos_conhecidos': obstacles.copy()
        }
        
        # Desejos (Desires) - objetivos do agente
        self.desejos = ['limpar_ambiente', 'conservar_bateria', 'evitar_obstaculos']
        
        # Intenções (Intentions) - planos ativos
        self.intencoes = []
        self.plano_atual = []
        self.objetivo_atual = None
    
    def agir(self):
        """Lógica do agente BDI"""
        # Atualiza crenças
        self.atualizar_crencas()
        
        # Primeiro tenta aspirar na posição atual
        if self.aspirar():
            self.remover_intencao_objetivo()
            return
        
        # Revisa desejos baseado nas crenças
        self.revisar_desejos()
        
        # Seleciona intenções baseado nos desejos
        self.selecionar_intencoes()
        
        # Executa intenções
        self.executar_intencoes()
    
    def atualizar_crencas(self):
        """Atualiza as crenças do agente"""
        self.crencas['posicao_atual'] = (self.x, self.y)
        self.crencas['bateria_baixa'] = self.bateria < 20
        
        # Atualiza conhecimento sobre sujeiras
        for y in range(5):
            for x in range(5):
                if self.grid[y][x] > 0:
                    sujeira = (x, y, self.grid[y][x])
                    if sujeira not in self.crencas['sujeiras_conhecidas']:
                        self.crencas['sujeiras_conhecidas'].append(sujeira)
    
    def revisar_desejos(self):
        """Revisa os desejos baseado nas crenças atuais"""
        if self.crencas['bateria_baixa']:
            # Prioriza conservar bateria
            self.desejos = ['conservar_bateria', 'limpar_ambiente', 'evitar_obstaculos']
        else:
            # Prioriza limpar ambiente
            self.desejos = ['limpar_ambiente', 'conservar_bateria', 'evitar_obstaculos']
    
    def selecionar_intencoes(self):
        """Seleciona intenções baseado nos desejos"""
        if not self.intencoes:  # Se não tem intenções ativas
            if 'limpar_ambiente' in self.desejos and self.crencas['sujeiras_conhecidas']:
                # Seleciona a sujeira mais próxima
                sujeira_proxima = self.encontrar_sujeira_mais_proxima()
                if sujeira_proxima:
                    x_dest, y_dest, valor, _ = sujeira_proxima
                    self.objetivo_atual = (x_dest, y_dest, valor)
                    self.criar_plano_bdi(x_dest, y_dest)
                    self.intencoes.append('ir_para_sujeira')
            elif 'conservar_bateria' in self.desejos:
                # Vai para o centro para economizar bateria
                self.objetivo_atual = (2, 2, 0)
                self.criar_plano_bdi(2, 2)
                self.intencoes.append('ir_para_centro')
    
    def criar_plano_bdi(self, x_destino, y_destino):
        """Cria um plano para chegar ao destino"""
        self.plano_atual = []
        x_atual, y_atual = self.x, self.y
        
        # Plano simples: move horizontalmente primeiro, depois verticalmente
        while x_atual != x_destino:
            if x_atual < x_destino:
                self.plano_atual.append((1, 0))  # Direita
                x_atual += 1
            else:
                self.plano_atual.append((-1, 0))  # Esquerda
                x_atual -= 1
        
        while y_atual != y_destino:
            if y_atual < y_destino:
                self.plano_atual.append((0, 1))  # Baixo
                y_atual += 1
            else:
                self.plano_atual.append((0, -1))  # Cima
                y_atual -= 1
    
    def executar_intencoes(self):
        """Executa as intenções ativas"""
        if 'ir_para_sujeira' in self.intencoes or 'ir_para_centro' in self.intencoes:
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
    
    def remover_intencao_objetivo(self):
        """Remove a intenção atual quando o objetivo é alcançado"""
        if 'ir_para_sujeira' in self.intencoes:
            self.intencoes.remove('ir_para_sujeira')
        if 'ir_para_centro' in self.intencoes:
            self.intencoes.remove('ir_para_centro')
        self.objetivo_atual = None
        self.plano_atual = []
    
    def get_cor(self):
        return (255, 0, 255)  # Magenta
    
    def get_letra(self):
        return "B"
