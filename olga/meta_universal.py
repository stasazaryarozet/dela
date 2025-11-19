#!/usr/bin/env python3
"""
ЕДИНЫЙ ИСТОЧНИК МЕТА-ПРИНЦИПА ПОМОЩИ
Архитектурно надежная система для всех проектов Ольги

Использование:
    from meta_universal import get_help_text, get_help_html, get_help_telegram

Проекты:
    - olgarozet.ru
    - olgarozet.ru/chl/
    - parisinjanuary.ru
    - @olgarozet (Telegram)
    - любые будущие проекты
"""

# ============================================================================
# ЕДИНСТВЕННЫЙ ИСТОЧНИК ИСТИНЫ
# ============================================================================

HELP_TITLE = "Нужна помощь?"
HELP_QUESTION = "Не можете себе позволить? Возможно, что-нибудь придумаем."
HELP_EMAIL = "o.g.rozet@gmail.com"
HELP_SUBJECT = "Субсидия"
HELP_TELEGRAM = "@ORozet"

# ============================================================================
# ГЕНЕРАТОРЫ ДЛЯ РАЗНЫХ КАНАЛОВ
# ============================================================================

def get_help_text(project_name=None):
    """
    Возвращает текст для Telegram или простого текста
    
    Args:
        project_name: название проекта для темы письма (опционально)
    
    Returns:
        str: текст с контактами
    """
    subject = f"{HELP_SUBJECT} {project_name}" if project_name else HELP_SUBJECT
    return f"{HELP_QUESTION}\nПожалуйста, пишите: {HELP_EMAIL} с темой \"{subject}\" или {HELP_TELEGRAM}"


def get_help_html(project_name=None, style="default"):
    """
    Возвращает HTML-разметку
    
    Args:
        project_name: название проекта для темы письма (опционально)
        style: стиль оформления ("default", "minimal", "paris")
    
    Returns:
        str: HTML-разметка
    """
    subject = f"{HELP_SUBJECT}%20{project_name.replace(' ', '%20')}" if project_name else HELP_SUBJECT
    
    if style == "minimal":
        return f'''<p style="text-align:center;font-size:0.9rem;color:#666;margin:1.5rem auto 2rem;max-width:32rem;line-height:1.6">
  {HELP_QUESTION}<br>
  Пожалуйста, пишите: <a href="mailto:{HELP_EMAIL}?subject={subject}" style="color:#666;text-decoration:underline">{HELP_EMAIL}</a> с темой "{HELP_SUBJECT}" или <a href="https://t.me/{HELP_TELEGRAM[1:]}" style="color:#666;text-decoration:underline">{HELP_TELEGRAM}</a>
</p>'''
    
    elif style == "paris":
        # Для Paris in January — Art Deco стиль
        return f'''<div class="help-section" style="text-align:center;margin:2rem auto;padding:2rem;background:rgba(255,248,240,0.5);border:1px solid #e8d5c4;max-width:36rem;">
  <p style="font-size:1rem;color:#4a4a4a;line-height:1.7;margin-bottom:1rem;">
    {HELP_QUESTION}
  </p>
  <p style="font-size:0.9rem;color:#666;">
    Пожалуйста, пишите: <a href="mailto:{HELP_EMAIL}?subject={subject}" style="color:#8b6f47;text-decoration:none;border-bottom:1px solid #8b6f47">{HELP_EMAIL}</a> с темой "{HELP_SUBJECT}"<br>
    или Telegram: <a href="https://t.me/{HELP_TELEGRAM[1:]}" style="color:#8b6f47;text-decoration:none;border-bottom:1px solid #8b6f47">{HELP_TELEGRAM}</a>
  </p>
</div>'''
    
    else:  # default
        return f'''<h2 style="font-size:1.3em;font-weight:400;margin-bottom:0.5em">{get_meta_title()}</h2>
<p style="color:#666;margin-bottom:1.5em">{get_meta_text()}</p>

<p style="color:#666;font-size:0.95em;line-height:1.6;max-width:32em">
  Напишите письмо на <a href="mailto:{HELP_EMAIL}?subject={subject}">{ HELP_EMAIL}</a> с темой <strong>"{HELP_SUBJECT}"</strong>.<br>
  В письме изложите ситуацию в самых общих чертах.<br>
  Или Telegram: <a href="https://t.me/{HELP_TELEGRAM[1:]}">{HELP_TELEGRAM}</a>
</p>'''


def get_help_form_error(project_name=None):
    """
    Возвращает текст ошибки для форм (JavaScript)
    
    Args:
        project_name: название проекта для темы письма (опционально)
    
    Returns:
        str: текст сообщения об ошибке
    """
    subject = f"{HELP_SUBJECT} {project_name}" if project_name else HELP_SUBJECT
    return f'✗ Ошибка. Напишите на {HELP_EMAIL} с темой "{subject}"'


def get_help_telegram(project_name=None):
    """
    Возвращает текст для Telegram (Markdown)
    
    Args:
        project_name: название проекта для темы письма (опционально)
    
    Returns:
        str: текст с Markdown-разметкой
    """
    subject = f"{HELP_SUBJECT} {project_name}" if project_name else HELP_SUBJECT
    return f"{HELP_QUESTION}\nПожалуйста, пишите: {HELP_EMAIL} с темой \"{subject}\" или {HELP_TELEGRAM}"


# ============================================================================
# ЭКСПОРТ ДЛЯ СПЕЦИФИЧНЫХ ПРОЕКТОВ
# ============================================================================

def get_for_olgarozet():
    """Для olgarozet.ru"""
    return get_help_html(project_name=None, style="default")


def get_for_cdl():
    """Для olgarozet.ru/chl/"""
    return get_help_html(project_name="ЦДЛ", style="default")


def get_for_paris():
    """Для parisinjanuary.ru"""
    return get_help_html(project_name="Paris 2026", style="paris")


def get_for_telegram():
    """Для @olgarozet (Telegram)"""
    return get_help_telegram(project_name=None)


# ============================================================================
# ВАЛИДАЦИЯ
# ============================================================================

def validate_all():
    """Проверяет, что все генераторы работают"""
    print("=" * 80)
    print("ВАЛИДАЦИЯ МЕТА-ПРИНЦИПА ПОМОЩИ")
    print("=" * 80)
    
    tests = [
        ("olgarozet.ru", get_for_olgarozet()),
        ("olgarozet.ru/chl/", get_for_cdl()),
        ("parisinjanuary.ru", get_for_paris()),
        ("@olgarozet (Telegram)", get_for_telegram()),
    ]
    
    for project, output in tests:
        print(f"\n{'─' * 80}")
        print(f"ПРОЕКТ: {project}")
        print(f"{'─' * 80}")
        print(output)
        
        # Проверки
        assert HELP_QUESTION in output, f"❌ {project}: нет вопроса"
        assert HELP_EMAIL in output, f"❌ {project}: нет email"
        assert HELP_SUBJECT in output, f"❌ {project}: нет темы"
        print(f"\n✅ {project}: все проверки пройдены")
    
    print("\n" + "=" * 80)
    print("✅ ВСЕ ПРОЕКТЫ ВАЛИДНЫ")
    print("=" * 80)


# ============================================================================
# CLI
# ============================================================================

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "validate":
            validate_all()
        elif command == "olgarozet":
            print(get_for_olgarozet())
        elif command == "cdl":
            print(get_for_cdl())
        elif command == "paris":
            print(get_for_paris())
        elif command == "telegram":
            print(get_for_telegram())
        else:
            print(f"Неизвестная команда: {command}")
            print("Доступные команды: validate, olgarozet, cdl, paris, telegram")
    else:
        validate_all()

