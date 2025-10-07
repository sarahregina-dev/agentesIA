import pygame
import random
import simpy
import constantes

from agents.simple_agent import SimpleAgent
from agents.model_based_agent import ModelBasedAgent
from agents.goal_based_agent import GoalBasedAgent
from agents.utility_based_agent import UtilityBasedAgent
from agents.agente_bdi import AgenteBDI

def gerar_ambiente():
    """Gera o ambiente 5x5 com sujeiras e obstáculos"""
    grid = [[0 for _ in range(5)] for _ in range(5)]
    obstacles = []
    
    # Gera obstáculos (3-5 móveis)
    # num_obstacles = random.randint(3, 4)
    num_obstacles = 3
    for _ in range(num_obstacles):
        while True:
            x = random.randint(0, 4)
            y = random.randint(0, 4)
            # Não coloca obstáculos nas bordas para facilitar movimento
            if (x, y) not in obstacles and (x != 2 or y != 2):
                obstacles.append((x, y))
                break
    
                



    # Gera sujeiras (8-12 no total)
    tipos_sujeira = [1, 2, 3]  # Mais poeira, menos detritos
    total_sujeiras = random.randint(8, 12)
    
    for _ in range(total_sujeiras):
        while True:
            x = random.randint(0, 4)
            y = random.randint(0, 4)
            if grid[y][x] == 0 and (x, y) not in obstacles:
                grid[y][x] = random.choice(tipos_sujeira)
                break
    # grid[2][3] = 3
    # grid[3][2] = 2
    return grid, obstacles

def mostrar_tela_inicial(tela):
    """Tela inicial do simulador"""
    fonte_titulo = pygame.font.SysFont("times", 36)
    fonte_botao = pygame.font.SysFont("arial", 24)
    
    titulo = fonte_titulo.render("Simulador - Robô Aspirador Inteligente", True, (255, 255, 255))
    subtitulo = fonte_botao.render("Comparação de Agentes Racionais", True, (200, 200, 200))
    botao_rect = pygame.Rect(constantes.WINDOW_WIDTH // 2 - 100, constantes.WINDOW_HEIGHT // 2, 200, 50)
    texto_botao = fonte_botao.render("Iniciar Simulação", True, (255, 255, 255))

    esperando = True
    while esperando:
        tela.fill((50, 50, 80))  # Azul escuro
        
        # Título e subtítulo
        tela.blit(titulo, (constantes.WINDOW_WIDTH // 2 - titulo.get_width() // 2, 100))
        tela.blit(subtitulo, (constantes.WINDOW_WIDTH // 2 - subtitulo.get_width() // 2, 150))
        
        # Botão
        pygame.draw.rect(tela, (70, 130, 180), botao_rect, border_radius=10)
        tela.blit(texto_botao, (constantes.WINDOW_WIDTH // 2 - texto_botao.get_width() // 2, 
                               botao_rect.y + texto_botao.get_height() // 2))
        
        # Legenda dos agentes
        fonte_legenda = pygame.font.SysFont("arial", 16)
        legendas = [
            "S - Agente Reativo Simples",
            "M - Agente Baseado em Modelo", 
            "G - Agente Baseado em Objetivos",
            "U - Agente Baseado em Utilidade",
            "B - Agente BDI"
        ]
        
        for i, legenda in enumerate(legendas):
            texto = fonte_legenda.render(legenda, True, (255, 255, 255))
            tela.blit(texto, (50, 300 + i * 25))
        
        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN and botao_rect.collidepoint(evento.pos):
                esperando = False

def mostrar_tela_resultado(tela, agentes):
    """Tela de resultados finais"""
    fonte_titulo = pygame.font.SysFont("arial", 32)
    fonte_resultado = pygame.font.SysFont("arial", 24)
    fonte_botao = pygame.font.SysFont("arial", 20)
    
    titulo = fonte_titulo.render("Resultados da Simulação", True, (255, 255, 255))
    botao_rect = pygame.Rect(constantes.WINDOW_WIDTH // 2 - 150, constantes.WINDOW_HEIGHT - 100, 300, 50)
    texto_botao = fonte_botao.render("Nova Simulação", True, (255, 255, 255))

    # Ordena agentes por pontuação
    agentes_ordenados = sorted(agentes, key=lambda a: a.pontuacao, reverse=True)
    
    esperando = True
    while esperando:
        tela.fill((50, 50, 80))
        tela.blit(titulo, (constantes.WINDOW_WIDTH // 2 - titulo.get_width() // 2, 40))

        # Resultados
        for i, agente in enumerate(agentes_ordenados):
            cor = (255, 255, 0) if i == 0 else (255, 255, 255)  # Destaque para o primeiro
            resultado = fonte_resultado.render(
                f"{i+1}º - {agente.nome}: {agente.pontuacao} pontos (Bateria: {agente.bateria})", 
                True, cor
            )
            tela.blit(resultado, (60, 100 + i * 40))
        
        # Estatísticas adicionais
        total_pontos = sum(agente.pontuacao for agente in agentes)
        stats = fonte_resultado.render(f"Total de pontos coletados: {total_pontos}", True, (200, 200, 200))
        tela.blit(stats, (60, 100 + len(agentes) * 40 + 20))

        # Botão
        pygame.draw.rect(tela, (70, 130, 180), botao_rect, border_radius=10)
        tela.blit(texto_botao, (constantes.WINDOW_WIDTH // 2 - texto_botao.get_width() // 2, 
                               botao_rect.y + 15))

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN and botao_rect.collidepoint(evento.pos):
                main()
                return

def parar_agente(agente):
    """Para um agente específico"""
    agente.parar()

def desenhar_ambiente(tela, grid, obstacles, agentes):
    """Desenha o ambiente completo"""
    # Fundo
    tela.fill((240, 240, 240))  # Cinza claro
    
    # Grade
    for x in range(5):
        for y in range(5):
            rect = pygame.Rect(x * constantes.CELL_SIZE, y * constantes.CELL_SIZE, 
                             constantes.CELL_SIZE, constantes.CELL_SIZE)
            pygame.draw.rect(tela, (255, 255, 255), rect)
            pygame.draw.rect(tela, (200, 200, 200), rect, 1)
    
    # Obstáculos
    for x, y in obstacles:
        pygame.draw.rect(tela, (100, 100, 100), 
                        (x * constantes.CELL_SIZE, y * constantes.CELL_SIZE, 
                         constantes.CELL_SIZE, constantes.CELL_SIZE))
    
    # Sujeiras
    fonte_sujeira = pygame.font.SysFont("arial", 12)
    for y in range(5):
        for x in range(5):
            if grid[y][x] > 0:
                cor = {
                    1: (200, 200, 200),   # Poeira - cinza
                    2: (100, 100, 255),   # Líquido - azul  
                    3: (139, 69, 19)      # Detritos - marrom
                }.get(grid[y][x], (0, 0, 0))
                
                pygame.draw.circle(tela, cor, 
                                 (x * constantes.CELL_SIZE + constantes.CELL_SIZE // 2,
                                  y * constantes.CELL_SIZE + constantes.CELL_SIZE // 2), 
                                 8)
                
                # Mostra valor da sujeira
                texto = fonte_sujeira.render(str(grid[y][x]), True, (0, 0, 0))
                tela.blit(texto, (x * constantes.CELL_SIZE + 8, y * constantes.CELL_SIZE + 6))
    
    # Agentes
    for agente in agentes:
        agente.desenhar(tela)
    
    # Painel de informações
    desenhar_painel_info(tela, agentes)

def desenhar_painel_info(tela, agentes):
    """Desenha painel com informações dos agentes"""
    painel_rect = pygame.Rect(5 * constantes.CELL_SIZE, 0, 
                             constantes.WINDOW_WIDTH - 5 * constantes.CELL_SIZE, 
                             constantes.WINDOW_HEIGHT)
    pygame.draw.rect(tela, (60, 60, 80), painel_rect)
    
    fonte_titulo = pygame.font.SysFont("arial", 20)
    fonte_info = pygame.font.SysFont("arial", 14)
    
    titulo = fonte_titulo.render("Status dos Agentes", True, (255, 255, 255))
    tela.blit(titulo, (5 * constantes.CELL_SIZE + 20, 20))
    
    for i, agente in enumerate(agentes):
        y_pos = 60 + i * 80
        cor_agente = {
            'SimpleAgent': constantes.BLUE,
            'ModelBasedAgent': constantes.GREEN, 
            'GoalBasedAgent': constantes.ORANGE,
            'UtilityBasedAgent': constantes.PURPLE,
            'AgenteBDI': (255, 0, 255)
        }.get(agente.__class__.__name__, (255, 255, 255))
        
        # Quadrado com cor do agente
        pygame.draw.rect(tela, cor_agente, (5 * constantes.CELL_SIZE + 20, y_pos, 20, 20))
        
        # Informações
        info_lines = [
            f"{agente.nome}",
            f"Pontos: {agente.pontuacao}",
            f"Bateria: {agente.bateria}",
            f"Posição: ({agente.x}, {agente.y})"
        ]
        
        for j, line in enumerate(info_lines):
            texto = fonte_info.render(line, True, (255, 255, 255))
            tela.blit(texto, (5 * constantes.CELL_SIZE + 50, y_pos + j * 18))

def main():
    """Função principal da simulação"""
    pygame.init()
    tela = pygame.display.set_mode((constantes.WINDOW_WIDTH, constantes.WINDOW_HEIGHT))
    pygame.display.set_caption("Simulador - Robô Aspirador Inteligente")
    relogio = pygame.time.Clock()
    
    ambiente = simpy.Environment()
    
    # Tela inicial
    mostrar_tela_inicial(tela)
    
    # Gera ambiente
    grid, obstacles = gerar_ambiente()
    
    # Criação dos agentes (todos começam na posição 2,2 - centro)
    pos_inicial_x, pos_inicial_y = 2, 2
    
    # agente_simples = SimpleAgent("Simples", ambiente, pos_inicial_x, pos_inicial_y, grid, obstacles)
    # agente_modelo = ModelBasedAgent("Modelo", ambiente, pos_inicial_x, pos_inicial_y, grid, obstacles)
    # agente_objetivo = GoalBasedAgent("Objetivo", ambiente, pos_inicial_x, pos_inicial_y, grid, obstacles)
    # agente_utilidade = UtilityBasedAgent("Utilidade", ambiente, pos_inicial_x, pos_inicial_y, grid, obstacles)
    agente_bdi = AgenteBDI("BDI", ambiente, pos_inicial_x, pos_inicial_y, grid, obstacles)
    
    # Lista de todos os agentes
    agentes = [ agente_bdi]
    
    # Configurações da simulação
    rodando = True
    passos = 0
    TEMPO_SIMULACAO = 120  # segundos
    
    print("Iniciando simulação...")
    print(f"Agentes: {[agente.nome for agente in agentes]}")
    print(f"Obstáculos: {obstacles}")
    print(f"Sujeiras totais: {sum(sum(linha) for linha in grid)}")
    
    while rodando and passos < constantes.FPS * TEMPO_SIMULACAO:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
        
        # Executa um passo da simulação
        ambiente.step()
        
        # Desenha ambiente
        desenhar_ambiente(tela, grid, obstacles, agentes)
        
        # Verifica se todos os agentes pararam (bateria zerada)
        agentes_ativos = [agente for agente in agentes if agente.executando and agente.bateria > 0]
        if not agentes_ativos:
            print("Todos os agentes ficaram sem bateria!")
            rodando = False
        
        pygame.display.update()
        passos += 1
        relogio.tick(constantes.FPS)
    
    # Tela de resultados
    mostrar_tela_resultado(tela, agentes)
    
    pygame.quit()

if __name__ == "__main__":
    # Configurações constantes (adicione ao arquivo constantes.py)
    constantes.WINDOW_WIDTH = 800
    constantes.WINDOW_HEIGHT = 600
    constantes.CELL_SIZE = 80
    constantes.FPS = 2  # Mais lento para visualização
    
    # Cores dos agentes
    constantes.BLUE = (0, 0, 255)
    constantes.GREEN = (0, 255, 0)
    constantes.ORANGE = (255, 165, 0)
    constantes.PURPLE = (128, 0, 128)
    
    main()