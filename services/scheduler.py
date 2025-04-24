"""
Serviço de agendamento de tarefas.
"""
import schedule
import time
import logging
from datetime import datetime
from services.email_service import EmailService

logger = logging.getLogger(__name__)

class Scheduler:
    """
    Classe responsável por agendar e executar tarefas periódicas.
    """
    
    def __init__(self):
        self.email_service = EmailService()
        
    def start(self):
        """Inicia o agendador de tarefas."""
        try:
            # Agenda envio de lembretes diariamente às 8h
            schedule.every().day.at("08:00").do(self._send_reminders)
            
            logger.info("Agendador iniciado")
            
            while True:
                schedule.run_pending()
                time.sleep(60)
                
        except Exception as e:
            logger.error(f"Erro no agendador: {str(e)}")
            
    def _send_reminders(self):
        """Envia lembretes de inspeções próximas."""
        try:
            logger.info("Iniciando envio de lembretes")
            
            if self.email_service.send_inspection_reminder():
                logger.info("Lembretes enviados com sucesso")
            else:
                logger.error("Falha ao enviar lembretes")
                
        except Exception as e:
            logger.error(f"Erro ao enviar lembretes: {str(e)}")
            
    def schedule_inspection_report(self, inspecao_id: int, send_date: datetime):
        """
        Agenda o envio de um relatório de inspeção.
        
        Args:
            inspecao_id: ID da inspeção
            send_date: Data para envio do relatório
        """
        try:
            schedule.every().day.at(send_date.strftime("%H:%M")).do(
                self._send_inspection_report, inspecao_id
            )
            
            logger.info(f"Relatório da inspeção {inspecao_id} agendado para {send_date}")
            
        except Exception as e:
            logger.error(f"Erro ao agendar relatório: {str(e)}")
            
    def _send_inspection_report(self, inspecao_id: int):
        """Envia um relatório de inspeção."""
        try:
            logger.info(f"Enviando relatório da inspeção {inspecao_id}")
            
            if self.email_service.send_inspection_report(inspecao_id):
                logger.info(f"Relatório da inspeção {inspecao_id} enviado com sucesso")
            else:
                logger.error(f"Falha ao enviar relatório da inspeção {inspecao_id}")
                
        except Exception as e:
            logger.error(f"Erro ao enviar relatório: {str(e)}")
            
    def clear_schedule(self):
        """Limpa todos os agendamentos."""
        try:
            schedule.clear()
            logger.info("Agendamentos limpos")
            
        except Exception as e:
            logger.error(f"Erro ao limpar agendamentos: {str(e)}") 