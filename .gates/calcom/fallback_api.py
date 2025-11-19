#!/usr/bin/env python3
"""
Flask API для Fallback Booking System
"""

from flask import Flask, jsonify, request
from fallback_booking import OlgaBookingFallback
import os
from pathlib import Path

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Инициализируем fallback систему
fallback = OlgaBookingFallback()

@app.route('/api/slots', methods=['GET'])
def get_slots():
    """Получить доступные слоты"""
    try:
        slots = fallback.get_available_slots()
        return jsonify(slots)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/book', methods=['POST'])
def book_slot():
    """Забронировать слот"""
    try:
        data = request.json
        
        event_id = data.get('event_id')
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        
        if not all([event_id, name, email]):
            return jsonify({'error': 'Не все обязательные поля заполнены'}), 400
        
        booking = fallback.book_slot(event_id, name, email, phone)
        
        if booking:
            return jsonify(booking)
        else:
            return jsonify({'error': 'Ошибка бронирования'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cancel', methods=['POST'])
def cancel_booking():
    """Отменить бронирование"""
    try:
        data = request.json
        booking_id = data.get('booking_id')
        
        if not booking_id:
            return jsonify({'error': 'booking_id не указан'}), 400
        
        success = fallback.cancel_booking(booking_id)
        
        if success:
            return jsonify({'status': 'cancelled'})
        else:
            return jsonify({'error': 'Бронирование не найдено'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """Главная страница с UI"""
    ui_path = Path(__file__).parent / 'fallback_booking_ui.html'
    with open(ui_path, 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == '__main__':
    print("=" * 60)
    print("FALLBACK BOOKING API — Ольга Розет")
    print("=" * 60)
    print()
    print("Доступно на: http://localhost:5000")
    print("API endpoints:")
    print("  GET  /api/slots  - получить доступные слоты")
    print("  POST /api/book   - забронировать слот")
    print("  POST /api/cancel - отменить бронирование")
    print()
    print("=" * 60)
    
    app.run(debug=True, port=5000)

