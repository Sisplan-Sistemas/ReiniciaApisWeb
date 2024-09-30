import win32service as w
import win32serviceutil as wsu
from time import sleep
from utils.logger import cria_log_txt
from os import path, getenv
from sys import executable
from utils.messenger import send_message_to_sispemail, send_message_to_telegram
from asyncio import run
from utils.error_handler import log_error
from subprocess import run as run_sb

def restart_single_service(service_name, username_service, password_service):
    try:
        emp_name = getenv("EMP_NAME")
        status_service = wsu.QueryServiceStatus(service_name)
        nssm_path = path.join(path.abspath(path.join(path.dirname(__file__), '..')), 'nssm.exe')
        apiweb_path = path.join(path.abspath(path.join(path.dirname(__file__), '..')), 'apiWeb.exe')
        apiweb_args = '/service'
        if status_service[1] == w.SERVICE_RUNNING:
            wsu.StopService(service_name)
            sleep(10)
            cria_log_txt(f'Serviço {service_name} parado com sucesso.')
        uninstall_command = [nssm_path, 'remove', service_name, 'confirm']
        run_sb(uninstall_command, check=True)
        sleep(3)
        install_command = [nssm_path, 'install', service_name, apiweb_path, apiweb_args]
        run_sb(install_command, check=True)
        sleep(3)
        for attempt in range(1, 4):
            status_new_service = wsu.QueryServiceStatus(service_name)
            if status_new_service[1] == w.SERVICE_RUNNING:
                cria_log_txt(f"Serviço {service_name} iniciado com sucesso.")
                return
            elif status_new_service[1] != w.SERVICE_START_PENDING:
                cria_log_txt(f"Tentativa {attempt} de iniciar o serviço {service_name}")
                wsu.StartService(service_name)
                sleep(10)
        cria_log_txt(f"Não foi possível iniciar o serviço {service_name} após 3 tentativas.")
        send_message_to_sispemail([service_name], f"⚠ Atenção ⚠ \\n$OLA$!\\nNão foi possível iniciar o serviço {service_name} após 3 tentativas no cliente *{emp_name.upper()}*. \\nPor favor, verifique!")
        run(send_message_to_telegram(f"⚠ Atenção ⚠ \\nNão foi possível iniciar o serviço {service_name} após 3 tentativas no cliente *{emp_name.upper()}*\\nPor favor, verifique"))
    except Exception as e:
        send_message_to_sispemail([service_name], f"⚠ Atenção ⚠ \\n$OLA$!\\nNão foi possível finalizar o processo de desinstalar e reinstalar o serviço {service_name} no cliente *{emp_name.upper()}*. \\nPor favor, verifique!")
        run(send_message_to_telegram(f"⚠ Atenção ⚠ \\nNão foi possível finalizar o processo de desinstalar e reinstalar o serviço {service_name} no cliente *{emp_name.upper()}*\\nPor favor, verifique"))
        log_error(e, f"Não foi possível finalizar o processo de desinstalar e reinstalar o serviço {service_name}. Por favor, verifique!")
        
        