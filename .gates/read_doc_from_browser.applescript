tell application "Google Chrome"
    activate
    set docUrl to "https://docs.google.com/document/d/1AfAFbklq2RCtOCtaKX_SPQTGNir2pMR9pq3V8Ggmhx4/edit"
    
    -- Пробуем найти открытую вкладку с документом
    repeat with w in windows
        repeat with t in tabs of w
            if URL of t contains "1AfAFbklq2RCtOCtaKX_SPQTGNir2pMR9pq3V8Ggmhx4" then
                set active tab index of w to index of t
                set index of w to 1
                return "Found tab"
            end if
        end repeat
    end repeat
    
    -- Если не найдено, открываем новую вкладку
    tell window 1
        set URL of active tab to docUrl
    end tell
    
    delay 2
    
    -- Пробуем выделить весь текст и скопировать
    tell application "System Events"
        keystroke "a" using {command down}
        delay 0.5
        keystroke "c" using {command down}
        delay 0.5
    end tell
    
    return "Copied"
end tell


