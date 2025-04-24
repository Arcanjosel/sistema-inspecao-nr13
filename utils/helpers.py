"""
Funções utilitárias para o sistema.
"""
import os
import re
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from config.settings import (
    UPLOAD_FOLDER, MAX_FILE_SIZE,
    ALLOWED_EXTENSIONS, BACKUP_PATH
)

logger = logging.getLogger(__name__)

def validate_email(email: str) -> bool:
    """
    Valida o formato de um endereço de e-mail.
    
    Args:
        email: Endereço de e-mail a ser validado
        
    Returns:
        bool: True se o e-mail for válido
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> bool:
    """
    Valida a força de uma senha.
    
    Args:
        password: Senha a ser validada
        
    Returns:
        bool: True se a senha for forte o suficiente
    """
    if len(password) < 8:
        return False
        
    if not re.search(r'[A-Z]', password):
        return False
        
    if not re.search(r'[a-z]', password):
        return False
        
    if not re.search(r'\d', password):
        return False
        
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
        
    return True

def format_date(date: datetime) -> str:
    """
    Formata uma data para exibição.
    
    Args:
        date: Data a ser formatada
        
    Returns:
        str: Data formatada
    """
    return date.strftime('%d/%m/%Y')

def format_datetime(dt: datetime) -> str:
    """
    Formata uma data e hora para exibição.
    
    Args:
        dt: Data e hora a serem formatadas
        
    Returns:
        str: Data e hora formatadas
    """
    return dt.strftime('%d/%m/%Y %H:%M')

def parse_date(date_str: str) -> Optional[datetime]:
    """
    Converte uma string de data para datetime.
    
    Args:
        date_str: String de data no formato dd/mm/yyyy
        
    Returns:
        datetime: Objeto datetime ou None se inválido
    """
    try:
        return datetime.strptime(date_str, '%d/%m/%Y')
    except ValueError:
        return None

def parse_datetime(dt_str: str) -> Optional[datetime]:
    """
    Converte uma string de data e hora para datetime.
    
    Args:
        dt_str: String de data e hora no formato dd/mm/yyyy HH:MM
        
    Returns:
        datetime: Objeto datetime ou None se inválido
    """
    try:
        return datetime.strptime(dt_str, '%d/%m/%Y %H:%M')
    except ValueError:
        return None

def validate_file(file_path: str) -> tuple[bool, str]:
    """
    Valida um arquivo antes do upload.
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        tuple[bool, str]: (True, "") se válido, (False, mensagem) se inválido
    """
    if not os.path.exists(file_path):
        return False, "Arquivo não encontrado"
        
    if os.path.getsize(file_path) > MAX_FILE_SIZE:
        return False, f"Arquivo muito grande. Tamanho máximo: {MAX_FILE_SIZE/1024/1024}MB"
        
    ext = os.path.splitext(file_path)[1][1:].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Tipo de arquivo não permitido. Tipos permitidos: {', '.join(ALLOWED_EXTENSIONS)}"
        
    return True, ""

def save_file(file_path: str, content: bytes) -> tuple[bool, str]:
    """
    Salva um arquivo no diretório de upload.
    
    Args:
        file_path: Caminho do arquivo
        content: Conteúdo do arquivo em bytes
        
    Returns:
        tuple[bool, str]: (True, caminho) se salvo, (False, mensagem) se erro
    """
    try:
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
            
        filename = os.path.basename(file_path)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(save_path, 'wb') as f:
            f.write(content)
            
        return True, save_path
        
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo: {str(e)}")
        return False, f"Erro ao salvar arquivo: {str(e)}"

def backup_database() -> tuple[bool, str]:
    """
    Realiza backup do banco de dados.
    
    Returns:
        tuple[bool, str]: (True, caminho) se backup realizado, (False, mensagem) se erro
    """
    try:
        if not os.path.exists(BACKUP_PATH):
            os.makedirs(BACKUP_PATH)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(BACKUP_PATH, f'backup_{timestamp}.bak')
        
        # Comando para backup do SQL Server
        cmd = f'sqlcmd -S {os.getenv("DB_SERVER")} -U {os.getenv("DB_USERNAME")} ' \
              f'-P {os.getenv("DB_PASSWORD")} -Q "BACKUP DATABASE {os.getenv("DB_NAME")} ' \
              f'TO DISK = \'{backup_file}\' WITH INIT"'
              
        os.system(cmd)
        
        # Remove backups antigos
        cleanup_old_backups()
        
        return True, backup_file
        
    except Exception as e:
        logger.error(f"Erro ao realizar backup: {str(e)}")
        return False, f"Erro ao realizar backup: {str(e)}"

def cleanup_old_backups():
    """Remove backups antigos conforme configuração de retenção."""
    try:
        if not os.path.exists(BACKUP_PATH):
            return
            
        retention_days = int(os.getenv('BACKUP_RETENTION', 7))
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for filename in os.listdir(BACKUP_PATH):
            if filename.startswith('backup_') and filename.endswith('.bak'):
                file_path = os.path.join(BACKUP_PATH, filename)
                file_date = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_date < cutoff_date:
                    os.remove(file_path)
                    logger.info(f"Backup antigo removido: {filename}")
                    
    except Exception as e:
        logger.error(f"Erro ao limpar backups antigos: {str(e)}")

def format_currency(value: float) -> str:
    """
    Formata um valor monetário.
    
    Args:
        value: Valor a ser formatado
        
    Returns:
        str: Valor formatado
    """
    return f'R$ {value:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')

def format_percentage(value: float) -> str:
    """
    Formata um valor percentual.
    
    Args:
        value: Valor a ser formatado
        
    Returns:
        str: Valor formatado
    """
    return f'{value:.2f}%'

def calculate_next_inspection(
    last_inspection: datetime,
    inspection_type: str
) -> datetime:
    """
    Calcula a data da próxima inspeção baseado no tipo.
    
    Args:
        last_inspection: Data da última inspeção
        inspection_type: Tipo da inspeção ('periodica' ou 'extraordinaria')
        
    Returns:
        datetime: Data da próxima inspeção
    """
    if inspection_type == 'periodica':
        return last_inspection + timedelta(days=365)  # 1 ano
    else:
        return last_inspection + timedelta(days=180)  # 6 meses

def validate_pressure(pressure: float) -> bool:
    """
    Valida um valor de pressão.
    
    Args:
        pressure: Valor da pressão em bar
        
    Returns:
        bool: True se o valor for válido
    """
    return 0 < pressure <= 1000  # Pressão máxima de 1000 bar

def validate_temperature(temperature: float) -> bool:
    """
    Valida um valor de temperatura.
    
    Args:
        temperature: Valor da temperatura em °C
        
    Returns:
        bool: True se o valor for válido
    """
    return -273.15 < temperature <= 1000  # Entre 0K e 1000°C 