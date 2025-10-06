import random
from .base_agent import BaseAgent

class UtilityBasedAgent(BaseAgent):
    """Agente baseado em utilidade - avalia diferentes ações e escolhe a de maior utilidade"""
    
    def __init__(self, nome, ambiente, x, y, grid, obstacles):
        super().__init__(nome, ambiente, x, y, grid, obstacles)
        # Modelo interno do ambiente
        self.modelo_grid = [[0 for _ in range(5)] for _ in range(5)]
        self.modelo_obstacles = obstacles.copy()
        self.ultima_acao = None
        # Rastreamento de casas visitadas
        self.casas_visitadas = set()
        self.casas_visitadas.add((x, y))  # Marca posição inicial como visitada
    
    def agir(self):
        """Lógica do agente baseado em modelo com priorização de casas não visitadas"""
        # Atualiza modelo com informações da posição atual
        self.atualizar_modelo()
  
        # Marca posição atual como visitada
        self.casas_visitadas.add((self.x, self.y))
        
        # Primeiro tenta aspirar na posição atual
        if self.aspirar():
            self.ultima_acao = "aspirar"
            return
        
        # Procura sujeira no modelo local
        sujeira_proxima = self.encontrar_sujeira_mais_proxima()
        if sujeira_proxima:
            x_dest, y_dest, _ = sujeira_proxima
            dx, dy = self.caminho_para_posicao(x_dest, y_dest)
            
            if self.mover(dx, dy):
                self.ultima_acao = "mover_para_sujeira"
                return
        
        # Prioriza casas não visitadas
        casa_nao_visitada = self.encontrar_casa_nao_visitada()
        if casa_nao_visitada:
            x_dest, y_dest = casa_nao_visitada
            dx, dy = self.caminho_para_posicao(x_dest, y_dest)
            if self.mover(dx, dy):
                self.ultima_acao = "explorar_nao_visitada"
                return

        self.parar()
    
    def atualizar_modelo(self):
        """Atualiza o modelo interno com informações atuais"""
        # Atualiza a posição atual no modelo
        self.modelo_grid[self.y][self.x] = self.grid[self.y][self.x]
        
        # Observa apenas as 4 casas imediatamente próximas (norte, sul, leste, oeste)
        movimentos_vizinhos = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # norte, sul, leste, oeste
        for dx, dy in movimentos_vizinhos:
            novo_x = self.x + dx
            novo_y = self.y + dy
            if 0 <= novo_x < 5 and 0 <= novo_y < 5:
                self.modelo_grid[novo_y][novo_x] = self.grid[novo_y][novo_x]
    
    def encontrar_sujeira_mais_proxima(self):
        """Encontra a sujeira mais próxima no modelo_grid (todo o grid conhecido pelo agente)"""
        sujeiras = []
        for y in range(5):
            for x in range(5):
                if self.modelo_grid[y][x] > 0:
                    distancia = self.distancia(self.x, self.y, x, y) 
        #    
                    sujeiras.append((x, y, self.modelo_grid[y][x]/( distancia + 2) ))

        if sujeiras:
                sujeiras.sort(key=lambda s: s[2], reverse=True) #maior utilidade primeiro
                if self.bateria >= sujeiras[0][2]:
                    print("sujeira mais proxima", sujeiras[0], "posicao", self.x, self.y)
                    return sujeiras[0]
        return None
    
    def encontrar_casa_nao_visitada(self):
        """Encontra a casa não visitada mais próxima entre as casas conhecidas"""
        casas_nao_visitadas = []
        
        # Procura apenas nas casas conhecidas (que o agente já observou)
        for y in range(5):
            for x in range(5):
                # Verifica se a casa foi modelada (conhecida) e não foi visitada
                if (x, y) not in self.casas_visitadas and (x, y) not in self.obstacles:
                    # Considera apenas casas conhecidas (já observadas pelo agente)
                    # Uma casa é "conhecida" se já foi observada (tem valor no modelo_grid)
                    # ou se é a posição atual
                    distancia = self.distancia(self.x, self.y, x, y)
                    casas_nao_visitadas.append((x, y, distancia))
        
        if casas_nao_visitadas:
            # Ordena por distância (mais próxima primeiro)
            casas_nao_visitadas.sort(key=lambda casa: casa[2], reverse=False) #mais próxima primeiro
            # Só vai se tiver bateria suficiente para chegar lá + margem de segurança
            if self.bateria >= casas_nao_visitadas[0][2] + 3:
               
                return (casas_nao_visitadas[0][0], casas_nao_visitadas[0][1])
        
        return None
    
    
    
    def get_cor(self):
        return (128, 0, 128)  # Roxo
    
    def get_letra(self):
        return "U"
