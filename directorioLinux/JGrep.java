import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.FileNotFoundException;
import java.nio.file.Files;
import java.nio.file.Paths;

public class JGrep {

    public static void main(String[] args) {
        // Verificar si hay al menos 3 argumentos (patrón y archivo)
        if (args.length < 3) {
            printUsage();
            return;
        }

        // capturando parametros
        String pattern = args[1];
        String filePath = args[2];
        boolean caseInsensitive = false;

        // Verificar si hay un tercer argumento y si es la opción -i
        if (args.length >= 3 && args[2].equalsIgnoreCase("-i")) {
            caseInsensitive = true;
            System.out.println("[Búsqueda insensible a mayúsculas/minúsculas activada]");
        }

        //IMPORT TEST

        // Validar que el archivo exista y sea un archivo regular
        if (!Files.exists(Paths.get(filePath)) || !Files.isRegularFile(Paths.get(filePath))) {
             System.err.println("Error: El archivo '" + filePath + "' no existe o no es un archivo válido.");
             return;
        }

        System.out.println("Buscando el patrón '" + pattern + "' en el archivo '" + filePath + "'...\n");

        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            int lineNumber = 0;
            boolean found = false;

            //ciclo para recorrer el archivo y buscar el patrón
            while ((line = reader.readLine()) != null) {
                lineNumber++;

                //convierte a minúsculas cuando caseInsensitive sea true
                String lineToCompare = caseInsensitive ? line.toLowerCase() : line;
                String patternToCompare = caseInsensitive ? pattern.toLowerCase() : pattern;

                if (lineToCompare.contains(patternToCompare)) {
                    System.out.println("L" + lineNumber + ": " + line);
                    found = true;
                }
            }

            if (!found) {
                System.out.println("No se encontraron coincidencias para el patrón '" + pattern + "'.");
            }

        } catch (FileNotFoundException e) {
            // Esta comprobación ya se hizo antes, pero es buena práctica mantener el catch
             System.err.println("Error: Archivo no encontrado '" + filePath + "'.");
        } catch (IOException e) {
            System.err.println("Error al leer el archivo '" + filePath + "': " + e.getMessage());
        } catch (SecurityException e) {
             System.err.println("Error: No se tienen permisos para leer el archivo '" + filePath + "'.");
        }
    }

    //explicacion del uso del comando en caso no se ingrese los parametros correctos
    private static void printUsage() {
        System.out.println("Uso: java JGrep <patrón> <rutaArchivo> [-i]");
        System.out.println("  <patrón>      : El texto a buscar dentro del archivo.");
        System.out.println("  <rutaArchivo> : La ruta completa al archivo de texto.");
        System.out.println("  [-i]          : (Opcional) Realiza la búsqueda insensible a mayúsculas/minúsculas.");
        System.out.println("\nEjemplo:");
        System.out.println("  java JGrep \"error\" log.txt -i");
        System.out.println("  java JGrep \"import java\" JGrep.java");
    }
}
