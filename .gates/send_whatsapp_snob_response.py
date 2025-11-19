#!/usr/bin/env python3
"""
Отправка ответа редакции "Сноб" через WhatsApp
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from whatsapp_gate import WhatsAppGate

def send_whatsapp_response():
    """Отправить ответ редакции 'Сноб' через WhatsApp"""
    print("=" * 80)
    print("ОТПРАВКА ОТВЕТА РЕДАКЦИИ 'СНОБ' ЧЕРЕЗ WHATSAPP")
    print("=" * 80)
    print()
    
    try:
        gate = WhatsAppGate()
        
        # Номер редактора "Сноб" - нужно найти из сообщения
        # Пока используем общий формат
        to_number = None  # Нужно получить из входящего сообщения
        
        message = """Добрый день! Внесла правки в документ. Текст стал более объективным и фактичным. Готов к публикации."""
        
        if to_number:
            result = gate.send_message(to_number, message)
            print("✅ Ответ отправлен через WhatsApp!")
            print(f"✅ Message ID: {result['message_id']}")
            print(f"✅ Status: {result['status']}")
            return True
        else:
            print("⚠️  Нужен номер телефона получателя")
            print("⚠️  Подготовлен текст ответа в .gates/whatsapp_snob_response.txt")
            return False
            
    except FileNotFoundError:
        print("⚠️  WhatsApp Gate не настроен")
        print("⚠️  Подготовлен текст ответа в .gates/whatsapp_snob_response.txt")
        print()
        print("Текст ответа:")
        print("Добрый день! Внесла правки в документ. Текст стал более объективным и фактичным. Готов к публикации.")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == '__main__':
    send_whatsapp_response()


