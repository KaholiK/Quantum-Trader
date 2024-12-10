# src/monitoring/monitor.py

from loguru import logger
import smtplib
from email.mime.text import MIMEText

class Monitor:
    def __init__(self, email_config: dict):
        self.email_config = email_config
    
    def send_email_alert(self, subject: str, message: str):
        try:
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = self.email_config['from_email']
            msg['To'] = self.email_config['to_email']
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['from_email'], self.email_config['password'])
                server.send_message(msg)
            logger.info("Email alert sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def log_event(self, event: str):
        logger.info(event)
