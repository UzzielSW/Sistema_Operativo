#!/bin/bash
# ./backup_24.sh . ./backup_linux/
# Backup de archivos modificados en las últimas 24 horas

# Parámetros de entrada
SOURCE_DIR="$1"
BACKUP_DIR="$2"
LOG_FILE="${BACKUP_DIR}/backup_24_$(date +'%Y%m%d').log"

# Contadores
declare -i COPIED_FILES=0
declare -i SKIPPED_FILES=0

# Validaciones
if [ $# -ne 2 ]; then
    echo "Uso: $0 <directorio_origen> <directorio_backup>"
    exit 1
fi

# Mostrar directorios
echo "Directorio origen: $SOURCE_DIR"
echo "Directorio backup: $BACKUP_DIR"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: El directorio origen no existe: $SOURCE_DIR"
    exit 1
fi

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Creando directorio de backup: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
fi

# Crear archivo de log
# Asegurarse de que el log se inicialice correctamente y no se escriba antes de tiempo
echo "$(date) - Inicio del backup" > "$LOG_FILE"

# Buscar y copiar archivos modificados en las últimas 24 horas
# Evitar cualquier escritura temprana del mensaje de finalización
echo "Buscando archivos modificados en las últimas 24 horas..."

# Buscar archivos modificados hoy
while IFS= read -r file; do
    if [ -f "$file" ]; then
        echo "Copiando: $file" >> "$LOG_FILE"
        if cp "$file" "$BACKUP_DIR"; then
            echo "[OK] Archivo copiado: $file"
            COPIED_FILES+=1
        else
            echo "[ERROR] No se pudo copiar: $file" >> "$LOG_FILE"
            SKIPPED_FILES+=1
        fi
    fi
done < <(find "$SOURCE_DIR" -type f -mtime -1)

# Mostrar resumen
echo
echo "Resumen del backup:"
echo "- Archivos copiados exitosamente: $COPIED_FILES"
echo "- Archivos omitidos: $SKIPPED_FILES"
echo

# Finalizar log
# Confirmar que el mensaje de finalización solo se escriba una vez al final
echo "$(date) - Backup completado." >> "$LOG_FILE"