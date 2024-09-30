from traceback import format_exc
from .logger import cria_log_txt

def log_error(error, context=""):
    error_message = format_exc()
    cria_log_txt(f"{context}. Erro: {error}")
    cria_log_txt(f"Mais detalhes do error: {error_message}")