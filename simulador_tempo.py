class SimuladorTempo:
    """Classe simples para simular o tempo sem SimPy"""
    def __init__(self):
        self.tempo = 0
        self.processos = []
    
    def process(self, generator):
        """Adiciona um processo ao simulador"""
        self.processos.append(generator)
    
    def step(self):
        """Executa um passo de todos os processos"""
        self.tempo += 1
        processos_ativos = []
        
        for processo in self.processos:
            try:
                next(processo)
                processos_ativos.append(processo)
            except StopIteration:
                pass  # Processo terminou
        
        self.processos = processos_ativos

    def timeout(self, delay):
        """Simula um timeout (para compatibilidade com SimPy)"""
        for _ in range(delay):
            yield None