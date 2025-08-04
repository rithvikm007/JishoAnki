import customtkinter as ctk
import requests

def search_jisho(word):
    url = f"https://jisho.org/api/v1/search/words?keyword={word}"
    response = requests.get(url)
    if response.status_code != 200:
        return None, None, None

    data = response.json()
    if data['data']:
        entry = data['data'][0]
        japanese = entry['japanese'][0]
        senses = entry['senses'][0]

        word_kanji = japanese.get('word', '') or japanese.get('reading', '')
        reading = japanese.get('reading', '')
        meaning = ', '.join(senses['english_definitions'])

        return word_kanji, reading, meaning
    else:
        return None, None, None

def add_to_anki(hiragana, romaji, meaning):
    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": "Japanese Self::Words",
                "modelName": "Japanese Words",
                "fields": {
                    "hiragana": hiragana,
                    "romaji": romaji,
                    "meanings": meaning
                },
                "options": {
                    "allowDuplicate": False
                },
                "tags": ["auto"]
            }
        }
    }
    response = requests.post("http://localhost:8765", json=payload)
    return response.json()

# ---- GUI Setup ----

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("600x400")
app.title("Jisho → Anki")

entry = ctk.CTkEntry(app, placeholder_text="Enter Romaji", font=("Arial", 18))
entry.pack(pady=20)

result_label = ctk.CTkLabel(app, text="", justify="left", font=("Arial", 18), wraplength=550, anchor="w")
result_label.pack(pady=10)

last_result = {"reading": None, "romaji": None, "meaning": None}  # Cache for Ctrl+Enter

def on_search():
    romaji = entry.get().strip()
    if not romaji:
        result_label.configure(text="❌ Enter a word.")
        add_button.configure(state="disabled")
        return

    result_label.configure(
        text = "⏳ Loading..."
        # text="✅ Kanji/Kana: ⏳ Loading...\n📖 Hiragana: ⏳ Loading...\n💡 Meaning: ⏳ Loading..."
    )
    add_button.configure(state="disabled")
    
    app.after(100, lambda: perform_search(romaji))

def perform_search(romaji):
    kanji, reading, meaning = search_jisho(romaji)
    if kanji:
        result_label.configure(
            text=f"✅ Kanji/Kana: {kanji}\n📖 Hiragana: {reading}\n💡 Meaning: {meaning}"
        )
        last_result.update({"reading": reading, "romaji": romaji, "meaning": meaning})
        add_button.configure(state="normal")
    else:
        result_label.configure(text="❌ Word not found on Jisho.")
        last_result.update({"reading": None, "romaji": None, "meaning": None})



def on_add(hiragana, romaji, meaning):
    result_label.configure(text="⏳ Adding to Anki...")
    add_button.configure(state="disabled")

    app.after(100, lambda: perform_add(hiragana, romaji, meaning))

def perform_add(hiragana, romaji, meaning):
    result = add_to_anki(hiragana, romaji, meaning)
    if 'error' in result and result['error']:
        result_label.configure(text=f"⚠️ Anki Error: {result['error']}")
    else:
        result_label.configure(text="✅ Added to Anki.")

    add_button.configure(state="normal")


def on_add_key():
    if all(last_result.values()):
        on_add(last_result["reading"], last_result["romaji"], last_result["meaning"])
    else:
        result_label.configure(text="❌ Nothing to add. Search first.")

search_button = ctk.CTkButton(app, text="Search", command=on_search, font=("Arial", 18))
search_button.pack(pady=10)

add_button = ctk.CTkButton(app, text="Add to Anki", command=on_add_key, font=("Arial", 18), state="disabled")
add_button.pack(pady=10)

# ---- Key Bindings ----
app.bind("<Return>", lambda event: on_search())
app.bind("<Control-Return>", lambda event: on_add_key())

app.mainloop()
