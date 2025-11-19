#!/usr/bin/env python3
"""
Простое чтение Google Docs через буфер обмена
После запуска скрипта откройте документ в браузере и нажмите Cmd+A, Cmd+C
"""
import subprocess
import pyperclip
import time
import json
import os

def read_from_clipboard():
    """Читать текст из буфера обмена"""
    print("=" * 80)
    print("ЧТЕНИЕ ДОКУМЕНТА ИЗ БУФЕРА ОБМЕНА")
    print("=" * 80)
    print()
    print("📋 Инструкция:")
    print("   1. Откройте документ в браузере:")
    print("      https://docs.google.com/document/d/1AfAFbklq2RCtOCtaKX_SPQTGNir2pMR9pq3V8Ggmhx4/edit")
    print("   2. Нажмите Cmd+A (выделить всё)")
    print("   3. Нажмите Cmd+C (копировать)")
    print("   4. Нажмите Enter здесь")
    print()
    input("Нажмите Enter после копирования текста...")
    
    try:
        # Читаем из буфера обмена
        text = pyperclip.paste()
        
        if text and len(text.strip()) > 10:
            print()
            print("✅ Текст получен!")
            print(f"📏 Длина: {len(text)} символов")
            print()
            print("=" * 80)
            print("СОДЕРЖИМОЕ ДОКУМЕНТА")
            print("=" * 80)
            print()
            print(text)
            print()
            print("=" * 80)
            
            # Сохраняем результат
            result = {
                'doc_id': '1AfAFbklq2RCtOCtaKX_SPQTGNir2pMR9pq3V8Ggmhx4',
                'source': 'clipboard',
                'text': text,
                'length': len(text)
            }
            
            output_file = os.path.join(os.path.dirname(__file__), 'google_doc_content.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Результат сохранён: {output_file}")
            return result
        else:
            print("❌ Буфер обмена пуст или содержит слишком мало текста")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n💡 Попробуйте установить pyperclip:")
        print("   pip3 install pyperclip")
        return None

if __name__ == '__main__':
    try:
        read_from_clipboard()
    except ImportError:
        print("❌ Требуется библиотека pyperclip")
        print("   Установите: pip3 install pyperclip")
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")


