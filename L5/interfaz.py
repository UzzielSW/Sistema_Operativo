from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from typing import Dict, List
import time
import random

class Interfaz:
    """
    Clase que implementa la interfaz de usuario del simulador.
    Utiliza la biblioteca rich para mostrar información de forma interactiva.
    
    Atributos:
        console (Console): Instancia de la consola rich para mostrar información
    """
    
    def __init__(self):
        """Inicializa la interfaz de usuario."""
        self.console = Console()
    
    def mostrar_bienvenida(self):
        """
        Muestra el mensaje de bienvenida del simulador.
        Se muestra al inicio de la simulación y permanece visible por 5 segundos.
        """
        self.console.print(Panel.fit(
            "[bold blue]Simulador de Estados de Procesos[/bold blue]\n"
            "[yellow]Sistema Operativo - Simulación de Procesos[/yellow]",
            border_style="blue"
        ))
    
    def crear_tabla_estado(self, estado: Dict) -> Table:
        """Crea una tabla con el estado actual del sistema"""
        tabla = Table(title="Estado del Sistema", show_header=True, header_style="bold magenta")
        tabla.add_column("Estado", style="cyan")
        tabla.add_column("Cantidad", justify="right", style="green")
        tabla.add_column("Procesos", style="yellow")
        
        for estado_nombre, procesos in estado['estado_sistema'].items():
            cantidad = len(procesos)
            lista_procesos = ", ".join([f"P{p.id}" for p in procesos]) if procesos else "-"
            tabla.add_row(estado_nombre, str(cantidad), lista_procesos)
        
        return tabla
    
    def crear_panel_estadisticas(self, estado: Dict) -> Panel:
        """Crea un panel con las estadísticas actuales"""
        stats = estado['estadisticas']
        return Panel(
            f"[bold]Estadísticas del Sistema[/bold]\n"
            f"Ciclo actual: {estado['ciclo_actual']}\n"
            f"Tiempo de espera promedio: {stats['tiempo_espera_promedio']:.2f}\n"
            f"Tiempo de respuesta promedio: {stats['tiempo_respuesta_promedio']:.2f}\n"
            f"Throughput: {stats['throughput']:.2f}",
            title="Métricas",
            border_style="green"
        )
    
    def mostrar_estado_actual(self, estado: Dict):
        """Muestra el estado actual del sistema"""
        # Limpiar la pantalla para mejor visualización
        self.console.clear()
        tabla = self.crear_tabla_estado(estado)
        estadisticas = self.crear_panel_estadisticas(estado)
        
        self.console.print(tabla)
        self.console.print(estadisticas)
    
    def mostrar_progreso(self, total: int, actual: int):
        """Muestra una barra de progreso"""
        with Progress() as progress:
            task = progress.add_task("[cyan]Simulando...", total=total)
            progress.update(task, completed=actual)
    
    def mostrar_resultados_finales(self, resultados: Dict):
        """Muestra los resultados finales de la simulación"""
        self.console.print("\n[bold green]Resultados Finales de la Simulación[/bold green]")
        
        tabla = Table(show_header=True, header_style="bold magenta")
        tabla.add_column("Métrica", style="cyan")
        tabla.add_column("Valor", justify="right", style="green")
        
        # Usar las estadísticas del último estado
        stats = resultados.get('estadisticas', {})
        tabla.add_row("Ciclos ejecutados", str(resultados.get('ciclo_actual', 0)))
        tabla.add_row("Procesos terminados", str(len(resultados.get('estado_sistema', {}).get('terminados', []))))
        tabla.add_row("Procesos pendientes", str(
            len(resultados.get('estado_sistema', {}).get('listos', [])) +
            len(resultados.get('estado_sistema', {}).get('esperando', [])) +
            len(resultados.get('estado_sistema', {}).get('listo_suspendido', [])) +
            len(resultados.get('estado_sistema', {}).get('esperando_suspendido', []))
        ))
        tabla.add_row("Tiempo de espera promedio", f"{stats.get('tiempo_espera_promedio', 0):.2f}")
        tabla.add_row("Tiempo de respuesta promedio", f"{stats.get('tiempo_respuesta_promedio', 0):.2f}")
        tabla.add_row("Throughput", f"{stats.get('throughput', 0):.2f}")
        
        self.console.print(tabla)
    
    def simular_en_tiempo_real(self, simulador, cantidad_procesos: int = 15):
        """
        Ejecuta la simulación en tiempo real con actualización continua.
        
        Args:
            simulador (Simulador): Instancia del simulador
            cantidad_procesos (int): Número de procesos a simular
        
        La simulación:
        1. Muestra el mensaje de bienvenida por 5 segundos
        2. Genera los procesos iniciales
        3. Ejecuta ciclos hasta alcanzar el límite configurado
        4. Muestra el estado actual en cada ciclo
        5. Permite interrumpir la simulación con Ctrl+C
        """
        try:
            # Mostrar mensaje de bienvenida por 5 segundos
            self.console.clear()
            self.mostrar_bienvenida()
            time.sleep(5)
            
            # Generar todos los procesos pero no admitirlos inmediatamente
            simulador.procesos_pendientes = simulador.generar_procesos(cantidad_procesos)
            ciclo_actual = 0
            
            while ciclo_actual < simulador.ciclos:  # Verificar el límite de ciclos
                # Incrementar ciclo actual
                ciclo_actual += 1
                
                # Limpiar pantalla
                self.console.clear()
                
                # Intentar admitir nuevos procesos
                if simulador.procesos_pendientes and random.random() < simulador.probabilidad_admision:
                    proceso = simulador.procesos_pendientes.pop(0)
                    simulador.planificador.admitir_proceso(proceso)
                
                # Ejecutar ciclo del planificador
                simulador.planificador.ejecutar_ciclo()
                
                # Simular swapping
                if random.random() < simulador.probabilidad_suspension:
                    simulador._simular_swapping()
                
                # Mostrar estado actual
                estado_actual = simulador.obtener_estado_actual()
                estado_actual['ciclo_actual'] = ciclo_actual
                self.mostrar_estado_actual(estado_actual)
                
                # Esperar antes de la siguiente actualización
                time.sleep(1)
            
            # Mostrar resultados finales
            self.mostrar_resultados_finales(simulador.obtener_estado_actual())
                
        except KeyboardInterrupt:
            self.console.print("\n[bold red]Simulación interrumpida por el usuario[/bold red]")
        except Exception as e:
            self.console.print(f"\n[bold red]Error durante la simulación: {str(e)}[/bold red]")
        finally:
            self.console.print("\n[bold yellow]Presiona Enter para volver al menú principal...[/bold yellow]")
            input() 