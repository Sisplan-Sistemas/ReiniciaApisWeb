import win32service as w
import win32serviceutil as wsu
from time import sleep
from .api_service import restart_single_service
from utils.logger import cria_log_txt
from requests import get
from utils.messenger import send_message_to_sispemail, send_message_to_telegram
from asyncio import run
from os import getenv

class ServiceManager:
    def __init__(self, username_service, password_service):
        self.services_api_web = []
        self.service_nginx = ''
        self.desired_access = w.SERVICE_CHANGE_CONFIG | w.SERVICE_START | w.SERVICE_STOP | w.SERVICE_QUERY_STATUS
        self.username_service = username_service
        self.password_service = password_service
        self.detect_services()
        self.emp_name = getenv('EMP_NAME')

    def detect_services(self):
        service_manager = w.OpenSCManager(None, None, w.SC_MANAGER_ALL_ACCESS)
        try:
            for service in w.EnumServicesStatus(service_manager, w.SERVICE_WIN32):
                if 'Sisplan_Api_Web' in service[0]:
                    self.services_api_web.append(service[0])
                if 'NGINX' in service[0].upper():
                    self.service_nginx = service[0]
            cria_log_txt(f"Encontrado os serviços -> [{', '.join(self.services_api_web)}] <- instalados.")
        finally:
            w.CloseServiceHandle(service_manager)

    def restart_services(self, function: str, list_unresponsive_apis = [], is_updating = False):
        if is_updating:
            send_message_to_sispemail([], f"⚠ Atenção ⚠\\n$OLA$!\\nNão foi possível executar a rotina de reinstalar os serviços no cliente *{self.emp_name.upper()}* devido a estarem atualizando o Sisplan WEB!")
            run(send_message_to_telegram(f"⚠ Atenção ⚠\\nNão foi possível executar a rotina de reinstalar os serviços no cliente *{self.emp_name.upper()}* devido a estarem atualizando o Sisplan WEB"))
            return
        if function == 'make_requests':
            cria_log_txt("Verificado que existem API's sem comunicar, reiniciando...")
        else:
            cria_log_txt("Iniciando rotina diária para reiniciar as API's web")
        try:
            if list_unresponsive_apis:
                for service in list_unresponsive_apis:
                    restart_single_service(service, self.username_service, self.password_service)
            else:
                for service in self.services_api_web:
                    restart_single_service(service, self.username_service, self.password_service)
            if function == 'make_requests':
                cria_log_txt("Rotina de reiniciar as API's que estavam sem comunicar completa")
            else:    
                cria_log_txt("Rotina de reiniciar as API's diariamente completa")
        finally:
            if not is_updating:
                self.test_services()
                run(send_message_to_telegram(f'Rotina de reinstalar os serviços no cliente *{self.emp_name.upper()}* completa'))

    def check_nginx_and_start(self, sv_manager):
        if self.service_nginx:
            try:
                s_nginx = w.OpenService(sv_manager, self.service_nginx, self.desired_access)
                status_nginx = w.QueryServiceStatus(self.service_nginx)

                if status_nginx[1] == w.SERVICE_STOPPED:
                    cria_log_txt("Nginx estava parado, iniciando...")
                    wsu.StartService(self.service_nginx)
            finally:
                w.CloseServiceHandle(s_nginx)

    def test_services(self):
        try:
            list_unresponsive_services = []
            for api_web in self.services_api_web:
                try:
                    port = api_web.replace('Sisplan_Api_Web_', '')
                    res = get(url=f"http://127.0.0.1:{port}/healthcheck")
                    if res.status_code != 200:
                        list_unresponsive_services.append(api_web)
                except:
                    list_unresponsive_services.append(api_web)
        finally:
            if len(list_unresponsive_services) > 0:
                send_message_to_sispemail(list_unresponsive_services)
                run(send_message_to_telegram(f"Existem serviços que não passaram no teste de serviços após a rotina de reinstalar no cliente *{self.emp_name.upper()}*\\nPor favor, verifique\\nServiços: {', '.join(list_unresponsive_services)}"))