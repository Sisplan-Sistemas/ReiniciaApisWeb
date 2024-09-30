from datetime import datetime
from os import getenv
from .jwt import request_auth_jwt, ip_sisplan
from requests import post
from base64 import b64encode
from json import dumps
from .helpers import encrypt, saudacao
from telegram import Bot
from .logger import cria_log_txt
from asyncio import run
from .error_handler import log_error

enviou_saudacao = False

def send_message_to_sispemail(list_unresponsive_services, message = ''):
    try:
        emp_name = getenv("EMP_NAME")
        bearer_token = request_auth_jwt()
        ip = ip_sisplan()
        header_post = { "Authorization": f"Bearer {bearer_token}" }
        if message == '':
            message = f"⚠ Atenção ⚠ \\n$OLA$!\\nOs serviços não foram iniciados com sucesso no cliente: *{emp_name.upper()}*. \\nServiços: {', '.join(list_unresponsive_services)}"
        username_api = "API"
        password_api = b64encode(encrypt('u^buhOCRgfta', 45857).encode('utf-8')).decode('utf-8')
        object_to_sispemail = {
            "TELEFONE": '120363321405542470@g.us',
            "ORIGEM": "E",
            "USUARIO": "VERIFICAAPIWEB",
            "TELA": "APIWEB",
            "CAMPOCHAVE": "APIWEB",
            "DT_CADASTRO": (datetime.now()).strftime('%Y-%m-%d %H:%M:%S'),
            "MENSAGEM": b64encode(message.encode()).decode()
        }
        json_string = dumps(object_to_sispemail)
        response = post(url=f"{ip}/WhatsAppSisp?USUARIO={username_api}&SENHA={password_api}", data=json_string, headers=header_post)
        if response.status_code != 200:
            run(send_message_to_telegram('Não foi possível enviar a seguinte mensagem pelo whatsapp'))
            run(send_message_to_telegram(message))
    except Exception as e:
        run(send_message_to_telegram('Não foi possível enviar a seguinte mensagem pelo whatsapp'))
        run(send_message_to_telegram(message))
        log_error(e, "Erro ao enviar whatsapp.")

async def send_message_to_telegram(message = ''):
    global enviou_saudacao
    try:
        id = '6528929191'
        token_bot = '8146413549:AAEgAjT-4109-P-k0p1XgjouG4dLO5nlaiQ'
        ares_bot = Bot(token=token_bot)
        saudacao_msg = saudacao()
        if enviou_saudacao == False and saudacao_msg == 'Bom dia':
            await ares_bot.send_message(chat_id=id, text=saudacao_msg)
        if saudacao_msg == 'Bom dia':
            enviou_saudacao = True
        elif saudacao_msg == 'Boa tarde':
            enviou_saudacao = False
        await ares_bot.send_message(chat_id=id, text=message, parse_mode="MarkdownV2")
    except Exception as e:
        cria_log_txt(f'Não foi possível enviar telegram com a mensagem: {message}')
        log_error(e, "Erro ao enviar telegram.")