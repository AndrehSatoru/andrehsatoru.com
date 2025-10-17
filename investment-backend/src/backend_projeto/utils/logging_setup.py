import logging
import json
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Formatter para logs estruturados em JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Adicionar exception info se existir
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Adicionar campos extras
        if hasattr(record, 'request_id'):
            log_data["request_id"] = record.request_id
        if hasattr(record, 'duration'):
            log_data["duration_ms"] = record.duration
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    level: int = logging.INFO,
    output_dir: Optional[Path] = None,
    log_format: str = 'text',
    log_file: Optional[str] = None,
):
    """Configura sistema de logging.
    
    Parâmetros:
        level: Nível de log (logging.DEBUG, INFO, WARNING, ERROR, CRITICAL).
        output_dir: Diretório para arquivo de log (None = sem arquivo).
        log_format: 'text' ou 'json' (estruturado).
        log_file: Nome do arquivo de log (None = padrão).
    """
    # Limpar handlers existentes
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    if log_format == 'json':
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
    handlers.append(console_handler)
    
    # File handler (opcional)
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = log_file or 'investment_api.log'
        file_handler = logging.FileHandler(output_dir / filename, mode='a')
        if log_format == 'json':
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
                )
            )
        handlers.append(file_handler)
    
    # Configurar root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True,
    )
    
    # Silenciar logs verbosos de bibliotecas externas
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('yfinance').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    logging.info(f"Logging configurado: level={logging.getLevelName(level)}, format={log_format}")


def get_logger(name: str) -> logging.Logger:
    """Retorna logger configurado para um módulo."""
    return logging.getLogger(name)
