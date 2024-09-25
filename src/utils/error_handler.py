from traceback import format_exc
from .logger import cria_logtxt

def log_error(error, context=""):
    error_message = format_exc()
    cria_logtxt(f"{context}. Erro: {error}")
    cria_logtxt(f"Mais detalhes do error: {error_message}")