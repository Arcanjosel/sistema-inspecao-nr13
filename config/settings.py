"""
Configurações globais do sistema.
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do banco de dados
DB_SERVER = os.getenv('DB_SERVER', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'sistema_inspecao')
DB_USERNAME = os.getenv('DB_USERNAME', 'sa')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

# Configurações de e-mail
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', '')

# Configurações de notificação
DAYS_BEFORE_REMINDER = int(os.getenv('DAYS_BEFORE_REMINDER', 30))
REMINDER_HOUR = os.getenv('REMINDER_HOUR', '08:00')

# Configurações de log
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/sistema.log')

# Configurações da interface
WINDOW_TITLE = os.getenv('WINDOW_TITLE', 'Sistema de Inspeções NR-13')
WINDOW_WIDTH = int(os.getenv('WINDOW_WIDTH', 1200))
WINDOW_HEIGHT = int(os.getenv('WINDOW_HEIGHT', 800))

# Configurações de segurança
PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', 8))
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 30))  # em minutos

# Configurações de relatórios
REPORT_TEMPLATE_PATH = os.getenv('REPORT_TEMPLATE_PATH', 'templates/relatorio.html')
REPORT_OUTPUT_PATH = os.getenv('REPORT_OUTPUT_PATH', 'relatorios/')

# Configurações de armazenamento
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads/')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))  # 10MB
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx',
    'jpg', 'jpeg', 'png', 'tiff'
}

# Configurações de backup
BACKUP_PATH = os.getenv('BACKUP_PATH', 'backups/')
BACKUP_INTERVAL = int(os.getenv('BACKUP_INTERVAL', 24))  # em horas
BACKUP_RETENTION = int(os.getenv('BACKUP_RETENTION', 7))  # em dias 