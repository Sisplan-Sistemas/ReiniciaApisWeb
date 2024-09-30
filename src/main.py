import schedule as a
from time import sleep
from services.service_manager import ServiceManager
from utils.logger import cria_log_txt
from utils.error_handler import log_error
from utils.messenger import send_message_to_sispemail, send_message_to_telegram
from requests import get
from os import path, getenv
from sys import executable
from dotenv import load_dotenv
from asyncio import run


load_dotenv()
class RestartService:
    def __init__(self):
        self.username_service = getenv("SERVICE_USERNAME")
        self.password_service = getenv("SERVICE_PASSWORD")
        self.emp_name = getenv("EMP_NAME")
        self.manager = ServiceManager(self.username_service, self.password_service)
        self.make_requests_running = False
        self.is_updating = False
        run(send_message_to_telegram(f"Bot funcionando pro cliente *{self.emp_name.upper()}*"))

    def make_requests(self):
        unresponsive_apis = []
        if self.is_updating:
            send_message_to_sispemail([], f"⚠ Atenção ⚠\\n$OLA$!\\nNão foi possível executar a rotina de fazer requisições no cliente *{self.emp_name.upper()}* devido a estarem atualizando o Sisplan WEB!")
            run(send_message_to_telegram(f"⚠ Atenção ⚠\\nNão foi possível executar a rotina de fazer requisições no cliente *{self.emp_name.upper()}* devido a estarem atualizando o Sisplan WEB"))
            return
        self.make_requests_running = True
        try:
            for service in self.manager.services_api_web:
                port = service.replace('Sisplan_Api_Web_', '')
                try:
                    response = get(url=f"http://127.0.0.1:{port}/healthcheck")
                    if response.status_code != 200:
                        unresponsive_apis.append(service)
                except:
                    unresponsive_apis.append(service)
            if unresponsive_apis:
                 self.manager.restart_services('make_requests', unresponsive_apis)
        except Exception as e:
            log_error(e, "Erro ao testar conexão das API's")
            send_message_to_sispemail([], f"⚠ Atenção ⚠ \\n$OLA$!\\nOcorreu um erro ao testar a conexão das API's no cliente *{self.emp_name.upper()}*. \\nPor favor, verifique!")
            run(send_message_to_telegram(f"⚠ Atenção ⚠ \\nOcorreu um erro ao testar a conexão das API's no cliente *{self.emp_name.upper()}*\\nPor favor, verifique"))
        finally:
            self.make_requests_running = False
            run(send_message_to_telegram(f"Rotina de fazer requisições concluída no cliente *{self.emp_name.upper()}*"))

    def main(self):
        a.every(0.10).minutes.do(self.make_requests)
        cria_log_txt("Agendamento da tarefa de checar as API's a cada 2 minutos feito.")
        a.every().day.at("22:00").do(lambda: self.manager.restart_services('restart_services'))
        cria_log_txt("Agendamento da tarefa de reiniciar as API's diariamente às 22:00 horas feito.")
        way_to_text_file = path.join(path.abspath(path.join(path.dirname(__file__), '..')), 'atualizacao_web.txt')
        while True:
            self.is_updating = 'true' in open(way_to_text_file, 'r').readlines()
            a.run_pending()
            sleep(30)

if __name__ == '__main__':
    restart_service = RestartService()
    restart_service.main()