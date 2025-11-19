#!/usr/bin/env python3
"""
Отправка ответа редакции "Сноб" через Gmail API
"""
import os
import sys
import base64
from email.mime.text import MIMEText

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'google'))
from google_gate import GoogleGate

def send_response_email():
    """Отправить ответ редакции 'Сноб'"""
    print("=" * 80)
    print("ОТПРАВКА ОТВЕТА РЕДАКЦИИ 'СНОБ'")
    print("=" * 80)
    print()
    
    gate = GoogleGate(
        credentials_path=os.path.join(os.path.dirname(__file__), 'google', 'credentials.json'),
        token_path=os.path.join(os.path.dirname(__file__), 'google', 'token.pickle')
    )
    
    gmail = gate.gmail()
    
    # Текст письма
    message_text = """Добрый день!

Внесла правки в документ. Текст стал более объективным и фактичным. Готов к публикации.

С уважением,
Ольга Розет"""
    
    # Создаем сообщение
    message = MIMEText(message_text, 'plain', 'utf-8')
    message['To'] = 'editor@snob.ru'  # Нужно найти реальный email из исходного сообщения
    message['Subject'] = 'Re: Доработанный текст на согласование — Эстетика исчезающего'
    message['From'] = 'o.g.rozet@gmail.com'
    
    # Кодируем сообщение
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    try:
        # Отправляем
        send_message = gmail.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        print("✅ Ответ отправлен!")
        print(f"✅ Message ID: {send_message['id']}")
        print()
        print(f"📧 Кому: editor@snob.ru")
        print(f"📝 Тема: Re: Доработанный текст на согласование — Эстетика исчезающего")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # Сначала нужно найти email редактора из исходного сообщения
    # Пока используем общий адрес
    print("⚠️  Нужно найти email редактора из исходного сообщения")
    print("⚠️  Используется общий адрес: editor@snob.ru")
    print()
    
    success = send_response_email()
    sys.exit(0 if success else 1)


