#!/bin/bash
# Actions from Claude — executable by Multitool Too
# Updated: 2025-11-11 21:06

cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○"

# Action 1: Export latest Substance from Google
echo "📦 Exporting Substance from Google..."
python3 .gates/google/export_substance.py

# Action 2: Show first post ready to publish
echo ""
echo "📝 First post ready (copy to Instagram):"
echo "========================================"
head -25 Ольга/posts_month.txt

# Action 3: Check webhook server status
echo ""
echo "🔗 Webhook server status:"
lsof -i:5000 | grep LISTEN && echo "✅ Running" || echo "⚠️  Not running"

# Action 4: Show integration coverage
echo ""
python3 .gates/autoconnect.py | grep "Покрытие\|Coverage"

echo ""
echo "✅ Actions completed"
echo "Next: Publish post to Instagram (@olga.rozet)"
