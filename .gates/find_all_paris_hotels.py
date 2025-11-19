#!/usr/bin/env python3
"""
Глубокий поиск информации о парижских отелях во всех группах пользователя.
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

gates_dir = Path(__file__).parent
sys.path.insert(0, str(gates_dir))

from telegram_group_gate import TelegramGroupGate


# Ключевые слова для поиска информации об отелях
HOTEL_KEYWORDS = [
    # Русский
    'отель', 'гостиница', 'бронирование', 'бронировать', 'бронь',
    'номер', 'ночь', 'ночей', 'проживание', 'размещение', 'размещ',
    'квартир', 'квартира', 'апартамент', 'апартаменты',
    # Английский
    'hotel', 'booking', 'reservation', 'room', 'night', 'nights',
    'accommodation', 'apartment', 'airbnb', 'hostel',
    # Французский
    'hôtel', 'réservation', 'chambre', 'nuit', 'nuits',
    'logement', 'hébergement', 'appartement',
    # Названия районов Парижа
    'saint lazare', 'saint-lazare', 'opéra', 'opera', 'marais',
    'montmartre', 'champs-élysées', 'champs elysees', 'louvre',
    'montparnasse', 'bastille', 'latin quarter', 'quartier latin',
    # Названия известных отелей
    'ritz', 'george v', 'plaza athénée', 'crillon', 'meurice',
    'lutetia', 'raphael', 'bristol', 'fouquet'
]

PARIS_KEYWORDS = ['париж', 'paris', 'париже', 'parisien']


async def get_all_groups(gate):
    """Получить список всех групп пользователя"""
    print("📋 Получение списка всех групп...")
    
    dialogs = await gate.client.get_dialogs()
    groups = []
    
    for dialog in dialogs:
        entity = dialog.entity
        if hasattr(entity, 'title'):  # Это группа или канал
            groups.append({
                'id': entity.id,
                'title': entity.title,
                'username': getattr(entity, 'username', None),
                'member_count': getattr(entity, 'participants_count', None)
            })
    
    return groups


async def search_hotels_in_group(gate, group_info, limit=1000):
    """Поиск информации об отелях в конкретной группе"""
    group_id = group_info['id']
    group_title = group_info['title']
    
    print(f"\n🔍 Обработка группы: {group_title}")
    
    try:
        # Читаем сообщения
        messages = await gate.read_messages(group_id, limit=limit)
        
        hotel_info = {
            'group': group_title,
            'group_id': group_id,
            'messages_found': [],
            'hotels_mentioned': set(),
            'locations_mentioned': set(),
            'links_found': [],
            'documents_found': []
        }
        
        # Анализируем каждое сообщение
        for msg in messages:
            text = msg.get('text', '').lower()
            
            # Проверяем наличие ключевых слов
            found_keywords = [kw for kw in HOTEL_KEYWORDS if kw in text]
            
            if found_keywords:
                # Проверяем, связано ли с Парижем
                is_paris_related = any(pk in text for pk in PARIS_KEYWORDS) or 'paris' in group_title.lower()
                
                if is_paris_related or found_keywords:
                    user = msg.get('from_user', {})
                    user_name = user.get('first_name', 'Unknown')
                    if user.get('last_name'):
                        user_name += ' ' + user.get('last_name')
                    
                    hotel_info['messages_found'].append({
                        'date': msg.get('date'),
                        'user': user_name,
                        'text': msg.get('text', ''),
                        'message_id': msg.get('message_id'),
                        'keywords': found_keywords,
                        'has_media': bool(msg.get('media'))
                    })
                    
                    # Извлекаем названия отелей
                    hotel_patterns = [
                        r'(?:отель|hotel|hôtel)\s+([A-ZА-Я][^\s,\.!?]+(?:\s+[A-ZА-Я][^\s,\.!?]+)*)',
                        r'([A-ZА-Я][^\s,\.!?]+(?:\s+[A-ZА-Я][^\s,\.!?]+)*)\s+(?:отель|hotel|hôtel)',
                    ]
                    
                    for pattern in hotel_patterns:
                        matches = re.findall(pattern, msg.get('text', ''), re.IGNORECASE)
                        for match in matches:
                            if isinstance(match, tuple):
                                match = match[0]
                            hotel_info['hotels_mentioned'].add(match.strip())
                    
                    # Извлекаем локации
                    location_patterns = [
                        r'saint[- ]?lazare',
                        r'opéra',
                        r'marais',
                        r'montmartre',
                        r'champs[- ]?élysées',
                        r'louvre',
                        r'montparnasse',
                        r'bastille',
                    ]
                    
                    for pattern in location_patterns:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        for match in matches:
                            hotel_info['locations_mentioned'].add(match.lower())
                    
                    # Ищем ссылки
                    if 'http' in text or 'www.' in text:
                        url_pattern = r'https?://[^\s\)]+|www\.[^\s\)]+'
                        urls = re.findall(url_pattern, text)
                        for url in urls:
                            hotel_info['links_found'].append({
                                'url': url,
                                'date': msg.get('date'),
                                'user': user_name,
                                'context': msg.get('text', '')[:200]
                            })
                    
                    # Проверяем медиа
                    if msg.get('media'):
                        media_type = msg['media'].get('type', '')
                        if media_type in ['document', 'photo']:
                            hotel_info['documents_found'].append({
                                'date': msg.get('date'),
                                'user': user_name,
                                'type': media_type,
                                'text': msg.get('text', '')[:200]
                            })
        
        hotel_info['hotels_mentioned'] = list(hotel_info['hotels_mentioned'])
        hotel_info['locations_mentioned'] = list(hotel_info['locations_mentioned'])
        
        return hotel_info
        
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return None


async def main():
    """Основная функция"""
    print("=" * 80)
    print("ГЛУБОКИЙ ПОИСК ИНФОРМАЦИИ О ПАРИЖСКИХ ОТЕЛЯХ")
    print("=" * 80)
    print()
    
    # Инициализация Gate
    try:
        gate = TelegramGroupGate()
        await gate.authenticate()
        print("✅ Подключено к Telegram\n")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return
    
    # Получаем все группы
    all_groups = await get_all_groups(gate)
    print(f"✅ Найдено групп: {len(all_groups)}\n")
    
    # Фильтруем группы, связанные с Парижем
    paris_groups = []
    for group in all_groups:
        title_lower = group['title'].lower()
        if any(pk in title_lower for pk in ['париж', 'paris']):
            paris_groups.append(group)
    
    print(f"📌 Группы, связанные с Парижем: {len(paris_groups)}\n")
    for group in paris_groups:
        print(f"  • {group['title']} ({group.get('member_count', '?')} участников)")
    
    # Обрабатываем все группы (не только парижские, на случай если там есть информация)
    print(f"\n🔍 Обработка всех групп (лимит: 1000 сообщений на группу)...")
    print("=" * 80)
    
    all_hotel_info = []
    
    # Сначала обрабатываем парижские группы
    for group in paris_groups:
        info = await search_hotels_in_group(gate, group, limit=1000)
        if info and info['messages_found']:
            all_hotel_info.append(info)
    
    # Затем обрабатываем остальные группы (но только если там есть упоминания Парижа)
    print(f"\n🔍 Проверка остальных групп на упоминания Парижа...")
    other_groups = [g for g in all_groups if g not in paris_groups]
    
    for group in other_groups[:20]:  # Ограничиваем 20 группами для скорости
        try:
            # Быстрая проверка - читаем только последние 100 сообщений
            messages = await gate.read_messages(group['id'], limit=100)
            has_paris = False
            for msg in messages:
                text = msg.get('text', '').lower()
                if any(pk in text for pk in PARIS_KEYWORDS):
                    has_paris = True
                    break
            
            if has_paris:
                print(f"  ✓ Найден Париж в группе: {group['title']}")
                info = await search_hotels_in_group(gate, group, limit=500)
                if info and info['messages_found']:
                    all_hotel_info.append(info)
        except:
            continue
    
    # Сохраняем результаты
    output_dir = gates_dir.parent / "Ольга" / "Дизайн-путешествия" / "PARIS-2026" / "hotels_research"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"paris_hotels_research_{timestamp}.json"
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'groups_processed': len(all_hotel_info),
        'total_groups_checked': len(all_groups),
        'paris_groups': len(paris_groups),
        'hotel_info': all_hotel_info
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Выводим итоги
    print("\n" + "=" * 80)
    print("✅ ПОИСК ЗАВЕРШЕН")
    print("=" * 80)
    
    print(f"\n📊 Статистика:")
    print(f"  Всего групп проверено: {len(all_groups)}")
    print(f"  Парижских групп: {len(paris_groups)}")
    print(f"  Групп с информацией об отелях: {len(all_hotel_info)}")
    
    total_messages = sum(len(info['messages_found']) for info in all_hotel_info)
    total_hotels = len(set(hotel for info in all_hotel_info for hotel in info['hotels_mentioned']))
    total_links = sum(len(info['links_found']) for info in all_hotel_info)
    
    print(f"  Найдено сообщений об отелях: {total_messages}")
    print(f"  Упоминаний отелей: {total_hotels}")
    print(f"  Ссылок: {total_links}")
    
    print(f"\n📁 Результаты сохранены: {output_file}")
    
    # Выводим найденные отели
    if all_hotel_info:
        print("\n🏨 НАЙДЕННЫЕ ОТЕЛИ И ИНФОРМАЦИЯ:\n")
        for info in all_hotel_info:
            print(f"📱 Группа: {info['group']}")
            if info['hotels_mentioned']:
                print(f"   Отели: {', '.join(info['hotels_mentioned'])}")
            if info['locations_mentioned']:
                print(f"   Локации: {', '.join(info['locations_mentioned'])}")
            print(f"   Сообщений: {len(info['messages_found'])}")
            print()
    
    await gate.close()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

