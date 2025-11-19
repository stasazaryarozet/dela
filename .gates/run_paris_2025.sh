#!/bin/bash
# Скрипт для запуска обработки группы "Париж 2025"
# Использует существующие credentials из telegram-bot

cd "$(dirname "$0")"

export TELEGRAM_API_ID='28482390'
export TELEGRAM_API_HASH='7392719c7cef090ff844c1da3f05f807'
export TELEGRAM_PHONE='+79854417201'

echo "🚀 Запуск обработки группы 'Париж 2025'"
echo ""

python3 process_paris_2025_group.py

