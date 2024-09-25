from datetime import datetime

def cria_logtxt(message):
    current_time = datetime.now()
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    formatted_time_nametxt = current_time.strftime('%Y-%m-%d')
    with open(f'log_restart_api_web{formatted_time_nametxt}.txt', 'a') as f:
        f.write(f'[{formatted_time}]: {message}\n')