#!/usr/bin/env python3
"""
Webhook Server — Мгновенная реакция на события (ZHE)
Gmail Push Notifications (Pub/Sub) + Calendar Push Notifications
"""

from flask import Flask, request, jsonify
from google_gate import GoogleGate
from export_substance import export_substance
from datetime import datetime
import json
import base64
import hmac
import hashlib

app = Flask(__name__)
gate = GoogleGate()

def trigger_export(reason):
    """Немедленный экспорт Субстанции"""
    print(f"\n{'=' * 60}")
    print(f"🔔 WEBHOOK: {reason}")
    print(f"{'=' * 60}")
    
    substance = export_substance()
    
    output = {
        'trigger': {
            'timestamp': datetime.now().isoformat(),
            'reason': reason,
            'type': 'webhook'
        },
        'substance': substance
    }
    
    filename = f"substance_webhook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Субстанция экспортирована: {filename}")
    print(f"✓ Задержка: < 1 секунда (ZHE)")
    print(f"{'=' * 60}\n")
    
    return filename

@app.route('/webhook/gmail', methods=['POST'])
def gmail_webhook():
    """
    Gmail Push Notification endpoint
    Google Pub/Sub отправляет POST при новом письме
    """
    try:
        # Декодировать Pub/Sub сообщение
        envelope = request.get_json()
        
        if not envelope:
            return jsonify({'error': 'No Pub/Sub message'}), 400
        
        # Извлечь данные
        pubsub_message = envelope.get('message', {})
        
        if pubsub_message:
            # Декодировать base64 данные
            data = base64.b64decode(pubsub_message.get('data', '')).decode('utf-8')
            
            # Триггер немедленного экспорта
            reason = f"Gmail Webhook: Новое письмо (historyId: {data})"
            trigger_export(reason)
            
            return jsonify({'status': 'success', 'processed': True}), 200
        
        return jsonify({'error': 'Invalid message format'}), 400
    
    except Exception as e:
        print(f"❌ Ошибка Gmail webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/calendar', methods=['POST'])
def calendar_webhook():
    """
    Google Calendar Push Notification endpoint
    Calendar API отправляет POST при изменении событий
    """
    try:
        # Извлечь заголовки
        channel_id = request.headers.get('X-Goog-Channel-ID')
        resource_state = request.headers.get('X-Goog-Resource-State')
        resource_uri = request.headers.get('X-Goog-Resource-URI')
        
        if resource_state == 'sync':
            # Начальная синхронизация, игнорируем
            return jsonify({'status': 'sync'}), 200
        
        # Триггер немедленного экспорта
        reason = f"Calendar Webhook: {resource_state} (канал: {channel_id})"
        trigger_export(reason)
        
        return jsonify({'status': 'success', 'processed': True}), 200
    
    except Exception as e:
        print(f"❌ Ошибка Calendar webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/cal.com', methods=['POST'])
def calcom_webhook():
    """
    Cal.com Webhook endpoint
    Cal.com отправляет POST при бронировании
    """
    try:
        data = request.get_json()
        
        # Cal.com отправляет разные типы событий
        trigger_event = data.get('triggerEvent')
        
        if trigger_event == 'BOOKING_CREATED':
            booking = data.get('payload', {})
            
            # Извлечь информацию о встрече
            title = booking.get('title', 'Новая консультация')
            start_time = booking.get('startTime')
            attendee = booking.get('attendees', [{}])[0].get('email', 'неизвестно')
            
            # Триггер немедленного экспорта
            reason = f"Cal.com: Бронирование '{title}' ({attendee}, {start_time})"
            trigger_export(reason)
            
            return jsonify({'status': 'success', 'processed': True}), 200
        
        return jsonify({'status': 'ignored', 'event': trigger_event}), 200
    
    except Exception as e:
        print(f"❌ Ошибка Cal.com webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Webhook Server (Google Gate)',
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == "__main__":
    print("=" * 60)
    print("Webhook Server — Мгновенная реакция (ZHE)")
    print("=" * 60)
    print("Endpoints:")
    print("  POST /webhook/gmail      — Gmail Push Notifications")
    print("  POST /webhook/calendar   — Calendar Push Notifications")
    print("  POST /webhook/cal.com    — Cal.com Webhooks")
    print("  GET  /health             — Health Check")
    print("=" * 60)
    print("\nСервер запущен на http://localhost:5000")
    print("Для публичного доступа используйте ngrok или Cloudflare Tunnel\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
