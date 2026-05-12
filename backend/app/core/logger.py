from datetime import datetime

# Buffer global para logs visibles vía API
DEBUG_LOGS = []

def add_debug_log(message: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    DEBUG_LOGS.append(log_entry)
    # Mantener solo los últimos 100 logs
    if len(DEBUG_LOGS) > 100:
        DEBUG_LOGS.pop(0)
    
    # También imprimir en consola para los logs de Render
    print(log_entry)
