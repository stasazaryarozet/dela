#!/usr/bin/env python3
"""
File Watcher — мониторинг интенций от Multitool Too

Следит за:
- from_multitool_intentions.txt
- from_multitool_quick.json
- from_multitool_data.json

При изменении → обновляет current_state.json и actions.sh
"""

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CONTEXT_DIR = Path(__file__).parent

class IntentionHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        
        filename = Path(event.src_path).name
        
        if filename == 'from_multitool_intentions.txt':
            print(f"\n📱 Новая интенция от Multitool Too")
            self.handle_intention()
        
        elif filename == 'from_multitool_quick.json':
            print(f"\n⚡ Быстрая команда от Multitool Too")
            # TODO: выполнить команду
        
        elif filename == 'from_multitool_data.json':
            print(f"\n📊 Данные от Multitool Too")
            # TODO: обработать данные
    
    def handle_intention(self):
        intentions_file = CONTEXT_DIR / 'from_multitool_intentions.txt'
        
        if intentions_file.exists():
            with open(intentions_file, 'r') as f:
                lines = f.readlines()
            
            if lines:
                intention = lines[-1].strip()
                print(f"   → {intention}")
                
                # Обновить current_state
                import json
                state_file = CONTEXT_DIR / 'current_state.json'
                
                if state_file.exists():
                    with open(state_file, 'r') as f:
                        state = json.load(f)
                    
                    state['last_intention'] = intention
                    state['timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                    
                    with open(state_file, 'w') as f:
                        json.dump(state, f, indent=2)
                    
                    print(f"   ✅ Обновлено current_state.json")

print("🔄 File Watcher: Мониторинг интенций")
print(f"   Директория: {CONTEXT_DIR}")
print("\n⏳ Жду изменений (Ctrl+C для остановки)...\n")

handler = IntentionHandler()
observer = Observer()
observer.schedule(handler, str(CONTEXT_DIR), recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    print("\n\n✅ Watcher остановлен")

observer.join()
