#!/usr/bin/env python3
"""
Поиск контакта Сноба через Google Contacts
и попытка найти WhatsApp номер
"""
import sys
import os
from pathlib import Path

gates_dir = Path(__file__).parent.parent
sys.path.insert(0, str(gates_dir / 'google'))

def find_snob_contact():
    """Поиск контакта Сноба в Google Contacts"""
    print("=" * 80)
    print("ПОИСК КОНТАКТА СНОБ ЧЕРЕЗ GOOGLE CONTACTS")
    print("=" * 80)
    print()
    
    try:
        from google_gate import GoogleGate
        
        gate = GoogleGate(
            credentials_path=str(gates_dir / 'google' / 'credentials.json'),
            token_path=str(gates_dir / 'google' / 'token.pickle')
        )
        
        contacts_service = gate.contacts()
        
        # Поиск по ключевым словам
        search_terms = ['сноб', 'snob', 'редакция', 'editor']
        
        for term in search_terms:
            print(f"🔍 Поиск по запросу: '{term}'...")
            try:
                results = contacts_service.people().searchContacts(query=term).execute()
                people = results.get('results', [])
                
                if people:
                    print(f"✅ Найдено контактов: {len(people)}")
                    for person in people:
                        person_data = person.get('person', {})
                        names = person_data.get('names', [])
                        phones = person_data.get('phoneNumbers', [])
                        emails = person_data.get('emailAddresses', [])
                        
                        name = names[0].get('displayName', 'Без имени') if names else 'Без имени'
                        print(f"\n  👤 {name}")
                        
                        if phones:
                            for phone in phones:
                                phone_num = phone.get('value', '')
                                print(f"     📱 {phone_num}")
                        
                        if emails:
                            for email in emails:
                                email_addr = email.get('value', '')
                                print(f"     📧 {email_addr}")
                    
                    return people
            except Exception as e:
                print(f"   ⚠️  Ошибка поиска: {e}")
                continue
        
        print("\nℹ️  Контакт Сноба не найден в Google Contacts")
        return None
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    find_snob_contact()


