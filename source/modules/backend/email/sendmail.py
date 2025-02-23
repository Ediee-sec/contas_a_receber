import pandas as pd
import smtplib
import configparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import os


class Mail:
    def __init__(self, df, to):
        self.df = df
        self.to = to
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(Path(__file__).resolve().parents[4], 'config\\access.ini'))
        self.email = self.config['gmail']['email']
        self.password = self.config['gmail']['key']
        self.server = smtplib.SMTP(self.config['gmail']['server'], self.config['gmail']['port'])
        self.subject = 'Resultado do envio de menssagens no Mola'
    
    def create_template(self):
        df = self.df
        
        def style_status(status):
            return f'status-{status.lower()}' if status in ['Sucesso', 'Erro'] else ''
        
        def style():
            with open(os.path.join(Path(__file__).resolve().parents[3], 'modules\\backend\\email\\template\\static\\style.css'), 'r') as f:
                return f.read()
            
        df_styled = df.copy()
        df_styled['Status'] = df_styled['Status'].apply(lambda x: f'<span class="{style_status(x)}">{x}</span>')
        
        
        df_html = df_styled.to_html(
            index=False,
            classes='data-table',
            escape=False
        )
        df_html = df_html.replace('<tr style="text-align: right;">', '<tr>')
        df_html = df_html.replace('border="1"', '')
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        {style()}
        </style>
        </head>
        <body>
        {df_html}
        </body>
        </html>
        """
        
        return template
  
    
    def send_mail(self):
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = self.to
        msg['Subject'] = self.subject
        
        msg.attach(MIMEText(self.create_template(), 'html'))
        
        try:
            self.server.starttls()
            self.server.login(self.email, self.password)
            self.server.sendmail(self.email, self.to, msg.as_string())
            self.server.quit()
            print('Email enviado com sucesso')
        except Exception as e:
            print(f'Erro ao enviar email: {e}')