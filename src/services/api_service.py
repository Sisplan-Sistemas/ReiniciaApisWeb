import win32service as w
import win32serviceutil as wsu
from time import sleep
from utils.logger import cria_logtxt

def restart_single_service(service_name, service_manager, username_service, password_service):
    try:
        s_open = w.OpenService(service_manager, service_name, w.SERVICE_CHANGE_CONFIG | w.SERVICE_START | w.SERVICE_STOP | w.SERVICE_QUERY_STATUS)
        status_s = wsu.QueryServiceStatus(service_name)
        if status_s[1] == w.SERVICE_RUNNING:
            wsu.StopService(service_name)
            sleep(10)
            cria_logtxt(f'Serviço {service_name} parado com sucesso.')

        wsu.ChangeServiceConfig(
            service_name,
            w.SERVICE_NO_CHANGE,
            w.SERVICE_NO_CHANGE,
            w.SERVICE_NO_CHANGE,
            None,
            None,
            False,
            None,
            username_service,
            password_service,
            None,
        )
    
        for attempt in range(1, 4):
            status_s = wsu.QueryServiceStatus(service_name)
            if status_s[1] == w.SERVICE_RUNNING:
                cria_logtxt(f'Serviço {service_name} iniciado com sucesso.')
                return
            elif status_s[1] != w.SERVICE_START_PENDING:
                cria_logtxt(f'Tentativa {attempt} de iniciar {service_name}')
                wsu.StartService(service_name)
                sleep(5)
        
        cria_logtxt(f'Não foi possível iniciar o serviço {service_name} após 3 tentativas.')

    finally:
        w.CloseServiceHandle(s_open)