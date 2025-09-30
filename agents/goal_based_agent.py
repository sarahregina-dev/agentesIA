import random
from .base_agent import BaseAgent

class GoalBasedAgent(BaseAgent):
    """Agente baseado em objetivos - define metas e planeja como alcançá-las"""
    
    def __init__(self, nome, ambiente, x, y, grid, obstacles):
        super().__init__(nome, ambiente, x, y, grid, obstacles)
        self.objetivo_atual = None
        self.plano = []
        self.estado_objetivo = "buscar_sujeira"  # buscar_sujeira, ir_para_sujeira, aspirar
    
    def agir(self):
        """Lógica do agente baseado em objetivos"""
        # Primeiro tenta aspirar na posição atual
        if self.aspirar():
            self.estado_objetivo = "buscar_sujeira"
            return
        
        # Define objetivo se não tem um
        if self.estado_objetivo == "buscar_sujeira":
            self.definir_objetivo()
        
        # Executa o plano para alcançar o objetivo
        if self.estado_objetivo == "ir_para_sujeira" and self.objetivo_atual:
            self.executar_plano()
    
    def definir_objetivo(self):
        """Define um novo objetivo (sujeira mais próxima)"""
        sujeira_proxima = self.encontrar_sujeira_mais_proxima()
        if sujeira_proxima:
            x_dest, y_dest, valor, distancia = sujeira_proxima
            self.objetivo_atual = (x_dest, y_dest, valor)
            self.estado_objetivo = "ir_para_sujeira"
            self.criar_plano(x_dest, y_dest)
        else:
            # Se não há sujeira, explora aleatoriamente
            self.estado_objetivo = "explorar"
    
    def criar_plano(self, x_destino, y_destino):
        """Cria um plano simples para chegar ao destino"""
        self.plano = []
        x_atual, y_atual = self.x, self.y
        
        # Plano simples: move horizontalmente primeiro, depois verticalmente
        while x_atual != x_destino:
            if x_atual < x_destino:
                self.plano.append((1, 0))  # Direita
                x_atual += 1
            else:
                self.plano.append((-1, 0))  # Esquerda
                x_atual -= 1
        
        while y_atual != y_destino:
            if y_atual < y_destino:
                self.plano.append((0, 1))  # Baixo
                y_atual += 1
            else:
                self.plano.append((0, -1))  # Cima
                y_atual -= 1
    
    def executar_plano(self):
        """Executa o próximo passo do plano"""
        if self.plano:
            dx, dy = self.plano.pop(0)
            if not self.mover(dx, dy):
                # Se não conseguiu mover, recria o plano
                if self.objetivo_atual:
                    x_dest, y_dest, _ = self.objetivo_atual
                    self.criar_plano(x_dest, y_dest)
        else:
            # Plano concluído, volta a buscar sujeira
            self.estado_objetivo = "buscar_sujeira"
            self.objetivo_atual = None
    
    def get_cor(self):
        return (255, 165, 0)  # Laranja
    
    def get_letra(self):
        return "G"
