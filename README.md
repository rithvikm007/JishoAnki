# JishoAnki – Jisho to Anki Desktop App

A minimalist desktop app that lets you search Japanese words from [Jisho.org](https://jisho.org) and add them directly to your Anki deck with a single click.

Built with **Python**, **CustomTkinter**, and **AnkiConnect**.
---

## Features

- 🔍 Search for Japanese words (Romaji input)
- 📖 View Kanji, Hiragana, and English meaning
- 📚 Select from existing Anki decks
- ➕ Add directly to Anki via AnkiConnect
- ⌨️ Keyboard shortcuts:  
  - `Enter` → Search  
  - `Ctrl+Enter` → Add to Anki

---

## Requirements

- **Python** 3.8+
- [Anki](https://apps.ankiweb.net/) (desktop version)
- [AnkiConnect](https://foosoft.net/projects/anki-connect/) plugin installed and running
- A note type in Anki named **"Japanese Words"** with the following fields:
  - `hiragana`
  - `romaji`
  - `meanings`

---

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/JishoAnki.git
cd JishoAnki
````

### 2. Install dependencies

You can use `pip`:


```bash
pip install customtkinter requests
```

### 3. Start Anki and enable AnkiConnect

Open Anki (desktop), go to **Tools → Add-ons**, and make sure **AnkiConnect** is installed and enabled.
You can install it using code: `2055492159`

### 4. Run the app

```bash
python jishoanki.py
```

---

## Packaging it into an Executable

To convert the app into a standalone `.exe` (Windows):

### 1. Install pyinstaller

```bash
pip install pyinstaller
```

### 2. Create the executable

```bash
pyinstaller --noconfirm --onefile --windowed app.py
```

* The `.exe` will be in the `dist/` folder.
* Use `--icon=icon.ico` if you have a custom icon.

---

## Notes

* Make sure Anki is running before using the app.
* If deck dropdown doesn't populate, check if AnkiConnect is running on `localhost:8765`.
* This app uses the **"Japanese Words"** note type. You can customize the fields, but you’ll need to modify the code accordingly.

---

## License

MIT License