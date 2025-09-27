"""
Sistema de simulação para comparar diferentes tipos de agentes racionais
"""

import time
import random
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import pandas as pd
from environment import Environment
from agent_base import AgenteReativoSimples, AgenteBaseadoModelo
from agents import AgenteBaseadoObjetivos, AgenteBaseadoUtilidade, AgenteBDI

class SimuladorAgentes:
    """Simulador para testar e comparar diferentes agentes"""
    
    def __init__(self, num_simulacoes: int = 10, seed_base: int = 42):
        self.num_simulacoes = num_simulacoes
        self.seed_base = seed_base
        self.resultados = []
        self.agentes = [
            AgenteReativoSimples(),
            AgenteBaseadoModelo(),
            AgenteBaseadoObjetivos(),
            AgenteBaseadoUtilidade(),
            AgenteBDI()
        ]
    
    def executar_simulacao(self, agente_index: int, seed: int) -> Dict:
        """Executa uma simulação completa com um agente específico"""
        # Criar ambiente com seed específico
        ambiente = Environment(seed=seed)
        agente = self.agentes[agente_index]
        
        # Reset do agente
        agente.reset()
        
        # Contadores para análise
        ciclos = 0
        max_ciclos = 200  # Limite de segurança
        
        # Executar simulação
        while ciclos < max_ciclos:
            continuar = agente.executar_ciclo(ambiente)
            ciclos += 1
            
            if not continuar:
                break
        
        # Coletar resultados
        stats_ambiente = ambiente.obter_estatisticas()
        stats_agente = agente.obter_estatisticas()
        
        resultado = {
            'agente': agente.nome,
            'seed': seed,
            'ciclos_executados': ciclos,
            'pontos_coletados': stats_agente['pontos_coletados'],
            'energia_gasta': stats_agente['energia_gasta'],
            'eficiencia_energetica': stats_agente['pontos_por_energia'],
            'percentual_limpo': stats_ambiente['percentual_limpo'],
            'movimentos_invalidos': stats_agente['movimentos_invalidos'],
            'eficiencia_movimento': stats_agente['eficiencia_movimento'],
            'total_acoes': stats_agente['total_acoes'],
            'acoes_movimento': stats_agente['acoes_movimento'],
            'acoes_aspirar': stats_agente['acoes_aspirar'],
            'ambiente_limpo': stats_ambiente['percentual_limpo'] >= 95.0,
            'bateria_esgotada': ambiente.bateria_esgotada()
        }
        
        return resultado
    
    def executar_todas_simulacoes(self) -> List[Dict]:
        """Executa todas as simulações para todos os agentes"""
        print("Iniciando simulações...")
        self.resultados = []
        
        for i, agente in enumerate(self.agentes):
            print(f"\nTestando {agente.nome}...")
            
            for simulacao in range(self.num_simulacoes):
                seed = self.seed_base + simulacao
                resultado = self.executar_simulacao(i, seed)
                self.resultados.append(resultado)
                
                # Progress indicator
                if (simulacao + 1) % 5 == 0:
                    print(f"  Simulação {simulacao + 1}/{self.num_simulacoes} concluída")
        
        print(f"\nTotal de {len(self.resultados)} simulações concluídas!")
        return self.resultados
    
    def analisar_resultados(self) -> Dict:
        """Analisa os resultados das simulações"""
        if not self.resultados:
            self.executar_todas_simulacoes()
        
        df = pd.DataFrame(self.resultados)
        
        # Análise por agente
        analise = {}
        
        for agente in df['agente'].unique():
            dados_agente = df[df['agente'] == agente]
            
            analise[agente] = {
                'pontos_medio': dados_agente['pontos_coletados'].mean(),
                'pontos_desvio': dados_agente['pontos_coletados'].std(),
                'eficiencia_energetica_media': dados_agente['eficiencia_energetica'].mean(),
                'percentual_limpo_medio': dados_agente['percentual_limpo'].mean(),
                'ciclos_medio': dados_agente['ciclos_executados'].mean(),
                'movimentos_invalidos_medio': dados_agente['movimentos_invalidos'].mean(),
                'taxa_sucesso': (dados_agente['ambiente_limpo'] == True).mean(),
                'energia_gasta_media': dados_agente['energia_gasta'].mean()
            }
        
        return analise
    
    def gerar_relatorio(self) -> str:
        """Gera um relatório textual dos resultados"""
        analise = self.analisar_resultados()
        
        relatorio = "=" * 80 + "\n"
        relatorio += "RELATÓRIO DE COMPARAÇÃO DE AGENTES RACIONAIS\n"
        relatorio += "=" * 80 + "\n\n"
        
        relatorio += f"Número de simulações por agente: {self.num_simulacoes}\n"
        relatorio += f"Total de simulações: {len(self.resultados)}\n\n"
        
        # Ranking por diferentes métricas
        df = pd.DataFrame(self.resultados)
        
        relatorio += "RANKING POR PONTOS COLETADOS:\n"
        relatorio += "-" * 40 + "\n"
        ranking_pontos = df.groupby('agente')['pontos_coletados'].mean().sort_values(ascending=False)
        for i, (agente, pontos) in enumerate(ranking_pontos.items(), 1):
            relatorio += f"{i}º - {agente}: {pontos:.2f} pontos\n"
        
        relatorio += "\nRANKING POR EFICIÊNCIA ENERGÉTICA:\n"
        relatorio += "-" * 40 + "\n"
        ranking_eficiencia = df.groupby('agente')['eficiencia_energetica'].mean().sort_values(ascending=False)
        for i, (agente, eficiencia) in enumerate(ranking_eficiencia.items(), 1):
            relatorio += f"{i}º - {agente}: {eficiencia:.3f} pontos/energia\n"
        
        relatorio += "\nRANKING POR PERCENTUAL DE LIMPEZA:\n"
        relatorio += "-" * 40 + "\n"
        ranking_limpeza = df.groupby('agente')['percentual_limpo'].mean().sort_values(ascending=False)
        for i, (agente, limpeza) in enumerate(ranking_limpeza.items(), 1):
            relatorio += f"{i}º - {agente}: {limpeza:.1f}%\n"
        
        relatorio += "\nRANKING POR TAXA DE SUCESSO (Ambiente >95% limpo):\n"
        relatorio += "-" * 40 + "\n"
        taxa_sucesso = df.groupby('agente')['ambiente_limpo'].mean().sort_values(ascending=False)
        for i, (agente, taxa) in enumerate(taxa_sucesso.items(), 1):
            relatorio += f"{i}º - {agente}: {taxa*100:.1f}%\n"
        
        # Análise detalhada por agente
        relatorio += "\n" + "=" * 80 + "\n"
        relatorio += "ANÁLISE DETALHADA POR AGENTE\n"
        relatorio += "=" * 80 + "\n\n"
        
        for agente, dados in analise.items():
            relatorio += f"AGENTE: {agente}\n"
            relatorio += "-" * 50 + "\n"
            relatorio += f"Pontos coletados (média ± desvio): {dados['pontos_medio']:.2f} ± {dados['pontos_desvio']:.2f}\n"
            relatorio += f"Eficiência energética: {dados['eficiencia_energetica_media']:.3f} pontos/energia\n"
            relatorio += f"Percentual de limpeza: {dados['percentual_limpo_medio']:.1f}%\n"
            relatorio += f"Ciclos executados: {dados['ciclos_medio']:.1f}\n"
            relatorio += f"Movimentos inválidos: {dados['movimentos_invalidos_medio']:.1f}\n"
            relatorio += f"Taxa de sucesso: {dados['taxa_sucesso']*100:.1f}%\n"
            relatorio += f"Energia gasta: {dados['energia_gasta_media']:.1f}\n\n"
        
        # Conclusões
        relatorio += "=" * 80 + "\n"
        relatorio += "CONCLUSÕES\n"
        relatorio += "=" * 80 + "\n\n"
        
        melhor_pontos = ranking_pontos.index[0]
        melhor_eficiencia = ranking_eficiencia.index[0]
        melhor_limpeza = ranking_limpeza.index[0]
        melhor_sucesso = taxa_sucesso.index[0]
        
        relatorio += f"• Melhor em pontos coletados: {melhor_pontos}\n"
        relatorio += f"• Melhor em eficiência energética: {melhor_eficiencia}\n"
        relatorio += f"• Melhor em limpeza geral: {melhor_limpeza}\n"
        relatorio += f"• Melhor em taxa de sucesso: {melhor_sucesso}\n\n"
        
        relatorio += "CARACTERÍSTICAS DOS AGENTES:\n"
        relatorio += "• Agente Reativo Simples: Reage diretamente às percepções\n"
        relatorio += "• Agente Baseado em Modelo: Mantém modelo interno do ambiente\n"
        relatorio += "• Agente Baseado em Objetivos: Planeja para alcançar objetivos\n"
        relatorio += "• Agente Baseado em Utilidade: Maximiza utilidade custo-benefício\n"
        relatorio += "• Agente BDI: Arquitetura cognitiva com crenças, desejos e intenções\n"
        
        return relatorio
    
    def gerar_graficos(self):
        """Gera gráficos comparativos dos resultados"""
        if not self.resultados:
            self.executar_todas_simulacoes()
        
        df = pd.DataFrame(self.resultados)
        
        # Configurar subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Comparação de Performance dos Agentes Racionais', fontsize=16)
        
        # Gráfico 1: Pontos coletados
        df.boxplot(column='pontos_coletados', by='agente', ax=axes[0,0])
        axes[0,0].set_title('Pontos Coletados por Agente')
        axes[0,0].set_xlabel('Agente')
        axes[0,0].set_ylabel('Pontos')
        
        # Gráfico 2: Eficiência energética
        df.boxplot(column='eficiencia_energetica', by='agente', ax=axes[0,1])
        axes[0,1].set_title('Eficiência Energética por Agente')
        axes[0,1].set_xlabel('Agente')
        axes[0,1].set_ylabel('Pontos/Energia')
        
        # Gráfico 3: Percentual de limpeza
        df.boxplot(column='percentual_limpo', by='agente', ax=axes[1,0])
        axes[1,0].set_title('Percentual de Limpeza por Agente')
        axes[1,0].set_xlabel('Agente')
        axes[1,0].set_ylabel('% Limpo')
        
        # Gráfico 4: Taxa de sucesso
        taxa_sucesso = df.groupby('agente')['ambiente_limpo'].mean() * 100
        taxa_sucesso.plot(kind='bar', ax=axes[1,1], color='skyblue')
        axes[1,1].set_title('Taxa de Sucesso por Agente')
        axes[1,1].set_xlabel('Agente')
        axes[1,1].set_ylabel('% Sucesso')
        axes[1,1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('comparacao_agentes.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return fig
    
    def demonstrar_agente_individual(self, agente_index: int, seed: int = 42, mostrar_passos: bool = True):
        """Demonstra o comportamento de um agente específico"""
        ambiente = Environment(seed=seed)
        agente = self.agentes[agente_index]
        
        print(f"\nDemonstração do {agente.nome}")
        print("=" * 50)
        print("Estado inicial:")
        ambiente.imprimir_grid()
        
        if mostrar_passos:
            input("Pressione Enter para continuar...")
        
        ciclos = 0
        max_ciclos = 50
        
        while ciclos < max_ciclos:
            if mostrar_passos:
                print(f"\nCiclo {ciclos + 1}:")
            
            continuar = agente.executar_ciclo(ambiente)
            
            if mostrar_passos:
                ambiente.imprimir_grid()
                input("Pressione Enter para próximo ciclo...")
            
            ciclos += 1
            
            if not continuar:
                break
        
        # Resultado final
        print(f"\nSimulação finalizada após {ciclos} ciclos")
        stats_agente = agente.obter_estatisticas()
        stats_ambiente = ambiente.obter_estatisticas()
        
        print(f"\nResultados do {agente.nome}:")
        print(f"Pontos coletados: {stats_agente['pontos_coletados']}")
        print(f"Energia gasta: {stats_agente['energia_gasta']}")
        print(f"Eficiência energética: {stats_agente['pontos_por_energia']:.3f}")
        print(f"Percentual de limpeza: {stats_ambiente['percentual_limpo']:.1f}%")
        print(f"Movimentos inválidos: {stats_agente['movimentos_invalidos']}")
        
        return {
            'agente': agente.nome,
            'ciclos': ciclos,
            'stats_agente': stats_agente,
            'stats_ambiente': stats_ambiente
        }
