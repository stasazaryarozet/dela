#!/usr/bin/env python3
"""
Тест интеграции WhatsApp для проверки работоспособности
"""
import sys
import os
from pathlib import Path

# Добавляем путь к gates
gates_dir = Path(__file__).parent.parent
sys.path.insert(0, str(gates_dir))

def test_import():
    """Тест импорта модуля"""
    try:
        from whatsapp.whatsapp_multi_user_gate import WhatsAppMultiUserGate
        print("✅ Импорт WhatsAppMultiUserGate успешен")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_structure():
    """Тест структуры директорий"""
    whatsapp_dir = Path(__file__).parent
    required_dirs = ['credentials', 'sessions', 'scripts']
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = whatsapp_dir / dir_name
        if dir_path.exists():
            print(f"✅ Директория {dir_name}/ существует")
        else:
            print(f"❌ Директория {dir_name}/ не найдена")
            all_exist = False
    
    return all_exist

def test_credentials_structure():
    """Тест структуры credentials (без реальных данных)"""
    whatsapp_dir = Path(__file__).parent
    credentials_dir = whatsapp_dir / 'credentials'
    
    if not credentials_dir.exists():
        print("⚠️  Директория credentials/ не существует")
        return False
    
    # Проверяем .gitignore
    gitignore_path = credentials_dir / '.gitignore'
    if gitignore_path.exists():
        print("✅ .gitignore в credentials/ существует")
    else:
        print("⚠️  .gitignore в credentials/ отсутствует")
    
    # Проверяем, что нет реальных credentials (безопасность)
    azarya_creds = credentials_dir / 'azarya_credentials.json'
    olga_creds = credentials_dir / 'olga_credentials.json'
    
    if azarya_creds.exists():
        print("⚠️  azarya_credentials.json найден (должен быть настроен)")
    else:
        print("ℹ️  azarya_credentials.json отсутствует (требуется настройка)")
    
    if olga_creds.exists():
        print("⚠️  olga_credentials.json найден (должен быть настроен)")
    else:
        print("ℹ️  olga_credentials.json отсутствует (требуется настройка)")
    
    return True

def test_gate_initialization():
    """Тест инициализации Gate (без реальных credentials)"""
    try:
        from whatsapp.whatsapp_multi_user_gate import WhatsAppMultiUserGate
        
        # Пытаемся инициализировать для azarya (ожидаем FileNotFoundError)
        try:
            gate = WhatsAppMultiUserGate(user='azarya')
            print("⚠️  Gate инициализирован (credentials найдены)")
            return True
        except FileNotFoundError as e:
            print(f"✅ Gate правильно требует credentials: {str(e)[:80]}...")
            return True
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return False
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Запуск всех тестов"""
    print("=" * 80)
    print("ТЕСТ ИНТЕГРАЦИИ WHATSAPP")
    print("=" * 80)
    print()
    
    results = []
    
    print("1. Тест структуры директорий...")
    results.append(("Структура", test_structure()))
    print()
    
    print("2. Тест структуры credentials...")
    results.append(("Credentials", test_credentials_structure()))
    print()
    
    print("3. Тест импорта модуля...")
    results.append(("Импорт", test_import()))
    print()
    
    print("4. Тест инициализации Gate...")
    results.append(("Инициализация", test_gate_initialization()))
    print()
    
    print("=" * 80)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 80)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    all_passed = all(result for _, result in results)
    
    print()
    if all_passed:
        print("✅ Все тесты пройдены успешно!")
        print()
        print("Следующие шаги:")
        print("1. Запустите .gates/whatsapp/scripts/setup_azarya_whatsapp.py")
        print("2. Запустите .gates/whatsapp/scripts/setup_olga_whatsapp.py")
    else:
        print("❌ Некоторые тесты не пройдены")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)


