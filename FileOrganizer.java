import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

public class FileOrganizer {
    public static void main(String[] args) {

        // Verificar si hay exactamente 3 argumentos
        if (args.length != 3 && args.length != 4 && args.length != 5) {
            printUsage();
            return;
        }

        String directoryPath = args[0]; // Ruta al directorio que contiene los archivos
        String extension = args[1].toLowerCase(); // Normalizar a minúsculas
        String action = args[2].toLowerCase(); // Normalizar a minúsculas

        // Este bloque de código se asegura de que la extensión de archivo proporcionada
        // como argumento no comience con un punto (.)
        if (extension.startsWith(".")) {
            extension = extension.substring(1);
            System.out.println("deb: " + extension + " -> " + args[1] + "\n");
        }

        File directory = new File(directoryPath);

        // Validar que el directorio exista y sea un directorio
        if (!directory.exists() || !directory.isDirectory()) {
            System.err.println("Error: La ruta '" + directoryPath + "' no existe o no es un directorio válido.");
            return;
        }

        // Validar la acción
        if (!action.equals("list") && !action.equals("move")) {
            System.err.println("Error: Acción '" + action + "' no reconocida. Use 'list' o 'move'.");
            printUsage();
            return;
        }

        System.out.println("Buscando archivos con extensión: ." + extension);
        System.out.println("Procesando directorio: " + directory.getAbsolutePath());
        System.out.println("Acción a realizar: " + action);
        System.out.println("---");

        final String normalizedExtension = extension;

        // Filtrar los archivos en el directorio según la extensión proporcionada
        // y asegurarse de que la extensión sea válida
        File[] files = directory.listFiles((dir, name) -> name.toLowerCase().endsWith("." + normalizedExtension));

        // Verificar si se encontraron archivos con la extensión especificada
        if (files == null || files.length == 0) {
            System.out.println("No se encontraron archivos con la extensión '." + extension + "' en este directorio.");
            return;
        }

        // validar la acción 'move' y la ruta de destino
        String targetDirectoryPath = null;
        if (action.equals("move")) {
            // Verificar si hay exactamente 4 argumentos para la acción 'move'
            if (args.length < 4) {
                System.err.println(
                        "Error: Para la acción 'move', debe proporcionar una ruta de destino como cuarto parámetro.");
                printUsage();
                return;
            }

            targetDirectoryPath = args[3];
            File targetDirectory = new File(targetDirectoryPath);

            // Validar que la ruta de destino exista y sea un directorio
            if ((!targetDirectory.exists() || !targetDirectory.isDirectory()) && args.length != 5) {
                System.err.println("Error: La ruta de destino '" + targetDirectoryPath
                        + "' no existe o no es un directorio válido.");
                return;
            }
        }

        switch (action) {
            case "list":
                System.out.println("Archivos encontrados:\n");
                for (File file : files) {
                    System.out.println("- " + file.getName());
                }
                break;

            case "move":
                System.out.println("Moviendo archivos a: " + targetDirectoryPath + "\n");
                // Crear el directorio de destino si no existe
                int movedCount = 0;
                // Verificar si el directorio de destino existe, si no, crearlo
                if (!Files.exists(Paths.get(targetDirectoryPath)) && args[4].equals("-f")) {
                    try {
                        Files.createDirectories(Paths.get(targetDirectoryPath));
                        System.out.println("Directorio de destino creado: " + targetDirectoryPath);
                    } catch (IOException e) {
                        System.err.println("Error al crear el directorio de destino: " +
                                e.getMessage());
                        return;
                    }
                }

                for (File file : files) {
                    try {
                        Path sourcePath = file.toPath(); // Ruta del archivo fuente
                        // Crear la ruta de destino
                        Path targetPath = Paths.get(targetDirectoryPath, file.getName());
                        // Mover el archivo a la ruta de destino
                        // Si el archivo ya existe en la ruta de destino, se reemplaza
                        Files.move(sourcePath, targetPath, StandardCopyOption.REPLACE_EXISTING);
                        System.out.println("- Movido: " + file.getName());
                        movedCount++;
                    } catch (IOException e) {
                        System.err.println("Error al mover el archivo '" + file.getName() + "': " + e.getMessage());
                    } catch (SecurityException e) {
                        System.err.println("Error de permisos al intentar mover '" + file.getName() + "'.");
                    }
                }
                System.out.println("---");
                System.out.println("Total de archivos movidos: " + movedCount);
                break;
        }
        System.out.println("---");
        System.out.println("Operación completada.");
    }

    // Método para imprimir la ayuda de uso
    private static void printUsage() {
        System.out.println("Uso: java FileOrganizer <directorio> <extension> <accion> [<ruta_destino>]");
        System.out.println("  <directorio> : La ruta al directorio que contiene los archivos.");
        System.out.println("  <extension>  : La extensión de archivo (sin el punto, ej: txt, jpg, pdf).");
        System.out.println(
                "  <accion>     : 'list' para listar los archivos o 'move' para moverlos a una ubicación específica.");
        System.out.println(
                "  [<ruta_destino>] : (Opcional) Requerido solo para 'move'. La ruta al directorio de destino donde se moverán los archivos.");
        System.out.println("\nEjemplos:");
        System.out.println("  java FileOrganizer ./mis_documentos pdf list");
        System.out.println("  java FileOrganizer ./mis_documentos pdf move ./destino");
        System.out.println(
                "  java FileOrganizer \"C:\\Users\\Usuario\\Descargas\" txt move \"C:\\Users\\Usuario\\Documentos\\Destino\"");
    }
}