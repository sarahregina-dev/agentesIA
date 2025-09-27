"""
Programa principal para executar simulações e comparações de agentes racionais
Robô Aspirador Inteligente - Comparação de Arquiteturas de Agentes
"""

import sys
import os
from simulador import SimuladorAgentes

def menu_principal():
    """Menu principal do programa"""
    print("=" * 80)
    print("ROBÔ ASPIRADOR INTELIGENTE - COMPARAÇÃO DE AGENTES RACIONAIS")
    print("=" * 80)
    print()
    print("1. Executar simulação completa (todos os agentes)")
    print("2. Demonstrar agente individual")
    print("3. Gerar relatório de resultados")
    print("4. Gerar gráficos comparativos")
    print("5. Executar simulação rápida (5 testes)")
    print("6. Sair")
    print()
    
    try:
        opcao = int(input("Escolha uma opção (1-6): "))
        return opcao
    except ValueError:
        print("Opção inválida!")
        return 0

def demonstrar_agente_individual(simulador):
    """Menu para demonstrar agente individual"""
    print("\n" + "=" * 50)
    print("DEMONSTRAÇÃO DE AGENTE INDIVIDUAL")
    print("=" * 50)
    print()
    print("Agentes disponíveis:")
    print("1. Agente Reativo Simples")
    print("2. Agente Baseado em Modelo")
    print("3. Agente Baseado em Objetivos")
    print("4. Agente Baseado em Utilidade")
    print("5. Agente BDI")
    print("6. Voltar ao menu principal")
    print()
    
    try:
        opcao_agente = int(input("Escolha um agente (1-6): "))
        if opcao_agente == 6:
            return
        
        if 1 <= opcao_agente <= 5:
            print("\nOpções de demonstração:")
            print("1. Demonstração passo a passo")
            print("2. Execução rápida")
            print()
            
            modo = int(input("Escolha o modo (1-2): "))
            mostrar_passos = (modo == 1)
            
            seed = input("Digite o seed do ambiente (ou Enter para usar 42): ").strip()
            if seed:
                try:
                    seed = int(seed)
                except ValueError:
                    seed = 42
            else:
                seed = 42
            
            print(f"\nDemonstrando {simulador.agentes[opcao_agente - 1].nome}...")
            simulador.demonstrar_agente_individual(opcao_agente - 1, seed, mostrar_passos)
        else:
            print("Opção inválida!")
    except ValueError:
        print("Opção inválida!")

def executar_simulacao_completa(simulador):
    """Executa simulação completa com todos os agentes"""
    print("\n" + "=" * 50)
    print("SIMULAÇÃO COMPLETA")
    print("=" * 50)
    print()
    
    try:
        num_simulacoes = int(input("Número de simulações por agente (padrão: 10): ") or "10")
        if num_simulacoes < 1:
            num_simulacoes = 10
    except ValueError:
        num_simulacoes = 10
    
    print(f"\nExecutando {num_simulacoes} simulações para cada agente...")
    print("Isso pode levar alguns minutos...")
    
    # Atualizar número de simulações
    simulador.num_simulacoes = num_simulacoes
    
    # Executar simulações
    simulador.executar_todas_simulacoes()
    
    # Gerar relatório
    print("\nGerando relatório...")
    relatorio = simulador.gerar_relatorio()
    
    # Salvar relatório
    with open('relatorio_resultados.txt', 'w', encoding='utf-8') as f:
        f.write(relatorio)
    
    print("\nRelatório salvo em 'relatorio_resultados.txt'")
    print("\nResultados resumidos:")
    print("-" * 40)
    
    # Mostrar ranking resumido
    import pandas as pd
    df = pd.DataFrame(simulador.resultados)
    
    print("RANKING POR PONTOS COLETADOS:")
    ranking_pontos = df.groupby('agente')['pontos_coletados'].mean().sort_values(ascending=False)
    for i, (agente, pontos) in enumerate(ranking_pontos.items(), 1):
        print(f"{i}º - {agente}: {pontos:.2f} pontos")
    
    print("\nRANKING POR EFICIÊNCIA ENERGÉTICA:")
    ranking_eficiencia = df.groupby('agente')['eficiencia_energetica'].mean().sort_values(ascending=False)
    for i, (agente, eficiencia) in enumerate(ranking_eficiencia.items(), 1):
        print(f"{i}º - {agente}: {eficiencia:.3f} pontos/energia")

def gerar_graficos(simulador):
    """Gera gráficos comparativos"""
    print("\n" + "=" * 50)
    print("GERANDO GRÁFICOS COMPARATIVOS")
    print("=" * 50)
    
    if not simulador.resultados:
        print("Nenhum resultado disponível. Execute uma simulação primeiro.")
        return
    
    print("Gerando gráficos...")
    try:
        simulador.gerar_graficos()
        print("Gráficos salvos como 'comparacao_agentes.png'")
    except ImportError:
        print("Erro: matplotlib não está instalado.")
        print("Instale com: pip install matplotlib")
    except Exception as e:
        print(f"Erro ao gerar gráficos: {e}")

def main():
    """Função principal"""
    print("Inicializando simulador...")
    simulador = SimuladorAgentes()
    
    while True:
        try:
            opcao = menu_principal()
            
            if opcao == 1:
                executar_simulacao_completa(simulador)
            elif opcao == 2:
                demonstrar_agente_individual(simulador)
            elif opcao == 3:
                if simulador.resultados:
                    relatorio = simulador.gerar_relatorio()
                    print(relatorio)
                    
                    salvar = input("\nSalvar relatório em arquivo? (s/n): ").lower()
                    if salvar == 's':
                        with open('relatorio_resultados.txt', 'w', encoding='utf-8') as f:
                            f.write(relatorio)
                        print("Relatório salvo em 'relatorio_resultados.txt'")
                else:
                    print("Nenhum resultado disponível. Execute uma simulação primeiro.")
            elif opcao == 4:
                gerar_graficos(simulador)
            elif opcao == 5:
                print("\nExecutando simulação rápida...")
                simulador.num_simulacoes = 5
                simulador.executar_todas_simulacoes()
                relatorio = simulador.gerar_relatorio()
                print(relatorio)
            elif opcao == 6:
                print("Encerrando programa...")
                break
            else:
                print("Opção inválida!")
            
            if opcao != 6:
                input("\nPressione Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n\nPrograma interrompido pelo usuário.")
            break
        except Exception as e:
            print(f"\nErro inesperado: {e}")
            input("Pressione Enter para continuar...")

if __name__ == "__main__":
    main()
