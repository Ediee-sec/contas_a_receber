from pathlib import Path
import sys
import os
sys.path.append(str(Path(__file__).resolve().parents[3]))
from source.modules.backend.tranform import Transformer
from source.modules.backend.email.sendmail import Mail
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import time
import configparser
import pandas as pd

class ListContacts:
    def __init__(self, file) -> None:
        self.__df = Transformer(file).transform_dataframe()
        
    def __filter_contacts(self):
        """
        Filtra a lista de contatos para somente incluir os que possuem validacao OK
        Retorna um dataframe filtrado com os contatos validos.
        
        Returns: pd.DataFrame
        """
        df_filtrado = self.__df.loc[self.__df["Validação"] == "OK"]
        return df_filtrado
    
    def list_contacts(self):
        return self.__filter_contacts()

class Mola:
    def __init__(self, file, message, email) -> None:
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--incognito')
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-notifications')
        self.driver = None
        self.portal = 'https://mola.kinbox.com.br/user/login'
        
        # Para excutar localmente
        # self.config = configparser.ConfigParser()
        # self.config.read(os.path.join(Path(__file__).resolve().parents[3], 'config\\access.ini'))
        # self.username = self.config['credentials']['username'] 
        # self.password = self.config['credentials']['password']
        
        # Para executar no docker
        self.username = os.getenv('USER')
        self.password = os.getenv('PWD')
        
        self.contacts = ListContacts(file).list_contacts()
        self.message = message
        self.email = email
        self.status = pd.DataFrame(columns=['Nome', 'Telefone', 'Status'])
        
        
    def login(self):
        """
        Realiza o login na plataforma Mola.
        
        Abre o driver do chrome com as opcoes de incognito.
        Acessa a pagina do portal Mola.
        Encontra e preenche os campos de usuario e senha com os valores
        configurados no arquivo access.ini.
        Clica no botao de login.
        """
        try:
            self.driver = webdriver.Chrome(options=self.options)
            self.driver.get(self.portal)
            time.sleep(3)
            self.driver.find_element('xpath','//*[@id="email"]').send_keys(self.username)
            self.driver.find_element('xpath','//*[@id="password"]').send_keys(self.password)
            self.driver.find_element('xpath','//*[@id="root"]/div/div[2]/form/div[3]/button').click()
            time.sleep(3)
            print('Login realizado com sucesso')
        except Exception as e:
            raise print(e)
    
    def disconnect_session(self):
        """
        Encerra a sessao atual do usuario na plataforma Mola.
        
        Utiliza o WebDriverWait para aguardar ate que o elemento do botao de desconectar esteja presente na pagina.
        Clica no botao para desconectar a sessao atual.
        Se o elemento nao for encontrado, ignora a excecao e continua a execucao.
        """
        time.sleep(3)
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div[2]/div/div[2]/div/div/div[2]/div/button'))
            )
            element.click()
            time.sleep(3)
        except TimeoutException:
            pass
        
    def send_message(self, number, name):
        """
        Envia uma mensagem para o numero de telefone especificado.
        
        Clica no botao de adicionar contato.
        Preenche o campo de plataforma com o valor 'ATIVO'.
        Preenche o campo de telefone com o numero especificado.
        Preenche o campo de mensagem com um texto padrao, incluindo o nome do contato.
        """
        try:
            self.driver.find_element('xpath','//*[@id="root"]/div/div[1]/div/div[2]/div/div[1]/div[1]/div/div[1]/div/div/div[2]/button').click()
            time.sleep(2)
            self.driver.find_element('xpath','//*[@id="workspacePlatformId"]').send_keys('ATIVO')
            self.driver.find_element('xpath','//*[@id="workspacePlatformId"]').send_keys(Keys.ENTER)
            self.driver.find_element('xpath','//*[@id="phone"]').send_keys(number)
            self.driver.find_element('xpath','/html/body/div[6]/div/div[2]/div/div[2]/div[2]/div/form/div[4]/div/div/div/div/div/div/div/div/form/textarea').send_keys(f'Olá {name} tudo bem?\n\n {self.message}')
            self.driver.find_element('xpath','/html/body/div[6]/div/div[2]/div/div[2]/div[3]/div/button').click()
            
            self.status = pd.concat([self.status, pd.DataFrame({'Nome': [name], 'Telefone': [number], 'Status': ['Sucesso']})], ignore_index=True)
        except Exception as e:
            self.status = pd.concat([self.status, pd.DataFrame({'Nome': [name], 'Telefone': [number], 'Status': ['Erro']})], ignore_index=True)
        
    def scroll_all_contacts(self):
        """
        Itera sobre a lista de contatos e envia uma mensagem para cada um deles.
        
        Utiliza o metodo send_message para enviar uma mensagem para cada contato na lista.
        O metodo send_message e responsavel por clicar no botao de adicionar contato,
        preencher o campo de plataforma com o valor 'ATIVO', preencher o campo de telefone
        com o numero especificado, preencher o campo de mensagem com um texto padrao,
        incluindo o nome do contato e, por fim, clicar no botao de enviar mensagem.
        """
        for index, row in self.contacts.iterrows():
            self.send_message(row['Celular'], row['Nome'])
        
        

        
    def flow(self):  
        """
        Executa o fluxo de envio de mensagens para todos os contatos na lista.
        
        Realiza o login na plataforma Mola, desconecta a sessao atual,
        envia uma mensagem para cada contato na lista e, por fim, fecha o driver.
        Se ocorrer algum erro durante a execucao, imprime o erro e fecha o driver.
        """
        try:
            self.login()
            self.disconnect_session()
            self.scroll_all_contacts()
            Mail(self.status, self.email).send_mail()
        except Exception as e:
            print(e)
        finally:
            self.disconnect_session()
            self.driver.close()

        
# job = Mola('C:\\Users\\emers\\OneDrive\\Documentos\\15.xlsx', 'Mensagem de teste', 'emersonrox8@gmail.com')
# job.flow()
