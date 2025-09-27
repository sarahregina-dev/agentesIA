"""
Programa principal atualizado para usar Mesa
Robô Aspirador Inteligente com visualização gráfica
"""

import sys
import os
from mesa_visualization import run_simulation, compare_agents, launch_visualization

def menu_principal():
    """Menu principal do programa"""
    print("=" * 80)
    print("ROBÔ ASPIRADOR INTELIGENTE - VERSÃO MESA")
    print("=" * 80)
    print()
    print("1. Visualização interativa (Mesa)")
    print("2. Testar agente individual")
    print("3. Comparar todos os agentes")
    print("4. Simulação rápida")
    print("5. Executar comparação completa")
    print("6. Sair")
    print()
    
    try:
        opcao = int(input("Escolha uma opção (1-6): "))
        return opcao
    except ValueError:
        print("Opção inválida!")
        return 0

def testar_agente_individual():
    """Testa um agente individual"""
    print("\n" + "=" * 50)
    print("TESTE DE AGENTE INDIVIDUAL")
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
        
        tipos_agentes = ["reativo", "modelo", "objetivos", "utilidade", "bdi"]
        if 1 <= opcao_agente <= 5:
            tipo = tipos_agentes[opcao_agente - 1]
            
            seed = input("Digite o seed do ambiente (ou Enter para usar 42): ").strip()
            if seed:
                try:
                    seed = int(seed)
                except ValueError:
                    seed = 42
            else:
                seed = 42
            
            max_steps = input("Número máximo de passos (ou Enter para 200): ").strip()
            if max_steps:
                try:
                    max_steps = int(max_steps)
                except ValueError:
                    max_steps = 200
            else:
                max_steps = 200
            
            print(f"\nTestando {tipo.title()}...")
            resultado = run_simulation(tipo, seed, max_steps)
            
            print("\nEstatísticas detalhadas:")
            print(f"Eficiência energética: {resultado['eficiencia_energetica']:.3f} pontos/energia")
            print(f"Taxa de sucesso: {'Sim' if resultado['percentual_limpo'] >= 95 else 'Não'}")
        else:
            print("Opção inválida!")
    except ValueError:
        print("Opção inválida!")

def comparar_agentes():
    """Compara todos os agentes"""
    print("\n" + "=" * 50)
    print("COMPARAÇÃO DE AGENTES")
    print("=" * 50)
    
    try:
        num_tests = int(input("Número de testes por agente (padrão: 5): ") or "5")
        if num_tests < 1:
            num_tests = 5
    except ValueError:
        num_tests = 5
    
    print(f"\nExecutando {num_tests} testes para cada agente...")
    print("Isso pode levar alguns minutos...")
    
    resultados = compare_agents(num_tests)
    
    # Salvar resultados em arquivo
    with open('resultados_mesa.txt', 'w', encoding='utf-8') as f:
        f.write("RESULTADOS DA COMPARAÇÃO DE AGENTES (MESA)\n")
        f.write("=" * 60 + "\n\n")
        
        for tipo, dados in resultados.items():
            f.write(f"AGENTE: {tipo.upper()}\n")
            f.write("-" * 30 + "\n")
            f.write(f"Pontos médios: {dados['pontos_medio']:.2f}\n")
            f.write(f"Eficiência energética: {dados['eficiencia_media']:.3f}\n")
            f.write(f"Percentual de limpeza: {dados['limpeza_media']:.1f}%\n")
            f.write(f"Passos médios: {dados['passos_medio']:.1f}\n\n")
    
    print(f"\nResultados salvos em 'resultados_mesa.txt'")

def simulacao_rapida():
    """Executa uma simulação rápida"""
    print("\n" + "=" * 50)
    print("SIMULAÇÃO RÁPIDA")
    print("=" * 50)
    print("Executando 3 testes para cada agente...")
    
    resultados = compare_agents(3)
    
    print("\nResumo dos resultados:")
    print("-" * 40)
    for tipo, dados in resultados.items():
        print(f"{tipo.title()}: {dados['pontos_medio']:.1f} pontos, "
              f"{dados['eficiencia_media']:.3f} eficiência, "
              f"{dados['limpeza_media']:.1f}% limpo")

def comparacao_completa():
    """Executa comparação completa com mais testes"""
    print("\n" + "=" * 50)
    print("COMPARAÇÃO COMPLETA")
    print("=" * 50)
    
    try:
        num_tests = int(input("Número de testes por agente (padrão: 10): ") or "10")
        if num_tests < 1:
            num_tests = 10
    except ValueError:
        num_tests = 10
    
    print(f"\nExecutando {num_tests} testes para cada agente...")
    print("Esta operação pode levar vários minutos...")
    
    confirmacao = input("Continuar? (s/n): ").lower()
    if confirmacao != 's':
        print("Operação cancelada.")
        return
    
    resultados = compare_agents(num_tests)
    
    # Gerar relatório detalhado
    with open('relatorio_completo_mesa.txt', 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO COMPLETO - AGENTES RACIONAIS (MESA)\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"Número de testes por agente: {num_tests}\n")
        f.write(f"Total de simulações: {num_tests * 5}\n\n")
        
        # Ranking por pontos
        f.write("RANKING POR PONTOS COLETADOS:\n")
        f.write("-" * 40 + "\n")
        ranking_pontos = sorted(resultados.items(), key=lambda x: x[1]['pontos_medio'], reverse=True)
        for i, (tipo, dados) in enumerate(ranking_pontos, 1):
            f.write(f"{i}º - {tipo.title()}: {dados['pontos_medio']:.2f} pontos\n")
        
        # Ranking por eficiência
        f.write("\nRANKING POR EFICIÊNCIA ENERGÉTICA:\n")
        f.write("-" * 40 + "\n")
        ranking_eficiencia = sorted(resultados.items(), key=lambda x: x[1]['eficiencia_media'], reverse=True)
        for i, (tipo, dados) in enumerate(ranking_eficiencia, 1):
            f.write(f"{i}º - {tipo.title()}: {dados['eficiencia_media']:.3f} pontos/energia\n")
        
        # Análise detalhada
        f.write("\n" + "=" * 70 + "\n")
        f.write("ANÁLISE DETALHADA POR AGENTE\n")
        f.write("=" * 70 + "\n\n")
        
        for tipo, dados in resultados.items():
            f.write(f"AGENTE: {tipo.upper()}\n")
            f.write("-" * 50 + "\n")
            f.write(f"Pontos coletados (média): {dados['pontos_medio']:.2f}\n")
            f.write(f"Eficiência energética: {dados['eficiencia_media']:.3f} pontos/energia\n")
            f.write(f"Percentual de limpeza: {dados['limpeza_media']:.1f}%\n")
            f.write(f"Passos executados: {dados['passos_medio']:.1f}\n")
            
            # Estatísticas dos testes individuais
            pontos_testes = [r['pontos_coletados'] for r in dados['resultados']]
            f.write(f"Pontos (min/max): {min(pontos_testes)}/{max(pontos_testes)}\n")
            f.write(f"Desvio padrão: {sum((p - dados['pontos_medio'])**2 for p in pontos_testes) / len(pontos_testes):.2f}\n\n")
    
    print(f"\nRelatório completo salvo em 'relatorio_completo_mesa.txt'")

def main():
    """Função principal"""
    print("Inicializando sistema Mesa...")
    
    while True:
        try:
            opcao = menu_principal()
            
            if opcao == 1:
                print("\nIniciando visualização Mesa...")
                print("A interface gráfica será aberta no navegador.")
                print("Pressione Ctrl+C para fechar.")
                try:
                    launch_visualization()
                except KeyboardInterrupt:
                    print("\nVisualização encerrada.")
            elif opcao == 2:
                testar_agente_individual()
            elif opcao == 3:
                comparar_agentes()
            elif opcao == 4:
                simulacao_rapida()
            elif opcao == 5:
                comparacao_completa()
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
