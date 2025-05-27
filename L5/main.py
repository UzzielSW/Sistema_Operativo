from simulador import Simulador
from interfaz import Interfaz

def main():
    # Configuración de la simulación
    QUANTUM = 2
    CICLOS = 100
    CANTIDAD_PROCESOS = 15
    
    # Crear instancias
    simulador = Simulador(quantum=QUANTUM, ciclos=CICLOS)
    interfaz = Interfaz()
    
    # Ejecutar simulación con visualización en tiempo real
    interfaz.simular_en_tiempo_real(simulador, CANTIDAD_PROCESOS)

if __name__ == "__main__":
    main() 