#!/usr/bin/env python3
"""
Чтение сообщений WhatsApp для Ольги
Поиск сообщения от Сноба
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Добавляем путь к gates
gates_dir = Path(__file__).parent.parent
sys.path.insert(0, str(gates_dir))

def find_snob_message():
    """Поиск сообщения от Сноба в WhatsApp Ольги"""
    print("=" * 80)
    print("ПОИСК СООБЩЕНИЯ ОТ СНОБ В WHATSAPP ОЛЬГИ")
    print("=" * 80)
    print()
    
    try:
        # Пробуем использовать multi-user gate
        from whatsapp.whatsapp_multi_user_gate import WhatsAppMultiUserGate
        
        print("🔐 Подключение к WhatsApp Ольги...")
        gate = WhatsAppMultiUserGate(user='olga')
        
        print("📨 Получение сообщений...")
        messages_data = gate.get_messages(limit=100)
        
        if 'error' in messages_data:
            print(f"❌ Ошибка: {messages_data['error']}")
            return None
        
        messages = messages_data.get('messages', [])
        print(f"✅ Получено сообщений: {len(messages)}")
        print()
        
        # Ищем сообщения от Сноба
        snob_keywords = ['сноб', 'snob', 'редакция', 'редактор', 'публикация', 'статья']
        snob_messages = []
        
        for msg in messages:
            # Проверяем текст сообщения
            text = ''
            if 'text' in msg:
                text = msg['text'].get('body', '').lower()
            elif 'body' in msg:
                text = str(msg.get('body', '')).lower()
            
            # Проверяем отправителя (может быть номер телефона или имя)
            from_number = msg.get('from', '')
            
            # Ищем ключевые слова
            for keyword in snob_keywords:
                if keyword in text:
                    snob_messages.append({
                        'id': msg.get('id'),
                        'from': from_number,
                        'text': text,
                        'timestamp': msg.get('timestamp'),
                        'full_message': msg
                    })
                    break
        
        if snob_messages:
            print(f"✅ Найдено сообщений от Сноба: {len(snob_messages)}")
            print()
            for i, msg in enumerate(snob_messages, 1):
                print(f"--- Сообщение {i} ---")
                print(f"От: {msg['from']}")
                print(f"Текст: {msg['text'][:200]}...")
                print(f"ID: {msg['id']}")
                print()
            
            return snob_messages
        else:
            print("ℹ️  Сообщений от Сноба не найдено в последних сообщениях")
            print("   Попробуйте увеличить лимит или проверить webhook")
            return []
            
    except FileNotFoundError as e:
        print(f"⚠️  Credentials для Ольги не найдены")
        print(f"   Запустите: .gates/whatsapp/scripts/setup_olga_whatsapp.py")
        print()
        print("Попробую использовать базовый WhatsApp Gate...")
        
        # Пробуем базовый gate и другие возможные расположения
        try:
            from whatsapp_gate import WhatsAppGate
            
            possible_paths = [
                gates_dir / 'whatsapp' / 'credentials.json',
                gates_dir / 'whatsapp_credentials.json',
                gates_dir.parent / 'whatsapp_credentials.json',
            ]
            
            for cred_path in possible_paths:
                if cred_path.exists():
                    try:
                        gate = WhatsAppGate(credentials_path=str(cred_path))
                        messages_data = gate.get_messages(limit=100)
                        messages = messages_data if isinstance(messages_data, list) else messages_data.get('data', [])
                        
                        print(f"✅ Получено сообщений через базовый Gate: {len(messages)}")
                        
                        # Ищем Сноб
                        for msg in messages:
                            text = str(msg).lower()
                            if any(kw in text for kw in snob_keywords):
                                print(f"✅ Найдено сообщение от Сноба!")
                                print(f"   Сообщение: {msg}")
                                return [msg]
                        break
                    except Exception as e_path:
                        continue
            
            print("ℹ️  Credentials не найдены в стандартных расположениях")
            print("   Попробую автоматическую настройку...")
            
            # Пробуем автоматическую настройку
            try:
                from auto_setup_olga import auto_setup
                if auto_setup():
                    # Повторяем попытку после настройки
                    gate = WhatsAppMultiUserGate(user='olga')
                    messages_data = gate.get_messages(limit=100)
                    messages = messages_data.get('messages', [])
                    
                    for msg in messages:
                        text = str(msg).lower() if isinstance(msg, dict) else str(msg).lower()
                        if any(kw in text for kw in snob_keywords):
                            print(f"✅ Найдено сообщение от Сноба после настройки!")
                            return [msg]
            except:
                pass
            
            return None
        except Exception as e2:
            print(f"ℹ️  Базовый Gate недоступен: {e2}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    result = find_snob_message()
    
    if result:
        print("=" * 80)
        print("✅ ПОИСК ЗАВЕРШЕН")
        print("=" * 80)
    else:
        print("=" * 80)
        print("⚠️  СООБЩЕНИЕ НЕ НАЙДЕНО")
        print("=" * 80)

