import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;


public class FileOrganizer {
    public static void main(String[] args) {
        // Verificar si hay exactamente 3 argumentos
        if (args.length != 3) {
            printUsage();
            return;
        }

        String directoryPath = args[0];
        String extension = args[1].toLowerCase(); // Normalizar a minúsculas
        String action = args[2].toLowerCase(); // Normalizar a minúsculas

        // Asegurarse que la extensión no tenga un punto inicial (se añade luego si es necesario)
        if (extension.startsWith(".")) {
            extension = extension.substring(1);
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
File[] files = directory.listFiles((dir, name) -> name.toLowerCase().endsWith("." + normalizedExtension));
        //File[] files = directory.listFiles((dir, name) -> name.toLowerCase().endsWith("." + extension));

        if (files == null || files.length == 0) {
            System.out.println("No se encontraron archivos con la extensión '." + extension + "' en este directorio.");
            return;
        }

        switch (action) {
            case "list":
                System.out.println("Archivos encontrados:");
                for (File file : files) {
                    System.out.println("- " + file.getName());
                }
                break;

            case "move":
                Path targetSubdirPath = Paths.get(directoryPath, extension + "_files");
                try {
                    // Crear el subdirectorio si no existe
                    if (!Files.exists(targetSubdirPath)) {
                        Files.createDirectories(targetSubdirPath);
                        System.out.println("Subdirectorio creado: " + targetSubdirPath.toString());
                    } else if (!Files.isDirectory(targetSubdirPath)) {
                         System.err.println("Error: Ya existe un archivo (no directorio) con el nombre: " + targetSubdirPath.getFileName());
                         return;
                    }

                    System.out.println("Moviendo archivos a: " + targetSubdirPath.toString());
                    int movedCount = 0;
                    for (File file : files) {
                        try {
                            Path sourcePath = file.toPath();
                            Path targetPath = targetSubdirPath.resolve(file.getName());
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

                } catch (IOException e) {
                    System.err.println("Error al crear el subdirectorio '" + targetSubdirPath.toString() + "': " + e.getMessage());
                } catch (SecurityException e) {
                     System.err.println("Error de permisos al intentar crear el subdirectorio '" + targetSubdirPath.toString() + "'.");
                }
                break;
        }
         System.out.println("---");
         System.out.println("Operación completada.");
    }

    private static void printUsage() {
        System.out.println("Uso: java FileOrganizer <directorio> <extension> <accion>");
        System.out.println("  <directorio> : La ruta al directorio que contiene los archivos.");
        System.out.println("  <extension>  : La extensión de archivo (sin el punto, ej: txt, jpg, pdf).");
        System.out.println("  <accion>     : 'list' para listar los archivos o 'move' para moverlos a una subcarpeta.");
        System.out.println("\nEjemplos:");
        System.out.println("  java FileOrganizer ./mis_documentos pdf move");
        System.out.println("  java FileOrganizer \"C:\\Users\\Usuario\\Descargas\" txt list");
    }
}
