# WhatsApp Integration — Quick Start

## Быстрая настройка

### Для Azarya

```bash
cd .gates/whatsapp/scripts
python3 setup_azarya_whatsapp.py
```

### Для Olga

```bash
cd .gates/whatsapp/scripts
python3 setup_olga_whatsapp.py
```

## Использование

```python
from .gates.whatsapp.whatsapp_multi_user_gate import WhatsAppMultiUserGate

# Azarya
gate = WhatsAppMultiUserGate(user='azarya')
gate.send_message(to='79991234567', message='Привет!')

# Olga
gate = WhatsAppMultiUserGate(user='olga')
messages = gate.get_messages(limit=50)
```

## Тестирование

```bash
python3 .gates/whatsapp/test_integration.py
```

## Документация

- [Архитектура](WHATSAPP_DEEP_INTEGRATION_ARCHITECTURE.md)
- [README](README.md)


