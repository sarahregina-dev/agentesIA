"""
Versão simplificada do ambiente Mesa sem visualização completa
Foca apenas na simulação e comparação de agentes
"""

import random
import time
from typing import Dict, List, Tuple, Optional
from enum import Enum

class TipoSujeira(Enum):
    """Tipos de sujeira com seus respectivos pontos"""
    LIMPO = 0
    POEIRA = 1
    LIQUIDO = 2
    DETRITOS = 3

class TipoCelula(Enum):
    """Tipos de células no ambiente"""
    VAZIA = "vazia"
    OBSTACULO = "obstaculo"

class Acao(Enum):
    """Ações possíveis do agente"""
    NORTE = "norte"
    SUL = "sul"
    LESTE = "leste"
    OESTE = "oeste"
    ASPIRAR = "aspirar"
    PARAR = "parar"

class AmbienteSimples:
    """Ambiente simplificado para simulação"""
    
    def __init__(self, width=5, height=5, seed=None):
        self.width = width
        self.height = height
        self.grid = {}
        self.posicao_agente = (0, 0)
        
        random.seed(seed)
        self._inicializar_ambiente()
    
    def _inicializar_ambiente(self):
        """Inicializa o ambiente com sujeira e obstáculos"""
        # Definir obstáculos fixos
        obstaculos = [(1, 1), (2, 3), (3, 1), (4, 4)]
        
        for x in range(self.width):
            for y in range(self.height):
                if (x, y) in obstaculos:
                    self.grid[(x, y)] = {
                        'tipo_celula': TipoCelula.OBSTACULO,
                        'sujeira': TipoSujeira.LIMPO,
                        'pontos': 0
                    }
                else:
                    # Gerar sujeira aleatória
                    tipo_sujeira = random.choices(
                        [TipoSujeira.LIMPO, TipoSujeira.POEIRA, TipoSujeira.LIQUIDO, TipoSujeira.DETRITOS],
                        weights=[30, 40, 20, 10]
                    )[0]
                    
                    self.grid[(x, y)] = {
                        'tipo_celula': TipoCelula.VAZIA,
                        'sujeira': tipo_sujeira,
                        'pontos': tipo_sujeira.value
                    }
    
    def _posicao_valida(self, x: int, y: int) -> bool:
        """Verifica se uma posição está dentro dos limites"""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def perceber(self) -> Dict:
        """Coleta informações do ambiente"""
        x, y = self.posicao_agente
        
        percepcao = {
            'posicao': self.posicao_agente,
            'celula_atual': self.grid.get((x, y), None),
            'vizinhos': {}
        }
        
        # Adicionar informações dos vizinhos
        direcoes = {
            'norte': (x, y - 1),
            'sul': (x, y + 1),
            'leste': (x + 1, y),
            'oeste': (x - 1, y)
        }
        
        for direcao, (nx, ny) in direcoes.items():
            if self._posicao_valida(nx, ny):
                percepcao['vizinhos'][direcao] = self.grid.get((nx, ny), None)
            else:
                percepcao['vizinhos'][direcao] = None
        
        return percepcao
    
    def executar_acao(self, acao: Acao, bateria: int) -> Tuple[bool, int]:
        """Executa uma ação do agente"""
        custo_energia = 0
        pontos_ganhos = 0
        
        if acao == Acao.ASPIRAR:
            custo_energia = 2
            x, y = self.posicao_agente
            celula = self.grid.get((x, y))
            if celula and celula['sujeira'] != TipoSujeira.LIMPO:
                pontos_ganhos = celula['pontos']
                celula['sujeira'] = TipoSujeira.LIMPO
                celula['pontos'] = 0
                
        elif acao in [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]:
            custo_energia = 1
            nova_posicao = self._calcular_nova_posicao(acao)
            if nova_posicao and self._pode_mover_para(nova_posicao):
                self.posicao_agente = nova_posicao
            else:
                return False, 0  # Movimento inválido
        
        if bateria >= custo_energia:
            return True, pontos_ganhos
        else:
            return False, 0
    
    def _calcular_nova_posicao(self, acao: Acao) -> Optional[Tuple[int, int]]:
        """Calcula a nova posição baseada na ação"""
        x, y = self.posicao_agente
        if acao == Acao.NORTE:
            return (x, y - 1)
        elif acao == Acao.SUL:
            return (x, y + 1)
        elif acao == Acao.LESTE:
            return (x + 1, y)
        elif acao == Acao.OESTE:
            return (x - 1, y)
        return None
    
    def _pode_mover_para(self, posicao: Tuple[int, int]) -> bool:
        """Verifica se pode mover para uma posição"""
        x, y = posicao
        if not self._posicao_valida(x, y):
            return False
        
        celula = self.grid.get((x, y))
        return celula and celula['tipo_celula'] != TipoCelula.OBSTACULO
    
    def ambiente_limpo(self) -> bool:
        """Verifica se o ambiente está limpo"""
        for x in range(self.width):
            for y in range(self.height):
                celula = self.grid.get((x, y))
                if celula and celula['sujeira'] != TipoSujeira.LIMPO:
                    return False
        return True
    
    def percentual_limpo(self) -> float:
        """Calcula o percentual do ambiente limpo"""
        total_celulas = 0
        celulas_limpas = 0
        
        for x in range(self.width):
            for y in range(self.height):
                celula = self.grid.get((x, y))
                if celula:
                    total_celulas += 1
                    if celula['sujeira'] == TipoSujeira.LIMPO:
                        celulas_limpas += 1
        
        return (celulas_limpas / max(total_celulas, 1)) * 100

class AspiradorSimples:
    """Agente aspirador simplificado"""
    
    def __init__(self, tipo_agente: str):
        self.tipo_agente = tipo_agente
        self.bateria = 30
        self.pontos_coletados = 0
        self.estatisticas = {
            'total_acoes': 0,
            'acoes_movimento': 0,
            'acoes_aspirar': 0,
            'movimentos_invalidos': 0,
            'energia_gasta': 0
        }
        
        # Modelo interno (para agentes que precisam)
        self.modelo_ambiente = {}
        self.posicoes_visitadas = set()
        self.posicoes_limpas = set()
        
        # Para agentes BDI
        self.crencas = {}
        self.desejos = []
        self.intencoes = []
        self.estado_emocional = "neutral"
    
    def decidir_acao(self, percepcao: Dict) -> Acao:
        """Decide qual ação tomar baseado no tipo de agente"""
        if self.tipo_agente == "reativo":
            return self._decisao_reativa(percepcao)
        elif self.tipo_agente == "modelo":
            return self._decisao_modelo(percepcao)
        elif self.tipo_agente == "objetivos":
            return self._decisao_objetivos(percepcao)
        elif self.tipo_agente == "utilidade":
            return self._decisao_utilidade(percepcao)
        elif self.tipo_agente == "bdi":
            return self._decisao_bdi(percepcao)
        else:
            return Acao.PARAR
    
    def executar_ciclo(self, ambiente: AmbienteSimples) -> bool:
        """Executa um ciclo completo"""
        if self.bateria <= 0:
            return False
        
        # Perceber
        percepcao = ambiente.perceber()
        
        # Decidir ação
        acao = self.decidir_acao(percepcao)
        
        # Executar ação
        sucesso, pontos_ganhos = ambiente.executar_acao(acao, self.bateria)
        
        # Atualizar estatísticas
        self._atualizar_estatisticas(acao, sucesso, pontos_ganhos)
        
        # Verificar condições de parada
        if acao == Acao.PARAR or ambiente.ambiente_limpo():
            return False
            
        return True
    
    def _atualizar_estatisticas(self, acao: Acao, sucesso: bool, pontos_ganhos: int):
        """Atualiza as estatísticas do agente"""
        self.estatisticas['total_acoes'] += 1
        self.pontos_coletados += pontos_ganhos
        
        if acao == Acao.ASPIRAR:
            self.estatisticas['acoes_aspirar'] += 1
            self.estatisticas['energia_gasta'] += 2
            self.bateria -= 2
        elif acao in [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]:
            self.estatisticas['acoes_movimento'] += 1
            if not sucesso:
                self.estatisticas['movimentos_invalidos'] += 1
            else:
                self.estatisticas['energia_gasta'] += 1
                self.bateria -= 1
    
    def _decisao_reativa(self, percepcao: Dict) -> Acao:
        """Decisão do agente reativo simples"""
        celula_atual = percepcao['celula_atual']
        
        if celula_atual and celula_atual['sujeira'] != TipoSujeira.LIMPO:
            return Acao.ASPIRAR
        
        if self.bateria <= 2:
            return Acao.PARAR
        
        vizinhos = percepcao['vizinhos']
        for direcao, vizinho in vizinhos.items():
            if vizinho and vizinho['sujeira'] != TipoSujeira.LIMPO:
                return Acao(direcao)
        
        direcoes = [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]
        return random.choice(direcoes)
    
    def _decisao_modelo(self, percepcao: Dict) -> Acao:
        """Decisão do agente baseado em modelo"""
        self._atualizar_modelo_interno(percepcao)
        
        celula_atual = percepcao['celula_atual']
        
        if celula_atual and celula_atual['sujeira'] != TipoSujeira.LIMPO:
            return Acao.ASPIRAR
        
        if self.bateria <= 2:
            return Acao.PARAR
        
        proxima_posicao = self._encontrar_proxima_posicao_nao_visitada()
        if proxima_posicao:
            return self._calcular_movimento_para(percepcao['posicao'], proxima_posicao)
        
        direcoes = [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]
        return random.choice(direcoes)
    
    def _decisao_objetivos(self, percepcao: Dict) -> Acao:
        """Decisão do agente baseado em objetivos"""
        self._atualizar_modelo_interno(percepcao)
        
        celula_atual = percepcao['celula_atual']
        
        if celula_atual and celula_atual['sujeira'] != TipoSujeira.LIMPO:
            return Acao.ASPIRAR
        
        if self.bateria <= 2:
            return Acao.PARAR
        
        posicao_sujeira = self._encontrar_sujeira_maior_valor()
        if posicao_sujeira:
            return self._calcular_movimento_para(percepcao['posicao'], posicao_sujeira)
        
        direcoes = [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]
        return random.choice(direcoes)
    
    def _decisao_utilidade(self, percepcao: Dict) -> Acao:
        """Decisão do agente baseado em utilidade"""
        self._atualizar_modelo_interno(percepcao)
        
        celula_atual = percepcao['celula_atual']
        
        if celula_atual and celula_atual['sujeira'] != TipoSujeira.LIMPO:
            return Acao.ASPIRAR
        
        if self.bateria <= 2:
            return Acao.PARAR
        
        acoes_possiveis = [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]
        melhor_acao = max(acoes_possiveis, key=lambda acao: self._calcular_utilidade(acao, percepcao))
        return melhor_acao
    
    def _decisao_bdi(self, percepcao: Dict) -> Acao:
        """Decisão do agente BDI"""
        self._atualizar_crencas(percepcao)
        self._atualizar_estado_emocional(percepcao)
        self._atualizar_desejos()
        self._selecionar_intencoes()
        
        celula_atual = percepcao['celula_atual']
        
        if celula_atual and celula_atual['sujeira'] != TipoSujeira.LIMPO:
            return Acao.ASPIRAR
        
        if self.bateria <= 2:
            return Acao.PARAR
        
        if self.intencoes:
            return self.intencoes.pop(0)
        
        direcoes = [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]
        return random.choice(direcoes)
    
    # Métodos auxiliares (implementações simplificadas)
    def _atualizar_modelo_interno(self, percepcao: Dict):
        """Atualiza o modelo interno"""
        posicao_atual = percepcao['posicao']
        self.posicoes_visitadas.add(posicao_atual)
        
        celula_atual = percepcao['celula_atual']
        if celula_atual:
            self.modelo_ambiente[posicao_atual] = celula_atual.copy()
            if celula_atual['sujeira'] == TipoSujeira.LIMPO:
                self.posicoes_limpas.add(posicao_atual)
        
        for direcao, vizinho in percepcao['vizinhos'].items():
            if vizinho:
                posicao_vizinho = self._calcular_posicao_vizinho(posicao_atual, direcao)
                if posicao_vizinho:
                    self.modelo_ambiente[posicao_vizinho] = vizinho.copy()
    
    def _calcular_posicao_vizinho(self, posicao_atual: Tuple[int, int], direcao: str) -> Optional[Tuple[int, int]]:
        """Calcula a posição do vizinho"""
        x, y = posicao_atual
        if direcao == 'norte':
            return (x, y - 1)
        elif direcao == 'sul':
            return (x, y + 1)
        elif direcao == 'leste':
            return (x + 1, y)
        elif direcao == 'oeste':
            return (x - 1, y)
        return None
    
    def _encontrar_proxima_posicao_nao_visitada(self) -> Optional[Tuple[int, int]]:
        """Encontra a próxima posição não visitada"""
        x_atual, y_atual = self.posicoes_visitadas.pop() if self.posicoes_visitadas else (0, 0)
        melhor_posicao = None
        menor_distancia = float('inf')
        
        for x in range(5):
            for y in range(5):
                posicao = (x, y)
                if posicao not in self.posicoes_visitadas:
                    if posicao in self.modelo_ambiente:
                        if self.modelo_ambiente[posicao]['tipo_celula'] == TipoCelula.OBSTACULO:
                            continue
                    distancia = abs(x - x_atual) + abs(y - y_atual)
                    if distancia < menor_distancia:
                        menor_distancia = distancia
                        melhor_posicao = posicao
        
        return melhor_posicao
    
    def _encontrar_sujeira_maior_valor(self) -> Optional[Tuple[int, int]]:
        """Encontra a sujeira de maior valor"""
        melhor_posicao = None
        maior_valor = 0
        
        for posicao, celula in self.modelo_ambiente.items():
            if (celula['sujeira'] != TipoSujeira.LIMPO and 
                posicao not in self.posicoes_limpas):
                if celula['pontos'] > maior_valor:
                    maior_valor = celula['pontos']
                    melhor_posicao = posicao
        
        return melhor_posicao
    
    def _calcular_movimento_para(self, origem: Tuple[int, int], destino: Tuple[int, int]) -> Acao:
        """Calcula o movimento necessário"""
        x_orig, y_orig = origem
        x_dest, y_dest = destino
        
        if x_dest > x_orig:
            return Acao.LESTE
        elif x_dest < x_orig:
            return Acao.OESTE
        elif y_dest > y_orig:
            return Acao.SUL
        elif y_dest < y_orig:
            return Acao.NORTE
        
        return Acao.PARAR
    
    def _calcular_utilidade(self, acao: Acao, percepcao: Dict) -> float:
        """Calcula a utilidade de uma ação"""
        if acao not in [Acao.NORTE, Acao.SUL, Acao.LESTE, Acao.OESTE]:
            return 0.0
        
        x, y = percepcao['posicao']
        if acao == Acao.NORTE:
            nova_posicao = (x, y - 1)
        elif acao == Acao.SUL:
            nova_posicao = (x, y + 1)
        elif acao == Acao.LESTE:
            nova_posicao = (x + 1, y)
        else:  # OESTE
            nova_posicao = (x - 1, y)
        
        if not (0 <= nova_posicao[0] < 5 and 0 <= nova_posicao[1] < 5):
            return -1.0
        
        utilidade = 0.0
        
        if nova_posicao in self.modelo_ambiente:
            celula = self.modelo_ambiente[nova_posicao]
            utilidade += celula['pontos'] * 1.0
        
        if nova_posicao not in self.posicoes_visitadas:
            utilidade += 0.5
        
        utilidade -= 0.2
        
        return utilidade
    
    def _atualizar_crencas(self, percepcao: Dict):
        """Atualiza as crenças do agente BDI"""
        self._atualizar_modelo_interno(percepcao)
    
    def _atualizar_estado_emocional(self, percepcao: Dict):
        """Atualiza o estado emocional"""
        bateria_baixa = self.bateria < 10
        sujeira_proxima = any(
            vizinho and vizinho['sujeira'] != TipoSujeira.LIMPO 
            for vizinho in percepcao['vizinhos'].values()
        )
        
        if bateria_baixa:
            self.estado_emocional = "desperate"
        elif sujeira_proxima:
            self.estado_emocional = "focused"
        else:
            self.estado_emocional = "neutral"
    
    def _atualizar_desejos(self):
        """Atualiza os desejos"""
        self.desejos = []
        
        for posicao, celula in self.modelo_ambiente.items():
            if celula['sujeira'] != TipoSujeira.LIMPO and posicao not in self.posicoes_limpas:
                self.desejos.append({
                    'tipo': 'limpar',
                    'posicao': posicao,
                    'prioridade': celula['pontos'],
                    'valor': celula['pontos']
                })
        
        self.desejos.sort(key=lambda d: d['prioridade'], reverse=True)
    
    def _selecionar_intencoes(self):
        """Seleciona intenções"""
        self.intencoes = []
        
        if not self.desejos:
            return
        
        if self.estado_emocional == "desperate":
            desejo = max([d for d in self.desejos if d['tipo'] == 'limpar'], 
                        key=lambda d: d['valor'], default=None)
        elif self.estado_emocional == "focused":
            desejo = next((d for d in self.desejos if d['tipo'] == 'limpar'), None)
        else:
            desejo = self.desejos[0] if self.desejos else None
        
        if desejo and desejo['tipo'] == 'limpar':
            self._criar_plano_limpeza((0, 0), desejo['posicao'])  # Simplificado
    
    def _criar_plano_limpeza(self, origem: Tuple[int, int], destino: Tuple[int, int]):
        """Cria um plano para limpeza"""
        x_orig, y_orig = origem
        x_dest, y_dest = destino
        
        while x_orig != x_dest:
            if x_orig < x_dest:
                self.intencoes.append(Acao.LESTE)
                x_orig += 1
            else:
                self.intencoes.append(Acao.OESTE)
                x_orig -= 1
        
        while y_orig != y_dest:
            if y_orig < y_dest:
                self.intencoes.append(Acao.SUL)
                y_orig += 1
            else:
                self.intencoes.append(Acao.NORTE)
                y_orig -= 1
        
        self.intencoes.append(Acao.ASPIRAR)

def run_simulation_simple(tipo_agente: str, seed: int = 42, max_steps: int = 200) -> Dict:
    """Executa uma simulação simples"""
    ambiente = AmbienteSimples(seed=seed)
    agente = AspiradorSimples(tipo_agente)
    
    print(f"Executando simulação com {tipo_agente}")
    print(f"Seed: {seed}")
    print("-" * 50)
    
    for step in range(max_steps):
        continuar = agente.executar_ciclo(ambiente)
        
        if not continuar:
            print(f"Simulação finalizada no passo {step + 1}")
            break
        
        if (step + 1) % 50 == 0:
            print(f"Passo {step + 1}: Bateria={agente.bateria}, "
                  f"Pontos={agente.pontos_coletados}, "
                  f"Limpeza={ambiente.percentual_limpo():.1f}%")
    
    # Resultados finais
    eficiencia = agente.pontos_coletados / max(agente.estatisticas['energia_gasta'], 1)
    
    resultado = {
        'tipo_agente': tipo_agente,
        'passos': step + 1,
        'pontos_coletados': agente.pontos_coletados,
        'bateria_restante': agente.bateria,
        'percentual_limpo': ambiente.percentual_limpo(),
        'total_acoes': agente.estatisticas['total_acoes'],
        'eficiencia_energetica': eficiencia,
        'movimentos_invalidos': agente.estatisticas['movimentos_invalidos']
    }
    
    print("\n" + "=" * 50)
    print("RESULTADOS FINAIS:")
    print("=" * 50)
    print(f"Tipo de Agente: {tipo_agente.title()}")
    print(f"Passos executados: {resultado['passos']}")
    print(f"Pontos coletados: {resultado['pontos_coletados']}")
    print(f"Bateria restante: {resultado['bateria_restante']}/30")
    print(f"Percentual limpo: {resultado['percentual_limpo']:.1f}%")
    print(f"Total de ações: {resultado['total_acoes']}")
    print(f"Eficiência energética: {resultado['eficiencia_energetica']:.3f}")
    print(f"Movimentos inválidos: {resultado['movimentos_invalidos']}")
    
    return resultado

def compare_agents_simple(num_tests: int = 5) -> Dict:
    """Compara diferentes tipos de agentes"""
    tipos_agentes = ["reativo", "modelo", "objetivos", "utilidade", "bdi"]
    resultados = {}
    
    print("COMPARAÇÃO DE AGENTES (VERSÃO SIMPLIFICADA)")
    print("=" * 60)
    
    for tipo in tipos_agentes:
        print(f"\nTestando Agente {tipo.title()}...")
        resultados_tipo = []
        
        for test in range(num_tests):
            seed = 42 + test
            resultado = run_simulation_simple(tipo, seed, max_steps=100)
            resultados_tipo.append(resultado)
            time.sleep(0.1)  # Pequena pausa
        
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

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "compare":
            num_tests = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            compare_agents_simple(num_tests)
        elif command == "test":
            tipo = sys.argv[2] if len(sys.argv) > 2 else "reativo"
            seed = int(sys.argv[3]) if len(sys.argv) > 3 else 42
            run_simulation_simple(tipo, seed)
        else:
            print("Comandos disponíveis:")
            print("  python mesa_simple.py compare [num_tests]")
            print("  python mesa_simple.py test [tipo] [seed]")
    else:
        print("Executando comparação rápida...")
        compare_agents_simple(3)
