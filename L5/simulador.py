import random
from typing import List, Dict
from proceso import Proceso
from planificador import PlanificadorProcesos

class Simulador:
    """
    Clase que implementa el simulador de estados de procesos.
    Coordina la generación de procesos y su ejecución a través del planificador.
    
    Atributos:
        planificador (PlanificadorProcesos): Instancia del planificador de procesos
        ciclos (int): Número total de ciclos de simulación
        ciclo_actual (int): Ciclo actual de la simulación
        historial_estados (List[Dict]): Historial de estados del sistema
        historial_estadisticas (List[Dict]): Historial de estadísticas
        procesos_pendientes (List[Proceso]): Lista de procesos pendientes de admisión
        probabilidad_admision (float): Probabilidad de admitir un nuevo proceso (30%)
        probabilidad_suspension (float): Probabilidad de suspender un proceso (40%)
    """
    
    def __init__(self, quantum: int = 2, ciclos: int = 100):
        """
        Inicializa el simulador.
        
        Args:
            quantum (int): Tiempo máximo de ejecución por proceso
            ciclos (int): Número total de ciclos de simulación
        """
        self.planificador = PlanificadorProcesos(quantum)
        self.ciclos = ciclos
        self.ciclo_actual = 0
        self.historial_estados: List[Dict] = []
        self.historial_estadisticas: List[Dict] = []
        self.procesos_pendientes: List[Proceso] = []
        self.probabilidad_admision = 0.3  # 30% de probabilidad de admitir un nuevo proceso
        self.probabilidad_suspension = 0.4  # 40% de probabilidad de suspender un proceso
    
    def generar_procesos(self, cantidad: int) -> List[Proceso]:
        """Genera una lista de procesos con características aleatorias"""
        procesos = []
        for i in range(cantidad):
            proceso = Proceso(
                id=i + 1,
                nombre=f"Proceso_{i + 1}",
                tiempo_ejecucion=random.randint(5, 20),
                prioridad=random.randint(1, 5),
                tiempo_restante=0  # Se inicializa en __post_init__
            )
            procesos.append(proceso)
        return procesos
    
    def simular(self, cantidad_procesos: int = 15) -> Dict:
        """Ejecuta la simulación completa"""
        # Generar todos los procesos pero no admitirlos inmediatamente
        self.procesos_pendientes = self.generar_procesos(cantidad_procesos)
        
        # Ejecutar ciclos de simulación
        for _ in range(self.ciclos):
            self.ciclo_actual += 1
            
            # Intentar admitir nuevos procesos
            if self.procesos_pendientes and random.random() < self.probabilidad_admision:
                proceso = self.procesos_pendientes.pop(0)
                self.planificador.admitir_proceso(proceso)
            
            # Ejecutar ciclo del planificador
            estadisticas = self.planificador.ejecutar_ciclo()
            
            # Registrar estado actual y estadísticas
            self.historial_estados.append(self.obtener_estado_actual())
            self.historial_estadisticas.append(estadisticas)
            
            # Simular swapping con mayor probabilidad
            if random.random() < self.probabilidad_suspension:
                self._simular_swapping()
        
        return self.obtener_resultados_finales()
    
    def _simular_swapping(self):
        """
        Simula el swapping de procesos entre memoria principal y secundaria.
        
        Realiza las siguientes operaciones:
        1. Suspende procesos de LISTO a LISTO_SUSPENDIDO
        2. Reanuda procesos de LISTO_SUSPENDIDO a LISTO
        3. Suspende procesos de ESPERANDO a ESPERANDO_SUSPENDIDO
        4. Reanuda procesos de ESPERANDO_SUSPENDIDO a ESPERANDO
        """
        # Suspender proceso aleatorio de la cola de listos
        if not self.planificador.cola_listos.empty() and random.random() < self.probabilidad_suspension:
            proceso = self.planificador.cola_listos.get()
            self.planificador.suspender_proceso(proceso)
            print(f"Proceso {proceso.id} suspendido desde LISTO")
        
        # Reanudar proceso aleatorio suspendido
        if not self.planificador.cola_listo_suspendido.empty() and random.random() < 0.3:
            proceso = self.planificador.cola_listo_suspendido.get()
            self.planificador.reanudar_proceso(proceso)
            print(f"Proceso {proceso.id} reanudado desde LISTO_SUSPENDIDO")
        
        # Suspender proceso aleatorio de la cola de esperando
        if not self.planificador.cola_esperando.empty() and random.random() < self.probabilidad_suspension:
            proceso = self.planificador.cola_esperando.get()
            self.planificador.suspender_proceso(proceso)
            print(f"Proceso {proceso.id} suspendido desde ESPERANDO")
        
        # Reanudar proceso aleatorio suspendido de esperando
        if not self.planificador.cola_esperando_suspendido.empty() and random.random() < 0.3:
            proceso = self.planificador.cola_esperando_suspendido.get()
            self.planificador.reanudar_proceso(proceso)
            print(f"Proceso {proceso.id} reanudado desde ESPERANDO_SUSPENDIDO")
    
    def obtener_resultados_finales(self) -> Dict:
        """Retorna los resultados finales de la simulación"""
        if not self.historial_estadisticas:
            return {}
        
        ultimas_estadisticas = self.historial_estadisticas[-1]
        return {
            'estadisticas_finales': ultimas_estadisticas,
            'ciclos_ejecutados': self.ciclo_actual,
            'procesos_terminados': len(self.planificador.cola_terminados),
            'procesos_pendientes': (
                self.planificador.cola_listos.qsize() +
                self.planificador.cola_esperando.qsize() +
                self.planificador.cola_listo_suspendido.qsize() +
                self.planificador.cola_esperando_suspendido.qsize()
            ),
            'historial_estados': self.historial_estados,
            'historial_estadisticas': self.historial_estadisticas
        }
    
    def obtener_estado_actual(self) -> Dict:
        """
        Retorna el estado actual del sistema.
        
        Returns:
            Dict: Estado actual que incluye:
                - ciclo_actual: Número del ciclo actual
                - estado_sistema: Estado de todas las colas de procesos
                - estadisticas: Estadísticas actuales del sistema
        """
        return {
            'ciclo_actual': self.ciclo_actual,
            'estado_sistema': self.planificador.obtener_estado_actual(),
            'estadisticas': self.planificador.obtener_estadisticas()
        } 