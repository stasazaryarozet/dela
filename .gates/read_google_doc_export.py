#!/usr/bin/env python3
"""
Чтение Google Docs документа через экспорт в текстовом формате
"""
import requests
import json
import os

def read_google_doc_export(doc_id):
    """Прочитать Google Docs документ через экспорт"""
    print("=" * 80)
    print("ЧТЕНИЕ GOOGLE DOCS ДОКУМЕНТА (ЭКСПОРТ)")
    print("=" * 80)
    print()
    
    # Пробуем разные форматы экспорта
    export_urls = [
        f"https://docs.google.com/document/d/{doc_id}/export?format=txt",
        f"https://docs.google.com/document/d/{doc_id}/export?format=html",
    ]
    
    for url in export_urls:
        try:
            print(f"📥 Пробую экспорт: {url}")
            response = requests.get(url, allow_redirects=True, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                if content and len(content) > 100:  # Проверяем, что получили реальный контент
                    print(f"✅ Успешно получен контент ({len(content)} символов)")
                    print()
                    print("=" * 80)
                    print("СОДЕРЖИМОЕ ДОКУМЕНТА")
                    print("=" * 80)
                    print()
                    print(content)
                    print()
                    print("=" * 80)
                    
                    # Сохраняем результат
                    result = {
                        'doc_id': doc_id,
                        'export_url': url,
                        'content': content,
                        'length': len(content)
                    }
                    
                    output_file = os.path.join(os.path.dirname(__file__), 'google_doc_export.json')
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    
                    print(f"\n💾 Результат сохранён: {output_file}")
                    return result
                else:
                    print(f"⚠️ Получен пустой или слишком короткий контент")
            else:
                print(f"❌ Ошибка HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            continue
    
    print("\n❌ Не удалось прочитать документ через экспорт")
    print("💡 Возможные причины:")
    print("   - Документ не публичный")
    print("   - Требуется авторизация")
    print("   - Документ недоступен")
    
    return None

if __name__ == '__main__':
    # ID документа из ссылки
    doc_id = '1AfAFbklq2RCtOCtaKX_SPQTGNir2pMR9pq3V8Ggmhx4'
    
    read_google_doc_export(doc_id)


