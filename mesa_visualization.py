"""
Visualização gráfica usando Mesa para o ambiente do robô aspirador
"""

import mesa
import mesa.visualization
from mesa_environment import AmbienteAspirador, TipoSujeira, TipoCelula, Aspirador

def cell_portrayal(cell):
    """Define como cada célula será representada visualmente"""
    if cell is None:
        return None
    
    if isinstance(cell, Aspirador):
        return {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 1,
            "Color": "red",
            "r": 0.8,
            "text": "🤖",
            "text_color": "black"
        }
    
    # Célula do ambiente
    portrayal = {
        "Shape": "rect",
        "Filled": "true",
        "Layer": 0,
        "w": 0.9,
        "h": 0.9,
    }
    
    if cell.tipo_celula == TipoCelula.OBSTACULO:
        portrayal["Color"] = "black"
        portrayal["text"] = "█"
        portrayal["text_color"] = "white"
    else:
        # Célula vazia com sujeira
        if cell.tipo_sujeira == TipoSujeira.LIMPO:
            portrayal["Color"] = "white"
            portrayal["text"] = "·"
            portrayal["text_color"] = "gray"
        elif cell.tipo_sujeira == TipoSujeira.POEIRA:
            portrayal["Color"] = "lightgray"
            portrayal["text"] = "·"
            portrayal["text_color"] = "black"
        elif cell.tipo_sujeira == TipoSujeira.LIQUIDO:
            portrayal["Color"] = "lightblue"
            portrayal["text"] = "~"
            portrayal["text_color"] = "blue"
        elif cell.tipo_sujeira == TipoSujeira.DETRITOS:
            portrayal["Color"] = "brown"
            portrayal["text"] = "♦"
            portrayal["text_color"] = "black"
    
    return portrayal

def create_visualization():
    """Cria a visualização Mesa"""
    grid = mesa.visualization.CanvasGrid(
        cell_portrayal, 
        5, 5, 400, 400
    )
    
    # Elementos da interface
    chart = mesa.visualization.ChartModule([
        {"Label": "Pontos_Coletados", "Color": "green"},
        {"Label": "Percentual_Limpo", "Color": "blue"},
        {"Label": "Bateria_Atual", "Color": "red"},
    ])
    
    # Informações do agente
    agent_info = mesa.visualization.TextElement(
        lambda model: f"""
        <b>Informações do Agente:</b><br>
        Tipo: {model.tipo_agente.title()}<br>
        Bateria: {model._calcular_bateria_atual()}/30<br>
        Pontos: {model._calcular_pontos_coletados()}<br>
        Limpeza: {model._calcular_percentual_limpo():.1f}%<br>
        Ações: {model._calcular_total_acoes()}<br>
        """,
        display_width=200,
        display_height=150
    )
    
    # Legenda
    legend = mesa.visualization.TextElement(
        """
        <b>Legenda:</b><br>
        🤖 = Aspirador<br>
        █ = Obstáculo<br>
        · = Limpo/Poeira<br>
        ~ = Líquido<br>
        ♦ = Detritos<br>
        """,
        display_width=200,
        display_height=150
    )
    
    # Servidor de visualização
    server = mesa.visualization.ModularServer(
        AmbienteAspirador,
        [grid, agent_info, legend, chart],
        "Robô Aspirador Inteligente",
        {
            "width": 5,
            "height": 5,
            "tipo_agente": "reativo",
            "seed": 42
        }
    )
    
    return server

def run_simulation(tipo_agente="reativo", seed=42, max_steps=200):
    """Executa uma simulação específica"""
    model = AmbienteAspirador(
        width=5, 
        height=5, 
        tipo_agente=tipo_agente, 
        seed=seed
    )
    
    print(f"Executando simulação com {tipo_agente}")
    print(f"Seed: {seed}")
    print("-" * 50)
    
    for step in range(max_steps):
        model.step()
        
        # Verificar condições de parada
        aspirador = None
        for agent in model.schedule.agents:
            if isinstance(agent, Aspirador):
                aspirador = agent
                break
        
        if aspirador and (aspirador.bateria <= 0 or model._calcular_percentual_limpo() >= 95):
            print(f"Simulação finalizada no passo {step + 1}")
            break
        
        # Mostrar progresso a cada 20 passos
        if (step + 1) % 20 == 0:
            print(f"Passo {step + 1}: Bateria={aspirador.bateria}, "
                  f"Pontos={aspirador.pontos_coletados}, "
                  f"Limpeza={model._calcular_percentual_limpo():.1f}%")
    
    # Resultados finais
    print("\n" + "=" * 50)
    print("RESULTADOS FINAIS:")
    print("=" * 50)
    print(f"Tipo de Agente: {tipo_agente.title()}")
    print(f"Passos executados: {step + 1}")
    print(f"Pontos coletados: {aspirador.pontos_coletados}")
    print(f"Bateria restante: {aspirador.bateria}/30")
    print(f"Percentual limpo: {model._calcular_percentual_limpo():.1f}%")
    print(f"Total de ações: {aspirador.estatisticas['total_acoes']}")
    print(f"Eficiência energética: {aspirador.pontos_coletados/max(aspirador.estatisticas['energia_gasta'], 1):.3f}")
    print(f"Movimentos inválidos: {aspirador.estatisticas['movimentos_invalidos']}")
    
    return {
        'tipo_agente': tipo_agente,
        'passos': step + 1,
        'pontos_coletados': aspirador.pontos_coletados,
        'bateria_restante': aspirador.bateria,
        'percentual_limpo': model._calcular_percentual_limpo(),
        'total_acoes': aspirador.estatisticas['total_acoes'],
        'eficiencia_energetica': aspirador.pontos_coletados/max(aspirador.estatisticas['energia_gasta'], 1),
        'movimentos_invalidos': aspirador.estatisticas['movimentos_invalidos']
    }

def compare_agents(num_tests=5):
    """Compara diferentes tipos de agentes"""
    tipos_agentes = ["reativo", "modelo", "objetivos", "utilidade", "bdi"]
    resultados = {}
    
    print("COMPARAÇÃO DE AGENTES")
    print("=" * 60)
    
    for tipo in tipos_agentes:
        print(f"\nTestando Agente {tipo.title()}...")
        resultados_tipo = []
        
        for test in range(num_tests):
            seed = 42 + test
            resultado = run_simulation(tipo, seed, max_steps=100)
            resultados_tipo.append(resultado)
        
        # Calcular médias
        resultados[tipo] = {
            'pontos_medio': sum(r['pontos_coletados'] for r in resultados_tipo) / num_tests,
            'eficiencia_media': sum(r['eficiencia_energetica'] for r in resultados_tipo) / num_tests,
            'limpeza_media': sum(r['percentual_limpo'] for r in resultados_tipo) / num_tests,
            'passos_medio': sum(r['passos'] for r in resultados_tipo) / num_tests,
            'resultados': resultados_tipo
        }
    
    # Mostrar ranking
    print("\n" + "=" * 60)
    print("RANKING POR PONTOS COLETADOS:")
    print("-" * 40)
    ranking_pontos = sorted(resultados.items(), key=lambda x: x[1]['pontos_medio'], reverse=True)
    for i, (tipo, dados) in enumerate(ranking_pontos, 1):
        print(f"{i}º - {tipo.title()}: {dados['pontos_medio']:.2f} pontos")
    
    print("\nRANKING POR EFICIÊNCIA ENERGÉTICA:")
    print("-" * 40)
    ranking_eficiencia = sorted(resultados.items(), key=lambda x: x[1]['eficiencia_media'], reverse=True)
    for i, (tipo, dados) in enumerate(ranking_eficiencia, 1):
        print(f"{i}º - {tipo.title()}: {dados['eficiencia_media']:.3f} pontos/energia")
    
    print("\nRANKING POR PERCENTUAL DE LIMPEZA:")
    print("-" * 40)
    ranking_limpeza = sorted(resultados.items(), key=lambda x: x[1]['limpeza_media'], reverse=True)
    for i, (tipo, dados) in enumerate(ranking_limpeza, 1):
        print(f"{i}º - {tipo.title()}: {dados['limpeza_media']:.1f}%")
    
    return resultados

def launch_visualization():
    """Inicia a visualização interativa"""
    server = create_visualization()
    print("Iniciando visualização Mesa...")
    print("Acesse: http://127.0.0.1:8521")
    server.launch()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "visualize":
            launch_visualization()
        elif command == "compare":
            num_tests = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            compare_agents(num_tests)
        elif command == "test":
            tipo = sys.argv[2] if len(sys.argv) > 2 else "reativo"
            seed = int(sys.argv[3]) if len(sys.argv) > 3 else 42
            run_simulation(tipo, seed)
        else:
            print("Comandos disponíveis:")
            print("  python mesa_visualization.py visualize")
            print("  python mesa_visualization.py compare [num_tests]")
            print("  python mesa_visualization.py test [tipo] [seed]")
    else:
        print("Usando modo padrão: comparação rápida")
        compare_agents(3)
