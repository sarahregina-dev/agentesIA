import pygame
import random
import simpy
import constantes
from datetime import datetime

from agents.simple_agent import SimpleAgent
from agents.model_based_agent import ModelBasedAgent
from agents.goal_based_agent import GoalBasedAgent
from agents.utility_based_agent import UtilityBasedAgent
from agents.agente_bdi import AgenteBDI

# Histórico global de simulações
historico_simulacoes = []

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
                grid[y][x] = -1
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

def mostrar_tela_selecao_agente(tela):
    """Tela de seleção de agente"""
    fonte_titulo = pygame.font.SysFont("times", 32)
    fonte_botao = pygame.font.SysFont("arial", 18)
    fonte_info = pygame.font.SysFont("arial", 14)
    
    titulo = fonte_titulo.render("Selecione o Agente para Simulação", True, (255, 255, 255))
    
    # Botões dos agentes
    agentes_info = [
        {"nome": "Reativo Simples", "letra": "S", "cor": (0, 0, 255), "classe": "SimpleAgent"},
        {"nome": "Baseado em Modelo", "letra": "M", "cor": (0, 255, 0), "classe": "ModelBasedAgent"},
        {"nome": "Baseado em Objetivos", "letra": "G", "cor": (255, 165, 0), "classe": "GoalBasedAgent"},
        {"nome": "Baseado em Utilidade", "letra": "U", "cor": (128, 0, 128), "classe": "UtilityBasedAgent"},
        {"nome": "BDI", "letra": "B", "cor": (255, 0, 255), "classe": "AgenteBDI"},
        {"nome": "TODOS", "letra": "ALL", "cor": (255, 255, 255), "classe": "Todos"}
    ]
    
    botoes = []
    y_inicio = 120
    for i, agente in enumerate(agentes_info):
        rect = pygame.Rect(constantes.WINDOW_WIDTH // 2 - 200, y_inicio + i * 70, 400, 55)
        botoes.append((rect, agente))
    
    selecionado = None
    while selecionado is None:
        tela.fill((50, 50, 80))
        
        # Título
        tela.blit(titulo, (constantes.WINDOW_WIDTH // 2 - titulo.get_width() // 2, 40))
        
        # Botões dos agentes
        mouse_pos = pygame.mouse.get_pos()
        for rect, agente in botoes:
            # Destaque se o mouse estiver sobre o botão
            cor_botao = (90, 140, 190) if rect.collidepoint(mouse_pos) else (70, 130, 180)
            pygame.draw.rect(tela, cor_botao, rect, border_radius=10)
            
            # Desenha círculo com cor do agente
            pygame.draw.circle(tela, agente["cor"], (rect.x + 30, rect.centery), 15)
            pygame.draw.circle(tela, (0, 0, 0), (rect.x + 30, rect.centery), 15, 2)
            
            # Letra do agente
            fonte_letra = pygame.font.SysFont("arial", 12, bold=True)
            texto_letra = fonte_letra.render(agente["letra"], True, (255, 255, 255))
            tela.blit(texto_letra, (rect.x + 30 - texto_letra.get_width()//2, rect.centery - texto_letra.get_height()//2))
            
            # Nome do agente
            texto = fonte_botao.render(agente["nome"], True, (255, 255, 255))
            tela.blit(texto, (rect.x + 60, rect.centery - texto.get_height() // 2))
        
        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                for rect, agente in botoes:
                    if rect.collidepoint(evento.pos):
                        selecionado = agente["classe"]
                        break
    
    return selecionado

def mostrar_historico(tela):
    """Mostra o histórico de todas as simulações"""
    fonte_titulo = pygame.font.SysFont("arial", 32, bold=True)
    fonte_texto = pygame.font.SysFont("arial", 18)
    fonte_botao = pygame.font.SysFont("arial", 20)
    
    botao_voltar = pygame.Rect(constantes.WINDOW_WIDTH // 2 - 100, constantes.WINDOW_HEIGHT - 80, 200, 50)
    botao_limpar = pygame.Rect(20, constantes.WINDOW_HEIGHT - 80, 150, 50)
    
    scroll_offset = 0
    max_scroll = 0
    
    esperando = True
    while esperando:
        tela.fill((40, 40, 60))
        
        # Título
        titulo = fonte_titulo.render(f"Histórico de Simulações ({len(historico_simulacoes)} total)", True, (255, 255, 255))
        tela.blit(titulo, (constantes.WINDOW_WIDTH // 2 - titulo.get_width() // 2, 20))
        
        if not historico_simulacoes:
            texto = fonte_texto.render("Nenhuma simulação realizada ainda", True, (200, 200, 200))
            tela.blit(texto, (constantes.WINDOW_WIDTH // 2 - texto.get_width() // 2, 200))
        else:
            # Área de scroll
            y_pos = 70 - scroll_offset
            
            # Calcula estatísticas gerais
            stats_por_agente = {}
            for sim in historico_simulacoes:
                for resultado in sim['resultados']:
                    nome = resultado['nome']
                    if nome not in stats_por_agente:
                        stats_por_agente[nome] = {'total_pontos': 0, 'simulacoes': 0}
                    stats_por_agente[nome]['total_pontos'] += resultado['pontuacao']
                    stats_por_agente[nome]['simulacoes'] += 1
                    
            
            # Mostra estatísticas gerais
            fonte_secao = pygame.font.SysFont("arial", 20, bold=True)
            texto = fonte_secao.render("=== ESTATÍSTICAS GERAIS ===", True, (255, 255, 100))
            tela.blit(texto, (30, y_pos))
            y_pos += 35
            
            for nome, stats in sorted(stats_por_agente.items(), key=lambda x: x[1]['total_pontos'], reverse=True):
                media = stats['total_pontos'] / stats['simulacoes']
            
                texto = fonte_texto.render(
                    f"{nome}: {stats['simulacoes']} simulações | Média: {media:.1f} pts",
                    True, (200, 255, 200)
                )
                tela.blit(texto, (50, y_pos))
                y_pos += 28
            
            y_pos += 25
            
            # Lista simulações individuais
            texto = fonte_secao.render("=== SIMULAÇÕES INDIVIDUAIS ===", True, (255, 255, 100))
            tela.blit(texto, (30, y_pos))
            y_pos += 35
            
            for i, sim in enumerate(reversed(historico_simulacoes)):
                # Cabeçalho da simulação
                pygame.draw.rect(tela, (60, 60, 90), (20, y_pos, 760, 35))
                fonte_sim = pygame.font.SysFont("arial", 17, bold=True)
                texto = fonte_sim.render(
                    f"Simulação #{len(historico_simulacoes) - i} - {sim['timestamp']}",
                    True, (255, 255, 255)
                )
                tela.blit(texto, (30, y_pos + 8))
                y_pos += 40
                
                # Resultados dos agentes
                for resultado in sim['resultados']:
                    cor = (200, 200, 200)
                    simbolo = "   "
                    texto = fonte_texto.render(
                        f"{simbolo}{resultado['nome']}: {resultado['pontuacao']} pts (Bateria: {resultado['bateria']})",
                        True, cor
                    )
                    tela.blit(texto, (50, y_pos))
                    y_pos += 26
                
                y_pos += 12
            
            max_scroll = max(0, y_pos - (constantes.WINDOW_HEIGHT - 150))
        
        # Botões
        mouse_pos = pygame.mouse.get_pos()
        
        # Botão Voltar
        cor_voltar = (90, 160, 200) if botao_voltar.collidepoint(mouse_pos) else (70, 130, 180)
        pygame.draw.rect(tela, cor_voltar, botao_voltar, border_radius=10)
        texto_voltar = fonte_botao.render("Voltar", True, (255, 255, 255))
        tela.blit(texto_voltar, (botao_voltar.centerx - texto_voltar.get_width() // 2, botao_voltar.y + 15))
        
        # Botão Limpar Histórico
        if historico_simulacoes:
            cor_limpar = (180, 60, 60) if botao_limpar.collidepoint(mouse_pos) else (150, 50, 50)
            pygame.draw.rect(tela, cor_limpar, botao_limpar, border_radius=10)
            texto_limpar = fonte_botao.render("Limpar", True, (255, 255, 255))
            tela.blit(texto_limpar, (botao_limpar.centerx - texto_limpar.get_width() // 2, botao_limpar.y + 15))
        
        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_voltar.collidepoint(evento.pos):
                    esperando = False
                elif botao_limpar.collidepoint(evento.pos) and historico_simulacoes:
                    historico_simulacoes.clear()
                    print("Histórico limpo!")
            elif evento.type == pygame.MOUSEWHEEL:
                scroll_offset -= evento.y * 20
                scroll_offset = max(0, min(scroll_offset, max_scroll))

def mostrar_tela_resultado(tela, agentes, grid_atual, obstacles_atuais):
    """Tela de resultados finais"""
    fonte_titulo = pygame.font.SysFont("arial", 32)
    fonte_resultado = pygame.font.SysFont("arial", 24)
    fonte_botao = pygame.font.SysFont("arial", 18)
    
    titulo = fonte_titulo.render("Resultados da Simulação", True, (255, 255, 255))
    
    # Botões
    botao_mesmo_mapa = pygame.Rect(50, constantes.WINDOW_HEIGHT - 100, 180, 50)
    botao_novo_mapa = pygame.Rect(250, constantes.WINDOW_HEIGHT - 100, 180, 50)
    botao_historico = pygame.Rect(450, constantes.WINDOW_HEIGHT - 100, 180, 50)
    botao_sair = pygame.Rect(650, constantes.WINDOW_HEIGHT - 100, 100, 50)
    
    texto_botao1 = fonte_botao.render("Mesmo Mapa", True, (255, 255, 255))
    texto_botao2 = fonte_botao.render("Novo Mapa", True, (255, 255, 255))
    texto_botao3 = fonte_botao.render("Histórico", True, (255, 255, 255))
    texto_botao4 = fonte_botao.render("Sair", True, (255, 255, 255))

    # Ordena agentes por pontuação
    agentes_ordenados = sorted(agentes, key=lambda a: a.pontuacao, reverse=True)
    
    esperando = True
    escolha = None
    while esperando:
        tela.fill((50, 50, 80))
        tela.blit(titulo, (constantes.WINDOW_WIDTH // 2 - titulo.get_width() // 2, 40))

        # Resultados
        for i, agente in enumerate(agentes_ordenados):
            cor = (255, 255, 0) if i == 0 else (255, 255, 255)  # Destaque para o primeiro
            simbolo = "🏆 " if i == 0 else f"{i+1}º - "
            resultado = fonte_resultado.render(
                f"{simbolo}{agente.nome}: {agente.pontuacao} pontos (Bateria: {agente.bateria})", 
                True, cor
            )
            tela.blit(resultado, (60, 100 + i * 40))
        
        # Estatísticas adicionais
        total_pontos = sum(agente.pontuacao for agente in agentes)
        stats = fonte_resultado.render(f"Total de pontos coletados: {total_pontos}", True, (200, 200, 200))
        tela.blit(stats, (60, 100 + len(agentes) * 40 + 20))

        # Botões
        mouse_pos = pygame.mouse.get_pos()
        
        # Botão "Mesmo Mapa"
        cor1 = (90, 160, 200) if botao_mesmo_mapa.collidepoint(mouse_pos) else (70, 130, 180)
        pygame.draw.rect(tela, cor1, botao_mesmo_mapa, border_radius=10)
        tela.blit(texto_botao1, (botao_mesmo_mapa.centerx - texto_botao1.get_width() // 2, 
                               botao_mesmo_mapa.y + 15))
        
        # Botão "Novo Mapa"
        cor2 = (90, 160, 200) if botao_novo_mapa.collidepoint(mouse_pos) else (70, 130, 180)
        pygame.draw.rect(tela, cor2, botao_novo_mapa, border_radius=10)
        tela.blit(texto_botao2, (botao_novo_mapa.centerx - texto_botao2.get_width() // 2, 
                               botao_novo_mapa.y + 15))
        
        # Botão "Histórico"
        cor3 = (90, 160, 200) if botao_historico.collidepoint(mouse_pos) else (70, 130, 180)
        pygame.draw.rect(tela, cor3, botao_historico, border_radius=10)
        tela.blit(texto_botao3, (botao_historico.centerx - texto_botao3.get_width() // 2, 
                               botao_historico.y + 15))
        
        # Botão "Sair"
        cor4 = (180, 60, 60) if botao_sair.collidepoint(mouse_pos) else (150, 50, 50)
        pygame.draw.rect(tela, cor4, botao_sair, border_radius=10)
        tela.blit(texto_botao4, (botao_sair.centerx - texto_botao4.get_width() // 2, 
                               botao_sair.y + 15))

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_mesmo_mapa.collidepoint(evento.pos):
                    escolha = "mesmo_mapa"
                    esperando = False
                elif botao_novo_mapa.collidepoint(evento.pos):
                    escolha = "novo_mapa"
                    esperando = False
                elif botao_historico.collidepoint(evento.pos):
                    mostrar_historico(tela)
                elif botao_sair.collidepoint(evento.pos):
                    escolha = "sair"
                    esperando = False
    
    return escolha

def parar_agente(agente):
    """Para um agente específico"""
    agente.parar()

def desenhar_ambiente(tela, grid, obstacles, agentes):
    """Desenha o ambiente completo"""
    # Fundo
    tela.fill((240, 240, 240))  # Cinza claro
    
    # Margem para centralizar o grid
    margem = 10
    
    # Grade com sombra para profundidade
    for x in range(5):
        for y in range(5):
            # Sombra
            shadow_rect = pygame.Rect(margem + x * constantes.CELL_SIZE + 2, 
                                     margem + y * constantes.CELL_SIZE + 2, 
                                     constantes.CELL_SIZE, constantes.CELL_SIZE)
            pygame.draw.rect(tela, (180, 180, 180), shadow_rect)
            
            # Célula principal
            rect = pygame.Rect(margem + x * constantes.CELL_SIZE, 
                             margem + y * constantes.CELL_SIZE, 
                             constantes.CELL_SIZE, constantes.CELL_SIZE)
            pygame.draw.rect(tela, (255, 255, 255), rect)
            pygame.draw.rect(tela, (150, 150, 150), rect, 2)
    
    # Obstáculos com degradê
    for x, y in obstacles:
        rect = pygame.Rect(margem + x * constantes.CELL_SIZE, 
                          margem + y * constantes.CELL_SIZE, 
                          constantes.CELL_SIZE, constantes.CELL_SIZE)
        pygame.draw.rect(tela, (80, 80, 80), rect)
        pygame.draw.rect(tela, (50, 50, 50), rect, 3)
    
    # Sujeiras com estilo melhorado
    fonte_sujeira = pygame.font.SysFont("arial", 16, bold=True)
    for y in range(5):
        for x in range(5):
            if grid[y][x] > 0:
                cor = {
                    1: (220, 220, 220),   # Poeira - cinza claro
                    2: (100, 150, 255),   # Líquido - azul  
                    3: (160, 82, 45)      # Detritos - marrom
                }.get(grid[y][x], (0, 0, 0))
                
                centro_x = margem + x * constantes.CELL_SIZE + constantes.CELL_SIZE // 2
                centro_y = margem + y * constantes.CELL_SIZE + constantes.CELL_SIZE // 2
                
                # Sujeira com borda
                pygame.draw.circle(tela, cor, (centro_x, centro_y), 12)
                pygame.draw.circle(tela, (0, 0, 0), (centro_x, centro_y), 12, 2)
                
                # Valor da sujeira centralizado
                texto = fonte_sujeira.render(str(grid[y][x]), True, (0, 0, 0))
                texto_x = centro_x - texto.get_width() // 2
                texto_y = centro_y - texto.get_height() // 2
                tela.blit(texto, (texto_x, texto_y))
    
    # Agentes
    for agente in agentes:
        agente.desenhar(tela, margem)
    
    # Painel de informações
    desenhar_painel_info(tela, agentes)

def desenhar_painel_info(tela, agentes):
    """Desenha painel lateral compacto e elegante"""
    # Painel lateral mais estreito
    painel_x = 5 * constantes.CELL_SIZE + 30
    painel_width = constantes.WINDOW_WIDTH - painel_x - 10
    
    # Fundo do painel com degradê simulado
    painel_rect = pygame.Rect(painel_x, 10, painel_width, constantes.WINDOW_HEIGHT - 20)
    pygame.draw.rect(tela, (45, 52, 70), painel_rect, border_radius=15)
    pygame.draw.rect(tela, (80, 90, 120), painel_rect, 3, border_radius=15)
    
    # Título estilizado
    fonte_titulo = pygame.font.SysFont("arial", 26, bold=True)
    titulo = fonte_titulo.render("STATUS", True, (255, 255, 255))
    titulo_x = painel_x + painel_width // 2 - titulo.get_width() // 2
    tela.blit(titulo, (titulo_x, 25))
    
    # Linha separadora
    pygame.draw.line(tela, (100, 110, 140), 
                     (painel_x + 15, 60), 
                     (painel_x + painel_width - 15, 60), 3)
    
    # Informações dos agentes de forma compacta
    fonte_nome = pygame.font.SysFont("arial", 18, bold=True)
    fonte_info = pygame.font.SysFont("arial", 15)
    
    y_inicial = 75
    espacamento = 105
    
    for i, agente in enumerate(agentes):
        y_pos = y_inicial + i * espacamento
        
        # Cor do agente
        cor_agente = {
            'SimpleAgent': constantes.BLUE,
            'ModelBasedAgent': constantes.GREEN, 
            'GoalBasedAgent': constantes.ORANGE,
            'UtilityBasedAgent': constantes.PURPLE,
            'AgenteBDI': (255, 0, 255)
        }.get(agente.__class__.__name__, (255, 255, 255))
        
        # Container do agente
        container_rect = pygame.Rect(painel_x + 10, y_pos - 5, painel_width - 20, 95)
        pygame.draw.rect(tela, (55, 62, 80), container_rect, border_radius=8)
        
        # Círculo colorido do agente
        circulo_x = painel_x + 32
        circulo_y = y_pos + 22
        pygame.draw.circle(tela, cor_agente, (circulo_x, circulo_y), 18)
        pygame.draw.circle(tela, (255, 255, 255), (circulo_x, circulo_y), 18, 3)
        
        # Letra do agente no círculo
        fonte_letra = pygame.font.SysFont("arial", 14, bold=True)
        letra = fonte_letra.render(agente.get_letra(), True, (255, 255, 255))
        tela.blit(letra, (circulo_x - letra.get_width()//2, circulo_y - letra.get_height()//2))
        
        # Nome do agente
        nome = fonte_nome.render(agente.nome, True, (255, 255, 255))
        tela.blit(nome, (painel_x + 58, y_pos))
        
        # Informações compactas
        info_y = y_pos + 26
        
        # Pontos
        pts_icon = "⭐"
        pts_texto = f"{pts_icon} {agente.pontuacao}"
        texto_pts = fonte_info.render(pts_texto, True, (255, 215, 0))
        tela.blit(texto_pts, (painel_x + 58, info_y))
        
        # Bateria com cor dinâmica
        bat_icon = "🔋"
        bat_cor = (0, 255, 0) if agente.bateria > 15 else (255, 100, 0) if agente.bateria > 5 else (255, 0, 0)
        bat_texto = f"{bat_icon} {agente.bateria}"
        texto_bat = fonte_info.render(bat_texto, True, bat_cor)
        tela.blit(texto_bat, (painel_x + 58, info_y + 22))
        
        # Posição
        pos_icon = "📍"
        pos_texto = f"{pos_icon} ({agente.x},{agente.y})"
        texto_pos = fonte_info.render(pos_texto, True, (200, 200, 255))
        tela.blit(texto_pos, (painel_x + 58, info_y + 44))

def copiar_grid(grid):
    """Cria uma cópia profunda do grid"""
    return [linha[:] for linha in grid]

def executar_simulacao(tela, tipo_agente, grid, obstacles):
    """Executa uma simulação com o agente selecionado"""
    relogio = pygame.time.Clock()
    ambiente = simpy.Environment()
    
    # Cria uma cópia do grid para não afetar o original
    grid_simulacao = copiar_grid(grid)
    
    # Criação dos agentes (todos começam na posição 2,2 - centro)
    pos_inicial_x, pos_inicial_y = 2, 2
    
    agentes = []
    
    if tipo_agente == "SimpleAgent":
        agentes.append(SimpleAgent("Simples", ambiente, pos_inicial_x, pos_inicial_y, grid_simulacao, obstacles))
    elif tipo_agente == "ModelBasedAgent":
        agentes.append(ModelBasedAgent("Modelo", ambiente, pos_inicial_x, pos_inicial_y, grid_simulacao, obstacles))
    elif tipo_agente == "GoalBasedAgent":
        agentes.append(GoalBasedAgent("Objetivo", ambiente, pos_inicial_x, pos_inicial_y, grid_simulacao, obstacles))
    elif tipo_agente == "UtilityBasedAgent":
        agentes.append(UtilityBasedAgent("Utilidade", ambiente, pos_inicial_x, pos_inicial_y, grid_simulacao, obstacles))
    elif tipo_agente == "AgenteBDI":
        agentes.append(AgenteBDI("BDI", ambiente, pos_inicial_x, pos_inicial_y, grid_simulacao, obstacles))
    elif tipo_agente == "Todos":
        agentes.append(SimpleAgent("Simples", ambiente, pos_inicial_x, pos_inicial_y, grid_simulacao, obstacles))
        agentes.append(ModelBasedAgent("Modelo", ambiente, pos_inicial_x, pos_inicial_y, grid_simulacao, obstacles))
        agentes.append(GoalBasedAgent("Objetivo", ambiente, pos_inicial_x, pos_inicial_y, grid_simulacao, obstacles))
        agentes.append(UtilityBasedAgent("Utilidade", ambiente, pos_inicial_x, pos_inicial_y, grid_simulacao, obstacles))
        agentes.append(AgenteBDI("BDI", ambiente, pos_inicial_x, pos_inicial_y, grid_simulacao, obstacles))
    
    # Configurações da simulação
    rodando = True
    passos = 0
    TEMPO_SIMULACAO = 120  # segundos
    DELAY_INICIAL = 2  # Segundos de pausa antes de começar
    
    print("\n" + "="*50)
    print("Iniciando simulação...")
    print(f"Agentes: {[agente.nome for agente in agentes]}")
    print(f"Obstáculos: {obstacles}")
    print(f"Sujeiras totais: {sum(sum(max(0, valor) for valor in linha) for linha in grid_simulacao)}")
    print("="*50 + "\n")
    
    # Mostra o estado inicial por alguns frames antes de começar
    for _ in range(constantes.FPS * DELAY_INICIAL):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                return None
        
        # Desenha ambiente inicial (sem executar ações)
        desenhar_ambiente(tela, grid_simulacao, obstacles, agentes)
        pygame.display.update()
        relogio.tick(constantes.FPS)
    
    while rodando and passos < constantes.FPS * TEMPO_SIMULACAO:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                return None  # Sinaliza que o usuário quer sair
        
        # Executa um passo da simulação
        ambiente.step()
        
        # Desenha ambiente
        desenhar_ambiente(tela, grid_simulacao, obstacles, agentes)
        
        # Verifica se todos os agentes pararam (bateria zerada)
        agentes_ativos = [agente for agente in agentes if agente.executando and agente.bateria > 0]
        if not agentes_ativos:
            print("Todos os agentes pararam!")
            rodando = False
        
        pygame.display.update()
        passos += 1
        relogio.tick(constantes.FPS)
    
    # Salva no histórico
    if agentes:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        pontuacao_max = max(agente.pontuacao for agente in agentes)
        
        resultados = []
        for agente in agentes:
            resultados.append({
                'nome': agente.nome,
                'pontuacao': agente.pontuacao,
                'bateria': agente.bateria,
            })
        
        historico_simulacoes.append({
            'timestamp': timestamp,
            'resultados': resultados
        })
        
        print(f"\n📊 Simulação salva no histórico ({len(historico_simulacoes)} total)")
    
    return agentes

def main():
    """Função principal da simulação"""
    pygame.init()
    tela = pygame.display.set_mode((constantes.WINDOW_WIDTH, constantes.WINDOW_HEIGHT))
    pygame.display.set_caption("Simulador - Robô Aspirador Inteligente")
    
    # Gera o primeiro ambiente
    grid_original, obstacles_original = gerar_ambiente()
    
    continuar = True
    while continuar:
        # Tela de seleção de agente
        tipo_agente = mostrar_tela_selecao_agente(tela)
        
        # Executa simulação
        agentes = executar_simulacao(tela, tipo_agente, grid_original, obstacles_original)
        
        if agentes is None:
            # Usuário fechou a janela durante a simulação
            continuar = False
        else:
            # Mostra resultados e pergunta se quer usar o mesmo mapa
            escolha = mostrar_tela_resultado(tela, agentes, grid_original, obstacles_original)
            
            if escolha == "novo_mapa":
                # Gera novo ambiente
                grid_original, obstacles_original = gerar_ambiente()
                print("\n🗺️  Novo mapa gerado!\n")
            elif escolha == "sair":
                print("\n👋 Encerrando simulador...\n")
                continuar = False
            else:
                print("\n🗺️  Usando o mesmo mapa\n")
    
    pygame.quit()

if __name__ == "__main__":
    # Configurações constantes (adicione ao arquivo constantes.py)
    constantes.WINDOW_WIDTH = 900
    constantes.WINDOW_HEIGHT = 600
    constantes.CELL_SIZE = 110
    constantes.FPS = 2  # Mais lento para visualização
    
    # Cores dos agentes
    constantes.BLUE = (0, 0, 255)
    constantes.GREEN = (0, 255, 0)
    constantes.ORANGE = (255, 165, 0)
    constantes.PURPLE = (128, 0, 128)
    
    main()