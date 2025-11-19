# Multitool Too → Дела Integration

**Location:** iCloud Drive/Дела/.context/

**Protocol:** File-based bidirectional

---

## Shortcuts to create in iPhone

### 1. "Дела Status"

**Action:**
- Get file: `Shortcuts/iCloud Drive/Дела/.context/to_multitool.json`
- Get dictionary value for "coverage"
- Get dictionary value for "active_providers"
- Show notification: "Дела: {coverage}% | Active: {providers}"

---

### 2. "Дела Publish"

**Action:**
- Get file: `Shortcuts/iCloud Drive/Дела/.context/content_ready.txt`
- Get text from lines 1-25 (first post)
- Copy to clipboard
- Open Instagram app
- Show alert: "Post copied. Paste and publish."

---

### 3. "Дела Intention"

**Input:** Ask for text

**Action:**
- Get text from input
- Append to file: `Shortcuts/iCloud Drive/Дела/.context/from_multitool_intentions.txt`
- Show notification: "Intention sent to Claude"

---

### 4. "Дела Substance"

**Action:**
- Get file: `Shortcuts/iCloud Drive/Дела/.context/substance_latest.json`
- Get dictionary value for "data.gmail.messages_count"
- Get dictionary value for "data.calendar.events_count"
- Show: "Emails: {count} | Events: {count}"

---

### 5. "Дела Execute"

**Action:**
- Get file: `Shortcuts/iCloud Drive/Дела/.context/actions.sh`
- Extract lines starting with "echo" (descriptions)
- Show as list
- Or: SSH to Mac and execute file

---

## Automation triggers

### "When file changes: to_multitool.json"

**Automation:**
- Trigger: File watcher (Shortcuts automation)
- Run: "Дела Status"
- If "ready_actions" > 0 → show notification

### "Daily 9 AM"

**Automation:**
- Run: "Дела Status"
- Run: "Дела Substance"
- Show summary notification

---

## Two-way flow

**Дела → Multitool:**
- I update `.context/` files
- iCloud syncs to iPhone
- Shortcuts read and show/execute

**Multitool → Дела:**
- You write to `from_multitool_*.txt`
- iCloud syncs to Mac
- I read and act

---

**All files in:** `iCloud Drive/Дела/.context/`

**Create these 5 shortcuts in iPhone Shortcuts app.**

**Point them to `.context/` folder.**
