
# -*- coding: utf-8 -*-
"""
Sistema de alertas para erros críticos
"""

import smtplib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict, deque

class AlertManager:
    """Gerenciador de alertas do sistema"""
    
    def __init__(self):
        self.config_path = Path(__file__).parent.parent.parent / "config" / "alert_config.json"
        self.alert_history = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.last_alert_time = defaultdict(lambda: datetime.min)
        
        self._load_config()
    
    def _load_config(self):
        """Carrega configuração de alertas"""
        default_config = {
            "email_alerts": {
                "enabled": False,
                "smtp_server": "localhost",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_email": "dac-system@localhost",
                "to_emails": []
            },
            "alert_rules": {
                "critical_error_threshold": 5,
                "error_rate_threshold": 10,
                "time_window_minutes": 15,
                "cooldown_minutes": 30
            },
            "log_alerts": {
                "enabled": True,
                "log_file": "alerts.log"
            }
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.config_path.parent.mkdir(exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def send_alert(self, severity: str, message: str, details: Dict = None):
        """Envia alerta baseado na severidade"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "message": message,
            "details": details or {}
        }
        
        self.alert_history.append(alert)
        
        # Verificar se deve enviar alerta
        if self._should_send_alert(severity, message):
            if self.config["email_alerts"]["enabled"]:
                self._send_email_alert(alert)
            
            if self.config["log_alerts"]["enabled"]:
                self._log_alert(alert)
    
    def _should_send_alert(self, severity: str, message: str) -> bool:
        """Verifica se deve enviar alerta baseado nas regras"""
        now = datetime.now()
        cooldown = timedelta(minutes=self.config["alert_rules"]["cooldown_minutes"])
        
        # Verificar cooldown
        alert_key = f"{severity}:{message}"
        if now - self.last_alert_time[alert_key] < cooldown:
            return False
        
        # Atualizar último alerta
        self.last_alert_time[alert_key] = now
        
        # Sempre alertar para erros críticos
        if severity == "CRITICAL":
            return True
        
        # Verificar taxa de erros
        time_window = timedelta(minutes=self.config["alert_rules"]["time_window_minutes"])
        recent_errors = sum(1 for alert in self.alert_history 
                          if datetime.fromisoformat(alert["timestamp"]) > now - time_window
                          and alert["severity"] in ["ERROR", "CRITICAL"])
        
        return recent_errors >= self.config["alert_rules"]["error_rate_threshold"]
    
    def _send_email_alert(self, alert: Dict):
        """Envia alerta por email"""
        try:
            config = self.config["email_alerts"]
            
            msg = MIMEMultipart()
            msg['From'] = config["from_email"]
            msg['To'] = ", ".join(config["to_emails"])
            msg['Subject'] = f"DAC Alert - {alert['severity']}: {alert['message']}"
            
            body = f"""
Alerta do Sistema DAC

Severidade: {alert['severity']}
Mensagem: {alert['message']}
Timestamp: {alert['timestamp']}

Detalhes:
{json.dumps(alert['details'], indent=2, ensure_ascii=False)}
"""
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            if config["username"]:
                server.starttls()
                server.login(config["username"], config["password"])
            
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            print(f"Erro ao enviar email de alerta: {e}")
    
    def _log_alert(self, alert: Dict):
        """Registra alerta em arquivo de log"""
        try:
            log_path = Path(__file__).parent.parent.parent / "logs" / "alerts.log"
            log_path.parent.mkdir(exist_ok=True)
            
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"{json.dumps(alert, ensure_ascii=False)}
")
                
        except Exception as e:
            print(f"Erro ao registrar alerta: {e}")

# Instância global
_alert_manager = None

def get_alert_manager():
    """Retorna instância do gerenciador de alertas"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager
