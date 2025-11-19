#!/usr/bin/env python3
"""
Integration Manager: обнаружение и управление интеграциями для всех проектов
"""
import json
import os
from pathlib import Path

ROOT = Path("/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○")

def discover_projects():
    """Обнаруживает все проекты в ○"""
    projects = {}
    
    for item in ROOT.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            projects[item.name] = {
                'path': str(item),
                'has_config': (item / '.integrations.json').exists(),
                'sub_projects': []
            }
            
            # Ищем подпроекты
            for sub in item.iterdir():
                if sub.is_dir() and not sub.name.startswith('.'):
                    projects[item.name]['sub_projects'].append({
                        'name': sub.name,
                        'path': str(sub),
                        'has_config': (sub / '.integrations.json').exists()
                    })
    
    return projects

def generate_config_template(project_path):
    """Генерирует шаблон .integrations.json"""
    template = {
        "project": Path(project_path).name,
        "providers": {},
        "auto_actions": [],
        "watchers": []
    }
    
    config_path = Path(project_path) / '.integrations.json'
    
    if not config_path.exists():
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        return True
    return False

def scan_integrations():
    """Сканирует все проекты и создает глобальный статус"""
    projects = discover_projects()
    
    print("🔍 Обнаружение проектов в ○...\n")
    print("=" * 80)
    
    for project_name, project_info in projects.items():
        print(f"\n📁 {project_name}/")
        print(f"   Путь: {project_info['path']}")
        print(f"   Конфиг: {'✅' if project_info['has_config'] else '❌ отсутствует'}")
        
        if not project_info['has_config']:
            print(f"   → Создаю .integrations.json...")
            if generate_config_template(project_info['path']):
                print(f"   ✅ Создан")
        
        if project_info['sub_projects']:
            print(f"\n   Подпроекты:")
            for sub in project_info['sub_projects']:
                print(f"     • {sub['name']}: {'✅' if sub['has_config'] else '❌'}")
                
                if not sub['has_config']:
                    print(f"       → Создаю .integrations.json...")
                    if generate_config_template(sub['path']):
                        print(f"       ✅ Создан")
    
    print("\n" + "=" * 80)
    print("✅ Сканирование завершено\n")
    
    # Сохраняем глобальный статус
    status = {
        'root': str(ROOT),
        'projects': projects,
        'providers': {
            'telegram': {
                'status': 'connected',
                'accounts': ['olga', 'azarya']
            },
            'google': {
                'status': 'connected',
                'services': ['gmail', 'calendar', 'drive', 'contacts', 'sheets', 'forms']
            },
            'github': {
                'status': 'connected'
            },
            'calcom': {
                'status': 'connected'
            },
            'instagram': {
                'status': 'partial',
                'coverage': '60%'
            }
        }
    }
    
    with open(ROOT / '.gates' / 'integration_status.json', 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"💾 Статус сохранен: .gates/integration_status.json")

if __name__ == '__main__':
    scan_integrations()
