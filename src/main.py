from dotenv import load_dotenv
import os
import schedule as a
from time import sleep
from services.service_manager import ServiceManager
from utils.logger import cria_logtxt
from utils.error_handler import log_error
from requests import get

load_dotenv()

class RestartService:
    def __init__(self):
        self.username_service = os.getenv("SERVICE_USERNAME", "default_username")
        self.password_service = os.getenv("SERVICE_PASSWORD", "default_password")
        self.manager = ServiceManager(self.username_service, self.password_service)
        self.make_requests_running = False
        self.is_updating = False

    def make_requests(self):
        list_unresponsive_apis = []
        self.make_requests_running = True
        try:
            for service in self.manager.services_api_web:
                port = service.replace('Sisplan_Api_Web_', '')
                try:
                    response = get(url=f"http://127.0.0.1:{port}/healthcheck")
                    if response.status_code != 200:
                        list_unresponsive_apis.append(service)
                except:
                    list_unresponsive_apis.append(service)
            if list_unresponsive_apis:
                self.manager.restart_services()
        except Exception as e:
            log_error(e, "Erro ao testar conexão das API's")
        finally:
            self.make_requests_running = False

    def main(self):
        a.every(2).minutes.do(self.make_requests)
        cria_logtxt("Agendamento da tarefa de checar as API's a cada 2 minutos.")
        a.every().day.at("22:00").do(self.manager.restart_services)
        cria_logtxt("Agendamento da tarefa de reiniciar as API's diariamente às 22:00 horas.")

        while True:
            self.is_updating = 'true' in open('atualizacao_web.txt', 'r').readlines()
            a.run_pending()
            sleep(30)

if __name__ == '__main__':
    restart_service = RestartService()
    restart_service.main()