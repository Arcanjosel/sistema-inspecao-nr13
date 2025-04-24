"""
Serviço de envio de e-mails para notificações.
"""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv
from database.connection import DatabaseConnection

logger = logging.getLogger(__name__)

class EmailService:
    """
    Serviço responsável pelo envio de e-mails de notificação.
    """
    
    def __init__(self):
        load_dotenv()
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL')
        self.db = DatabaseConnection()
        
    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Envia um e-mail.
        
        Args:
            to_email: Email do destinatário
            subject: Assunto do e-mail
            body: Corpo do e-mail
            
        Returns:
            bool: True se e-mail enviado com sucesso
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            logger.info(f"E-mail enviado para {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail: {str(e)}")
            return False
            
    def send_inspection_reminder(self, days_before: int = 30) -> bool:
        """
        Envia lembretes de inspeções próximas.
        
        Args:
            days_before: Número de dias de antecedência para enviar o lembrete
            
        Returns:
            bool: True se todos os e-mails foram enviados com sucesso
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Busca inspeções próximas
            cursor.execute("""
                SELECT i.*, e.codigo_projeto, e.localizacao,
                       u.email, u.nome
                FROM inspecoes i
                JOIN equipamentos e ON i.equipamento_id = e.id
                JOIN usuarios u ON e.empresa = u.empresa
                WHERE i.proxima_inspecao BETWEEN ? AND ?
                AND u.tipo = 'cliente'
            """, (
                datetime.now(),
                datetime.now() + timedelta(days=days_before)
            ))
            
            inspections = cursor.fetchall()
            success = True
            
            for insp in inspections:
                subject = f"Lembrete: Inspeção NR-13 - {insp.codigo_projeto}"
                
                body = f"""
                Prezado(a) {insp.nome},
                
                Este é um lembrete sobre a próxima inspeção do equipamento:
                
                Código: {insp.codigo_projeto}
                Localização: {insp.localizacao}
                Data da Próxima Inspeção: {insp.proxima_inspecao.strftime('%d/%m/%Y')}
                Tipo: {insp.tipo_inspecao}
                
                Por favor, entre em contato com nossa equipe para agendar a inspeção.
                
                Atenciosamente,
                Equipe de Inspeções NR-13
                """
                
                if not self._send_email(insp.email, subject, body):
                    success = False
                    
            return success
            
        except Exception as e:
            logger.error(f"Erro ao enviar lembretes: {str(e)}")
            return False
            
        finally:
            cursor.close()
            
    def send_inspection_report(self, inspecao_id: int) -> bool:
        """
        Envia relatório de inspeção por e-mail.
        
        Args:
            inspecao_id: ID da inspeção
            
        Returns:
            bool: True se e-mail enviado com sucesso
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Busca dados da inspeção
            cursor.execute("""
                SELECT i.*, e.codigo_projeto, e.localizacao,
                       u.email, u.nome, r.link_arquivo
                FROM inspecoes i
                JOIN equipamentos e ON i.equipamento_id = e.id
                JOIN usuarios u ON e.empresa = u.empresa
                LEFT JOIN relatorios r ON i.id = r.inspecao_id
                WHERE i.id = ?
            """, (inspecao_id,))
            
            insp = cursor.fetchone()
            
            if not insp:
                logger.error(f"Inspeção {inspecao_id} não encontrada")
                return False
                
            subject = f"Relatório de Inspeção NR-13 - {insp.codigo_projeto}"
            
            body = f"""
            Prezado(a) {insp.nome},
            
            Segue o relatório da inspeção realizada:
            
            Código: {insp.codigo_projeto}
            Localização: {insp.localizacao}
            Data da Inspeção: {insp.data_inspecao.strftime('%d/%m/%Y')}
            Tipo: {insp.tipo_inspecao}
            Engenheiro Responsável: {insp.engenheiro_responsavel}
            Resultado: {insp.resultado}
            
            Link do Relatório: {insp.link_arquivo}
            
            Recomendações:
            {insp.recomendacoes}
            
            Próxima Inspeção: {insp.proxima_inspecao.strftime('%d/%m/%Y')}
            
            Atenciosamente,
            Equipe de Inspeções NR-13
            """
            
            return self._send_email(insp.email, subject, body)
            
        except Exception as e:
            logger.error(f"Erro ao enviar relatório: {str(e)}")
            return False
            
        finally:
            cursor.close() 