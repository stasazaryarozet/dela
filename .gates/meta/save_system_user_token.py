#!/usr/bin/env python3
"""
Сохранение System User Token для WhatsApp API
"""
import os
from pathlib import Path
from getpass import getpass

meta_dir = Path(__file__).parent
env_path = meta_dir / '.env'

def save_system_user_token():
    """Сохранить System User Token в .env файл"""
    print("=" * 80)
    print("СОХРАНЕНИЕ SYSTEM USER TOKEN")
    print("=" * 80)
    print()
    print("📝 Инструкция по получению токена для глубокой интеграции:")
    print()
    print("   1. Откройте: https://business.facebook.com/settings/system-users")
    print("   2. Создайте System User: 'Meta Deep Integration' (Role: Admin)")
    print("   3. Назначьте права на ВСЕ активы:")
    print("      - Facebook Pages (Full Control)")
    print("      - Instagram Accounts (Full Control)")
    print("      - WhatsApp Accounts (Full Control)")
    print("      - Business Assets (Full Control)")
    print("   4. Сгенерируйте токен с максимальными правами:")
    print("      WhatsApp: whatsapp_business_management, messaging, analytics")
    print("      Pages: pages_show_list, manage_posts, read_engagement")
    print("      Instagram: instagram_basic, manage_comments, content_publish")
    print("      Business: business_management, ads_management")
    print("   5. Скопируйте токен")
    print()
    print("📚 Полная инструкция: .gates/meta/create_system_user_token.md")
    print()
    
    token = getpass("Введите System User Token (скрыт): ").strip()
    
    if not token:
        print("❌ Токен не введен")
        return False
    
    # Читаем существующий .env или создаем новый
    env_vars = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    # Обновляем токен
    env_vars['META_SYSTEM_USER_TOKEN'] = token
    
    # Сохраняем .env
    with open(env_path, 'w') as f:
        f.write("# Meta System User Token для WhatsApp API\n")
        f.write("# Создан автоматически через save_system_user_token.py\n")
        f.write("# Не коммитьте этот файл в git!\n")
        f.write("\n")
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print()
    print(f"✅ System User Token сохранен в: {env_path}")
    print()
    print("Теперь можно использовать для доступа к WhatsApp API:")
    print("   python3 .gates/whatsapp/setup_whatsapp_cloud_api.py")
    print()
    
    return True

if __name__ == '__main__':
    save_system_user_token()

