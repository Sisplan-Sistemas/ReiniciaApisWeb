from datetime import datetime
from time import sleep
from requests import get
from traceback import format_exc
import win32service as w
import win32serviceutil as wsu
import schedule as a

class RestartApiService:
    def __init__(self):
        self.cria_logtxt("Iniciando serviço de reiniciar as api's web...")
        self.username_service = "bruno.sena@sisplan.local"
        self.password_service = "miguel08912!"
        self.services_api_web = []
        self.service_nginx = ''
        self.restarting_services_api = False
        self.make_requests_running = False
        self.is_updating = False
        self.desired_access = w.SERVICE_CHANGE_CONFIG | w.SERVICE_START | w.SERVICE_STOP | w.SERVICE_QUERY_STATUS
        try:
            service_manager = w.OpenSCManager(None, None, w.SC_MANAGER_ALL_ACCESS)
            for service in w.EnumServicesStatus(service_manager, w.SERVICE_WIN32):
                if 'Sisplan_Api_Web' in service[0]:
                    self.services_api_web.append(service[0])
                if 'NGINX' in service[0].upper():
                    self.service_nginx = service[0]
            self.cria_logtxt(f"Encontrado os serviços -> [{', '.join(self.services_api_web)}] <- instalados.")
        finally:
            w.CloseServiceHandle(service_manager)

    def cria_logtxt(self, message):
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        formatted_time_nametxt = current_time.strftime('%Y-%m-%d')
        with open(f'log_restart_api_web{formatted_time_nametxt}.txt', 'a') as f:
            f.write(f'[{formatted_time}]: {message}\n')

    def check_nginx_and_start(self, sv_manager):
        if self.service_nginx != '':
            try:
                s_nginx = w.OpenService(sv_manager, self.service_nginx, self.desired_access)
                status_nginx = w.QueryServiceStatus(self.service_nginx)
                if status_nginx[1] == w.SERVICE_STOPPED:
                    self.cria_logtxt("Nginx estava sem parado, iniciando...")
                    wsu.StartService(self.service_nginx)
            finally:
                w.CloseServiceHandle(s_nginx)

    def restart_services(self):
        if self.make_requests_running:
            sleep(20)
            self.cria_logtxt("Verificado que a tarefa de checar conexão das api's está rodando, aguardar 30 segundos...")
        try:
            if not self.is_updating:
                if (len(self.services_api_web) > 0):
                    try:
                        self.restarting_services_api = True
                        self.cria_logtxt("Iniciado rotina diária para reiniciar as api's web. Reiniciando...")
                        service_manager = w.OpenSCManager(None, None, w.SC_MANAGER_ALL_ACCESS)
                        for s in self.services_api_web:
                            try:
                                s_open = w.OpenService(service_manager, s, self.desired_access)
                                status_s = wsu.QueryServiceStatus(s)
                                if status_s[1] == w.SERVICE_RUNNING:
                                    wsu.StopService(s) 
                                    sleep(10)
                                    self.cria_logtxt(f'Serviço {s} parado com sucesso.')   
                                w.ChangeServiceConfig(
                                    s_open,
                                    w.SERVICE_NO_CHANGE,
                                    w.SERVICE_NO_CHANGE,
                                    w.SERVICE_NO_CHANGE,
                                    None,
                                    None,
                                    False,
                                    None,
                                    self.username_service,
                                    self.password_service,
                                    None,
                                )
                                status_s_after_changing = wsu.QueryServiceStatus(s)
                                if status_s_after_changing[1] != w.SERVICE_RUNNING:
                                    if status_s_after_changing[1] != w.SERVICE_START_PENDING:
                                        self.cria_logtxt(f'Serviço {s} sendo iniciado novamente...')
                                        wsu.StartService(s)
                                        sleep(5)
                                    else:
                                        self.cria_logtxt(f'Serviço {s} sendo iniciado novamente...')
                                        sleep(5)
                            finally:
                                status_s_after_start = wsu.QueryServiceStatus(s)
                                if status_s_after_start[1] != w.SERVICE_RUNNING:
                                    if status_s_after_start[1] != w.SERVICE_START_PENDING:
                                        self.cria_logtxt('Não foi possível iniciar serviço novamente, tentando novamente 3 vezes...')
                                        for attempt in range(1, 4):
                                            self.cria_logtxt(f'Tentativa {attempt}...')
                                            status_s_attemps = wsu.QueryServiceStatus(s)
                                            if status_s_attemps[1] != w.SERVICE_RUNNING:
                                                if status_s_attemps[1] != w.SERVICE_START_PENDING:
                                                    wsu.StartService(s)
                                                    sleep(5)
                                                else:
                                                    sleep(5)
                                                    break
                                            else:
                                                break
                                    else:
                                        self.cria_logtxt(f'Serviço {s} sendo iniciado novamente...')
                                else:
                                    self.cria_logtxt(f'Serviço {s} iniciado com sucesso...')
                                
                                status_s_after_attempts = wsu.QueryServiceStatus(s)
                                if status_s_after_attempts[1] != w.SERVICE_RUNNING:
                                    if status_s_after_attempts[1] != w.SERVICE_START_PENDING:
                                        self.cria_logtxt(f'Não foi possível iniciar o serviço {s}! Por favor, verifique.')
                                    else:
                                        sleep(5)
                                w.CloseServiceHandle(s_open)
                    finally:
                        w.CloseServiceHandle(service_manager)
                        self.cria_logtxt("Rotina de reiniciar as api's diariamente completa.")
                        self.restarting_services_api = False
        except Exception as e:
            error_message = format_exc()
            self.cria_logtxt(f"Ocorreu erro na rotina de reiniciar os serviços diária. Erro: {e}")
            self.cria_logtxt(f"Mais detalhes do erro: {error_message}")

    def change_and_start_unresponsive_services(self, list_unresponsive_apis):
        if (len(list_unresponsive_apis) > 0):
            if not self.restarting_services_api:
                try:
                    self.cria_logtxt(f"Api's que não responderam a requisição de teste de conexão -> [{', '.join(list_unresponsive_apis)}] <- Iniciando rotina de reiniciar os serviços...")
                    sc_manager = w.OpenSCManager(None, None, w.SC_MANAGER_ALL_ACCESS)
                    self.check_nginx_and_start(sc_manager)
                    for unresponsive_api in list_unresponsive_apis:
                        try:        
                            service_api = w.OpenService(sc_manager, unresponsive_api, self.desired_access)
                            status_service = wsu.QueryServiceStatus(unresponsive_api)
                            if status_service[1] != w.SERVICE_STOPPED:
                                wsu.StopService(unresponsive_api)
                                sleep(10)
                                self.cria_logtxt(f'Serviço {unresponsive_api} sendo parado devido a falta de comunicação. Reiniciando...')
                            w.ChangeServiceConfig(
                                service_api,
                                w.SERVICE_NO_CHANGE,
                                w.SERVICE_NO_CHANGE,
                                w.SERVICE_NO_CHANGE,
                                None,
                                None,
                                False,
                                None,
                                self.username_service,
                                self.password_service,
                                None,
                            )
                            status_service_api_after_changing = wsu.QueryServiceStatus(unresponsive_api)
                            if status_service_api_after_changing[1] != w.SERVICE_RUNNING:
                                if status_service_api_after_changing[1] != w.SERVICE_START_PENDING:
                                    self.cria_logtxt(f'Serviço {unresponsive_api} sendo iniciado novamente...')
                                    wsu.StartService(unresponsive_api)
                                    sleep(5)
                                else:
                                    self.cria_logtxt(f'Serviço {unresponsive_api} sendo iniciado novamente...')
                                    sleep(5)
                        finally:
                            status_after_attempt_to_start = wsu.QueryServiceStatus(unresponsive_api)
                            if status_after_attempt_to_start[1] != w.SERVICE_RUNNING:
                                if status_after_attempt_to_start[1] != w.SERVICE_START_PENDING:
                                    self.cria_logtxt(f'Não foi possível iniciar o serviço {unresponsive_api}. Tentando novamente 3 vezes...')
                                    for attempt in range(1, 4):
                                        self.cria_logtxt(f'Tentativa {attempt}')
                                        status_service_attempt = wsu.QueryServiceStatus(unresponsive_api)
                                        if status_service_attempt[1] != w.SERVICE_RUNNING:
                                            if status_service_attempt[1] != w.SERVICE_START_PENDING:
                                                wsu.StartService(unresponsive_api)
                                                sleep(5)
                                            else:
                                                sleep(5)
                                                break
                                        else:
                                            break
                                else:
                                    self.cria_logtxt(f'Serviço {unresponsive_api} sendo iniciado novamente...')
                                    sleep(5)
                            else:
                                self.cria_logtxt(f'Serviço {unresponsive_api} iniciado com sucesso...')

                            status_service_final = wsu.QueryServiceStatus(unresponsive_api)
                            if status_service_final[1] != w.SERVICE_RUNNING:
                                if status_service_final[1] != w.SERVICE_START_PENDING:
                                    self.cria_logtxt(f'Não foi possível iniciar o serviço {unresponsive_api}. Por favor, verifique.')
                                else:
                                    sleep(5)
                            w.CloseServiceHandle(service_api)
                finally:
                    self.cria_logtxt("Finalizado rotina para reiniciar api's que não responderam a requisição.")
                    w.CloseServiceHandle(sc_manager)
    
    def make_requests(self):
        list_unresponsive_apis = []
        self.make_requests_running = True
        try:
            if not self.is_updating:
                for serv in self.services_api_web:
                    port = serv.replace('Sisplan_Api_Web_', '')
                    try:
                        response = get(url=f"http://127.0.0.1:{port}/healthcheck")
                        if response.status_code != 200:
                            list_unresponsive_apis.append(serv)
                    except:
                        list_unresponsive_apis.append(serv)
                self.change_and_start_unresponsive_services(list_unresponsive_apis)
        except Exception as e:
            self.cria_logtxt(f"Não foi possível executar a rotina das requisições para testar a conexão das api's! Erro: {e}")
            exec_error = format_exc()
            self.cria_logtxt(f"Mais detalhes do erro: {exec_error}")
        self.make_requests_running = False

    def main(self):
        a.every(2).minutes.do(self.make_requests)
        self.cria_logtxt('Agendamento da primeira tarefa feita de 2 em 2 minutos com sucesso.')
        a.every().day.at("22:00").do(self.restart_services)
        self.cria_logtxt('Agendamento da segunda tarefa feita para as 22:00 horas com sucesso.')
        while True:
            with open('atualizacao_web.txt', 'r') as txt:
                conteudo = txt.readlines()
                if 'true' in conteudo:
                    self.is_updating = True
                else:
                    self.is_updating = False
            a.run_pending()

if __name__ == '__main__':
    restart_services = RestartApiService()
    restart_services.main()