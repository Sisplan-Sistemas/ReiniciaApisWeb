import win32service as w
import win32serviceutil as wsu
from time import sleep
from .api_service import restart_single_service
from utils.logger import cria_logtxt

class ServiceManager:
    def __init__(self, username_service, password_service):
        self.services_api_web = []
        self.service_nginx = ''
        self.desired_access = w.SERVICE_CHANGE_CONFIG | w.SERVICE_START | w.SERVICE_STOP | w.SERVICE_QUERY_STATUS
        self.username_service = username_service
        self.password_service = password_service
        self.detect_services()

    def detect_services(self):
        service_manager = w.OpenSCManager(None, None, w.SC_MANAGER_ALL_ACCESS)
        try:
            for service in w.EnumServicesStatus(service_manager, w.SERVICE_WIN32):
                if 'Sisplan_Api_Web' in service[0]:
                    self.services_api_web.append(service[0])
                if 'NGINX' in service[0].upper():
                    self.service_nginx = service[0]
            cria_logtxt(f"Encontrado os serviços -> [{', '.join(self.services_api_web)}] <- instalados.")
        finally:
            w.CloseServiceHandle(service_manager)

    def restart_services(self):
        cria_logtxt("Iniciando rotina diária para reiniciar as API's web")
        service_manager = w.OpenSCManager(None, None, w.SC_MANAGER_ALL_ACCESS)
        try:
            for service in self.services_api_web:
                restart_single_service(service, service_manager, self.username_service, self.password_service)
            cria_logtxt("Rotina de reiniciar as API's diariamente completa")
        finally:
            w.CloseServiceHandle(service_manager)

    def check_nginx_and_start(self, sv_manager):
        if self.service_nginx:
            try:
                s_nginx = w.OpenService(sv_manager, self.service_nginx, self.desired_access)
                status_nginx = w.QueryServiceStatus(self.service_nginx)

                if status_nginx[1] == w.SERVICE_STOPPED:
                    cria_logtxt("Nginx estava parado, iniciando...")
                    wsu.StartService(self.service_nginx)
            finally:
                w.CloseServiceHandle(s_nginx)