#!/usr/bin/env python3
"""
Чтение Google Docs документа по ID
"""
import os
import sys
import json

# Добавляем путь к google gate
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'google'))
from google_gate import GoogleGate

def extract_text_from_doc(doc_content):
    """Извлечь текст из структуры Google Docs"""
    text_parts = []
    
    if 'body' in doc_content and 'content' in doc_content['body']:
        for element in doc_content['body']['content']:
            if 'paragraph' in element:
                para = element['paragraph']
                if 'elements' in para:
                    for elem in para['elements']:
                        if 'textRun' in elem:
                            text = elem['textRun'].get('content', '')
                            text_parts.append(text)
    
    return ''.join(text_parts)

def read_google_doc(doc_id):
    """Прочитать Google Docs документ"""
    print("=" * 80)
    print("ЧТЕНИЕ GOOGLE DOCS ДОКУМЕНТА")
    print("=" * 80)
    print()
    
    # Инициализируем Google Gate
    gate = GoogleGate(
        credentials_path=os.path.join(os.path.dirname(__file__), 'google', 'credentials.json'),
        token_path=os.path.join(os.path.dirname(__file__), 'google', 'token.pickle')
    )
    
    # Получаем Docs service
    docs_service = gate.docs()
    
    print(f"📄 Читаю документ: {doc_id}")
    print()
    
    try:
        # Получаем документ
        doc = docs_service.documents().get(documentId=doc_id).execute()
        
        # Извлекаем заголовок
        title = doc.get('title', 'Без названия')
        print(f"📋 Заголовок: {title}")
        print()
        
        # Извлекаем текст
        full_text = extract_text_from_doc(doc)
        
        print("=" * 80)
        print("СОДЕРЖИМОЕ ДОКУМЕНТА")
        print("=" * 80)
        print()
        print(full_text)
        print()
        print("=" * 80)
        
        # Сохраняем в JSON для дальнейшей обработки
        result = {
            'doc_id': doc_id,
            'title': title,
            'text': full_text,
            'full_structure': doc
        }
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка при чтении документа: {e}")
        return None

if __name__ == '__main__':
    # ID документа из ссылки
    doc_id = '1AfAFbklq2RCtOCtaKX_SPQTGNir2pMR9pq3V8Ggmhx4'
    
    result = read_google_doc(doc_id)
    
    if result:
        # Сохраняем результат
        output_file = os.path.join(os.path.dirname(__file__), 'google_doc_content.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Результат сохранён: {output_file}")


