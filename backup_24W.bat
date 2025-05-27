REM backup_24W.bat "C:\Users\USUARIO\Test" "C:\Users\USUARIO\Test\backup_cmd"
REM cmd.exe /c backup_24W.bat "C:\Users\USUARIO\Test" "C:\Users\USUARIO\Test\backup_cmd"

@echo off
setlocal enabledelayedexpansion

REM Backup de archivos modificados en las últimas 24 horas

REM Parámetros de entrada
set SOURCE_DIR=%1
set BACKUP_DIR=%2

REM Quitar comillas si existen
set SOURCE_DIR=%SOURCE_DIR:"=%
set BACKUP_DIR=%BACKUP_DIR:"=%

REM Mostrar valores de las variables
echo Directorio origen: %SOURCE_DIR%
echo Directorio backup: %BACKUP_DIR%

REM Validaciones básicas
if "%1"=="" (
  echo Uso: %0 [directorio_origen] [directorio_backup]
  exit /b 1
)

REM Verificar si los directorios existen
if not exist "%SOURCE_DIR%" (
  echo Error: El directorio origen no existe: %SOURCE_DIR%
  exit /b 1
)

if not exist "%BACKUP_DIR%" (
  echo Creando directorio de backup: %BACKUP_DIR%
  mkdir "%BACKUP_DIR%"
)

REM Crear archivo de log
set LOG_FILE=%BACKUP_DIR%\backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log
echo %date% %time% - Inicio del backup > "%LOG_FILE%"

REM Contador de archivos
set /a archivos_copiados=0
set /a archivos_omitidos=0

REM Buscar y copiar archivos modificados en las últimas 24 horas
echo Buscando archivos modificados en las últimas 24 horas...
for /f "delims=" %%F in ('dir /b /a-d /s "%SOURCE_DIR%\*.*" ^| findstr /v "\\$"') do (
  if exist "%%F" (
    for /f "tokens=1-3 delims= " %%a in ('dir /tc "%%F" ^| findstr /v "^$" ^| findstr /v "^[A-Z]"') do (
      set "fecha=%%a"
      set "hora=%%b"
      set "archivo=%%F"
      
      REM Verificar si el archivo fue modificado en las últimas 24 horas
      for /f "tokens=1-3 delims=/" %%x in ("!fecha!") do (
        set "dia=%%x"
        set "mes=%%y"
        set "anio=%%z"
      )
      
      REM Obtener la fecha actual
      for /f "tokens=1-3 delims=/" %%x in ("%date%") do (
        set "dia_actual=%%x"
        set "mes_actual=%%y"
        set "anio_actual=%%z"
      )
      
      REM Si el archivo fue modificado hoy, copiarlo
      if "!anio!"=="!anio_actual!" if "!mes!"=="!mes_actual!" if "!dia!"=="!dia_actual!" (
        echo Copiando: !archivo! >> "%LOG_FILE%"
        copy "!archivo!" "%BACKUP_DIR%\" > nul
        if !errorlevel! equ 0 (
          echo [OK] Archivo copiado: !archivo!
          set /a archivos_copiados+=1
        ) else (
          echo [ERROR] No se pudo copiar: !archivo! >> "%LOG_FILE%"
          set /a archivos_omitidos+=1
        )
      )
    )
  )
)

echo.
echo Resumen del backup:
echo - Archivos copiados exitosamente: %archivos_copiados%
echo - Archivos omitidos: %archivos_omitidos%
echo.
echo %date% %time% - Backup completado. >> "%LOG_FILE%"
echo Backup completado. Revisa el archivo de log: %LOG_FILE%

endlocal
