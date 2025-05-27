from enum import Enum
from dataclasses import dataclass
from typing import Optional
import random

class EstadoProceso(Enum):
    NUEVO = "NUEVO"
    LISTO = "LISTO"
    EJECUTANDO = "EJECUTANDO"
    ESPERANDO = "ESPERANDO"
    TERMINADO = "TERMINADO"
    LISTO_SUSPENDIDO = "LISTO_SUSPENDIDO"
    ESPERANDO_SUSPENDIDO = "ESPERANDO_SUSPENDIDO"

@dataclass
class Proceso:
    id: int
    nombre: str
    tiempo_ejecucion: int
    prioridad: int
    tiempo_restante: int
    estado: EstadoProceso = EstadoProceso.NUEVO
    tiempo_creacion: int = 0
    tiempo_espera: int = 0
    tiempo_respuesta: Optional[int] = None
    tiempo_finalizacion: Optional[int] = None
    
    def __post_init__(self):
        self.tiempo_restante = self.tiempo_ejecucion
    
    def ejecutar(self, quantum: int) -> int:
        """Ejecuta el proceso por un quantum de tiempo y retorna el tiempo real usado"""
        tiempo_usado = min(quantum, self.tiempo_restante)
        self.tiempo_restante -= tiempo_usado
        return tiempo_usado
    
    def necesita_io(self) -> bool:
        """Determina si el proceso necesita realizar operaciones de I/O"""
        # 20% de probabilidad de necesitar I/O
        return random.random() < 0.2
    
    def completado(self) -> bool:
        """Verifica si el proceso ha completado su ejecución"""
        return self.tiempo_restante <= 0
    
    def actualizar_tiempo_espera(self):
        """Incrementa el tiempo de espera del proceso"""
        self.tiempo_espera += 1
    
    def calcular_tiempo_respuesta(self, tiempo_actual: int):
        """Calcula el tiempo de respuesta del proceso"""
        if self.tiempo_respuesta is None:
            self.tiempo_respuesta = tiempo_actual - self.tiempo_creacion
    
    def calcular_tiempo_finalizacion(self, tiempo_actual: int):
        """Registra el tiempo de finalización del proceso"""
        self.tiempo_finalizacion = tiempo_actual
    
    def __str__(self) -> str:
        return f"Proceso {self.id} ({self.nombre}) - Estado: {self.estado.value} - Tiempo restante: {self.tiempo_restante}" 