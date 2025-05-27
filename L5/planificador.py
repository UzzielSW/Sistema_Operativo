from queue import Queue
from typing import List, Dict, Optional
from proceso import Proceso, EstadoProceso
import random

class PlanificadorProcesos:
    """
    Clase que implementa el planificador de procesos del sistema operativo.
    Maneja las transiciones de estado de los procesos y mantiene las colas de procesos.
    
    Atributos:
        quantum (int): Tiempo máximo de ejecución por proceso
        tiempo_actual (int): Tiempo actual de la simulación
        proceso_actual (Proceso): Proceso que está ejecutándose actualmente
        cola_nuevos (Queue): Cola de procesos en estado NUEVO
        cola_listos (Queue): Cola de procesos en estado LISTO
        cola_esperando (Queue): Cola de procesos en estado ESPERANDO
        cola_terminados (List): Lista de procesos terminados
        cola_listo_suspendido (Queue): Cola de procesos en estado LISTO_SUSPENDIDO
        cola_esperando_suspendido (Queue): Cola de procesos en estado ESPERANDO_SUSPENDIDO
    """
    
    def __init__(self, quantum: int = 2):
        """
        Inicializa el planificador de procesos.
        
        Args:
            quantum (int): Tiempo máximo de ejecución por proceso
        """
        self.quantum = quantum
        self.tiempo_actual = 0
        self.proceso_actual: Optional[Proceso] = None
        
        # Colas para cada estado
        self.cola_nuevos = Queue()
        self.cola_listos = Queue()
        self.cola_esperando = Queue()
        self.cola_terminados: List[Proceso] = []
        
        # Colas para estados suspendidos
        self.cola_listo_suspendido = Queue()
        self.cola_esperando_suspendido = Queue()
        
        # Estadísticas
        self.estadisticas = {
            'tiempo_espera_total': 0,
            'tiempo_respuesta_total': 0,
            'procesos_completados': 0
        }
    
    def admitir_proceso(self, proceso: Proceso):
        """Admite un nuevo proceso al sistema"""
        proceso.tiempo_creacion = self.tiempo_actual
        proceso.estado = EstadoProceso.NUEVO  # Aseguramos que el proceso comience en NUEVO
        self.cola_nuevos.put(proceso)
    
    def mover_a_listo(self, proceso: Proceso):
        """Mueve un proceso al estado LISTO"""
        proceso.estado = EstadoProceso.LISTO
        self.cola_listos.put(proceso)
    
    def mover_a_esperando(self, proceso: Proceso):
        """Mueve un proceso al estado ESPERANDO"""
        proceso.estado = EstadoProceso.ESPERANDO
        self.cola_esperando.put(proceso)
    
    def mover_a_terminado(self, proceso: Proceso):
        """Mueve un proceso al estado TERMINADO"""
        proceso.estado = EstadoProceso.TERMINADO
        proceso.calcular_tiempo_finalizacion(self.tiempo_actual)
        self.cola_terminados.append(proceso)
        self.estadisticas['procesos_completados'] += 1
        self.estadisticas['tiempo_espera_total'] += proceso.tiempo_espera
        if proceso.tiempo_respuesta:
            self.estadisticas['tiempo_respuesta_total'] += proceso.tiempo_respuesta
    
    def suspender_proceso(self, proceso: Proceso):
        """Suspende un proceso (simula swapping)"""
        if proceso.estado == EstadoProceso.LISTO:
            proceso.estado = EstadoProceso.LISTO_SUSPENDIDO
            self.cola_listo_suspendido.put(proceso)
        elif proceso.estado == EstadoProceso.ESPERANDO:
            proceso.estado = EstadoProceso.ESPERANDO_SUSPENDIDO
            self.cola_esperando_suspendido.put(proceso)
    
    def reanudar_proceso(self, proceso: Proceso):
        """Reanuda un proceso suspendido"""
        if proceso.estado == EstadoProceso.LISTO_SUSPENDIDO:
            proceso.estado = EstadoProceso.LISTO
            self.cola_listos.put(proceso)
        elif proceso.estado == EstadoProceso.ESPERANDO_SUSPENDIDO:
            proceso.estado = EstadoProceso.ESPERANDO
            self.cola_esperando.put(proceso)
    
    def ejecutar_ciclo(self) -> Dict:
        """
        Ejecuta un ciclo completo del planificador.
        
        El ciclo incluye:
        1. Procesar nuevos procesos (permanecen en NUEVO por 3 ciclos)
        2. Procesar I/O completado
        3. Ejecutar proceso actual o seleccionar uno nuevo
        4. Actualizar tiempos de espera
        
        Returns:
            Dict: Estadísticas actuales del sistema
        """
        # Incrementar el tiempo actual al inicio del ciclo
        self.tiempo_actual += 1
        
        # Procesar nuevos procesos
        procesos_nuevos = []
        while not self.cola_nuevos.empty():
            proceso = self.cola_nuevos.get()
            # Si el proceso ha estado en NUEVO por al menos 3 ciclos, lo movemos a LISTO
            if self.tiempo_actual - proceso.tiempo_creacion >= 3:
                self.mover_a_listo(proceso)
            else:
                procesos_nuevos.append(proceso)
        
        # Devolver procesos que aún deben permanecer en NUEVO
        for proceso in procesos_nuevos:
            self.cola_nuevos.put(proceso)
        
        # Procesar I/O completado
        procesos_esperando = []
        while not self.cola_esperando.empty():
            proceso = self.cola_esperando.get()
            if random.random() < 0.3:  # 30% de probabilidad de completar I/O
                self.mover_a_listo(proceso)
            else:
                procesos_esperando.append(proceso)
        
        # Devolver procesos no completados a la cola
        for proceso in procesos_esperando:
            self.cola_esperando.put(proceso)
        
        # Ejecutar proceso actual o seleccionar uno nuevo
        if self.proceso_actual is None or self.proceso_actual.estado != EstadoProceso.EJECUTANDO:
            if not self.cola_listos.empty():
                self.proceso_actual = self.cola_listos.get()
                self.proceso_actual.estado = EstadoProceso.EJECUTANDO
                self.proceso_actual.calcular_tiempo_respuesta(self.tiempo_actual)
        
        # Ejecutar proceso actual si existe
        if self.proceso_actual is not None:
            tiempo_usado = self.proceso_actual.ejecutar(self.quantum)
            self.tiempo_actual += tiempo_usado
            
            # Verificar si el proceso necesita I/O
            if self.proceso_actual.necesita_io():
                self.mover_a_esperando(self.proceso_actual)
                self.proceso_actual = None
            # Verificar si el proceso ha terminado
            elif self.proceso_actual.completado():
                self.mover_a_terminado(self.proceso_actual)
                self.proceso_actual = None
            # Verificar si se agotó el quantum
            elif tiempo_usado == self.quantum:
                self.mover_a_listo(self.proceso_actual)
                self.proceso_actual = None
        
        # Actualizar tiempos de espera
        for proceso in list(self.cola_listos.queue):
            proceso.actualizar_tiempo_espera()
        
        return self.obtener_estadisticas()
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas actuales del sistema"""
        total_procesos = len(self.cola_terminados)
        if total_procesos == 0:
            return {
                'tiempo_espera_promedio': 0,
                'tiempo_respuesta_promedio': 0,
                'throughput': 0
            }
        
        return {
            'tiempo_espera_promedio': self.estadisticas['tiempo_espera_total'] / total_procesos,
            'tiempo_respuesta_promedio': self.estadisticas['tiempo_respuesta_total'] / total_procesos,
            'throughput': total_procesos / self.tiempo_actual if self.tiempo_actual > 0 else 0
        }
    
    def obtener_estado_actual(self) -> Dict:
        """Retorna el estado actual del sistema"""
        return {
            'nuevos': list(self.cola_nuevos.queue),
            'listos': list(self.cola_listos.queue),
            'ejecutando': [self.proceso_actual] if self.proceso_actual else [],
            'esperando': list(self.cola_esperando.queue),
            'terminados': self.cola_terminados,
            'listo_suspendido': list(self.cola_listo_suspendido.queue),
            'esperando_suspendido': list(self.cola_esperando_suspendido.queue)
        } 