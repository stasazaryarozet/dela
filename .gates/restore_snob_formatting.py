#!/usr/bin/env python3
"""
Восстановление форматирования Google Docs документа для "Сноб"
Добавляет заголовки и жирный текст для лида
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'google'))
from google_gate import GoogleGate

DOC_ID = "1AfAFbklq2RCtOCtaKX_SPQTGNir2pMR9pq3V8Ggmhx4"

def restore_formatting():
    """Восстановить форматирование документа"""
    print("=" * 80)
    print("ВОССТАНОВЛЕНИЕ ФОРМАТИРОВАНИЯ GOOGLE DOCS")
    print("=" * 80)
    print()
    
    gate = GoogleGate(
        credentials_path=os.path.join(os.path.dirname(__file__), 'google', 'credentials.json'),
        token_path=os.path.join(os.path.dirname(__file__), 'google', 'token.pickle')
    )
    
    docs_service = gate.docs()
    
    print(f"📄 Восстанавливаю форматирование документа: {DOC_ID}")
    print()
    
    # Получаем документ
    doc = docs_service.documents().get(documentId=DOC_ID).execute()
    body = doc.get('body', {})
    content = body.get('content', [])
    
    requests = []
    
    # Находим текст в документе и применяем форматирование
    full_text = ""
    for element in content:
        if 'paragraph' in element:
            para = element['paragraph']
            if 'elements' in para:
                for elem in para['elements']:
                    if 'textRun' in elem:
                        text = elem['textRun'].get('content', '')
                        full_text += text
    
    # Находим позиции для форматирования
    lead_start = full_text.find("В эпоху алгоритмов и 3D-принтеров")
    lead_end = full_text.find("Ольгой Розет.", lead_start) + len("Ольгой Розет.")
    
    h2_1_start = full_text.find("Причины формирования ценности несовершенства")
    h2_1_end = h2_1_start + len("Причины формирования ценности несовершенства")
    
    h2_2_start = full_text.find("Изменения в индустрии дизайна")
    h2_2_end = h2_2_start + len("Изменения в индустрии дизайна")
    
    h2_3_start = full_text.find("Отражение эстетики несовершенства в винтажной мебели")
    h2_3_end = h2_3_start + len("Отражение эстетики несовершенства в винтажной мебели и предметах интерьера")
    
    # Но нам нужны индексы символов в документе, а не в тексте
    # Используем поиск по тексту для нахождения индексов
    
    # 1. Форматируем лид жирным
    if lead_start >= 0 and lead_end > lead_start:
        # Находим индекс в документе через поиск
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,  # Начинаем с начала документа
                    'endIndex': 500   # Примерно до конца лида
                },
                'textStyle': {
                    'bold': True
                },
                'fields': 'bold'
            }
        })
    
    # 2. Форматируем заголовки как Heading 2
    # Используем replaceAllText для поиска и форматирования заголовков
    
    # Находим заголовки через поиск текста
    requests.append({
        'updateParagraphStyle': {
            'range': {
                'startIndex': 1,
                'endIndex': len(full_text)
            },
            'paragraphStyle': {
                'namedStyleType': 'NORMAL_TEXT'
            },
            'fields': 'namedStyleType'
        }
    })
    
    # Более точный подход: используем поиск и замену с форматированием
    # Найдем каждый заголовок и применим стиль
    
    print(f"📝 Применяю форматирование...")
    print()
    
    # Альтернативный подход: используем поиск текста для точного определения позиций
    # Сначала найдем все заголовки через поиск
    
    # Проще: используем replaceAllText с сохранением форматирования
    # Или применяем стили к найденным фразам
    
    # Восстанавливаем через поиск конкретных фраз
    headings = [
        "Причины формирования ценности несовершенства",
        "Изменения в индустрии дизайна",
        "Отражение эстетики несовершенства в винтажной мебели и предметах интерьера"
    ]
    
    # Для каждого заголовка находим и форматируем
    for heading in headings:
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': 1,  # Будет найдено через поиск
                    'endIndex': len(full_text)
                },
                'paragraphStyle': {
                    'namedStyleType': 'HEADING_2'
                },
                'fields': 'namedStyleType'
            }
        })
    
    # Более правильный подход: читаем структуру документа и применяем стили к нужным параграфам
    # Перечитываем документ для получения точных индексов
    doc = docs_service.documents().get(documentId=DOC_ID).execute()
    body = doc.get('body', {})
    content = body.get('content', [])
    
    requests = []
    current_index = 1
    
    for element in content:
        if 'paragraph' in element:
            para = element['paragraph']
            para_text = ""
            if 'elements' in para:
                for elem in para['elements']:
                    if 'textRun' in elem:
                        para_text += elem['textRun'].get('content', '')
            
            para_start = current_index
            para_end = current_index + len(para_text)
            
            # Проверяем, является ли параграф заголовком
            para_text_clean = para_text.strip()
            if para_text_clean in headings:
                # Применяем стиль HEADING_2
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': para_start,
                            'endIndex': para_end
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_2'
                        },
                        'fields': 'namedStyleType'
                    }
                })
            
            # Проверяем, является ли параграф лидом
            if para_text_clean.startswith("В эпоху алгоритмов и 3D-принтеров"):
                # Применяем жирный стиль
                requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': para_start,
                            'endIndex': para_end - 1  # Минус символ новой строки
                        },
                        'textStyle': {
                            'bold': True
                        },
                        'fields': 'bold'
                    }
                })
            
            current_index = para_end
    
    if requests:
        try:
            result = docs_service.documents().batchUpdate(
                documentId=DOC_ID,
                body={'requests': requests}
            ).execute()
            
            print("✅ Форматирование восстановлено!")
            print(f"✅ Применено изменений: {len(result.get('replies', []))}")
            print()
            print("📄 Документ: https://docs.google.com/document/d/" + DOC_ID)
            return True
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print("⚠️ Нет изменений для применения")
        return False

if __name__ == '__main__':
    success = restore_formatting()
    sys.exit(0 if success else 1)


