from datetime import datetime

def encrypt(s: str, key: int):
    C1 = 76541
    C2 = 84529
    result = ''
    key = key % 65536
    for char in s:
        byte_val = ord(char)
        xor_result = byte_val ^ (key >> 8)
        xor_result_byte = xor_result & 0xFF
        encrypted_char = format(xor_result_byte, '02x')
        result += encrypted_char
        key = (xor_result_byte + key) * C1 + C2
        key = key % 65536
    return result

def saudacao():
    hora_atual = datetime.now().hour
    if 5 <= hora_atual < 12:
        return "Bom dia"
    elif 12 <= hora_atual < 18:
        return "Boa tarde"
    return "Boa noite"