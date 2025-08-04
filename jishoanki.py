import customtkinter as ctk
import requests

app = ctk.CTk()
app.title("Jisho to Anki")
app.geometry("500x500")

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Input field
entry = ctk.CTkEntry(app, width=400, font=("Arial", 18), placeholder_text="Enter Romaji")
entry.pack(pady=20)

# Result label
result_label = ctk.CTkLabel(app, text="", font=("Arial", 16))
result_label.pack(pady=10)

# Fetch Anki deck names
def fetch_deck_names():
    payload = {"action": "deckNames", "version": 6}
    try:
        response = requests.post("http://localhost:8765", json=payload)
        return response.json().get("result", [])
    except:
        return []

raw_decks = fetch_deck_names()
decks = ["Select deck"] + raw_decks
selected_deck = ctk.StringVar(value="Select deck")

# Deck dropdown
deck_dropdown = ctk.CTkOptionMenu(app, values=decks, variable=selected_deck, font=("Arial", 18))
deck_dropdown.pack(pady=10)

# Jisho search
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

# Add to Anki
def add_to_anki(hiragana, romaji, meaning):
    deck = selected_deck.get()
    if deck == "Select deck":
        return {"error": "Please select a valid deck."}

    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deck,
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
    try:
        response = requests.post("http://localhost:8765", json=payload)
        return response.json()
    except:
        return {"error": "Failed to connect to AnkiConnect"}

last_result = {"reading": None, "romaji": None, "meaning": None}

# Button actions
def on_search():
    romaji = entry.get().strip()
    if not romaji:
        result_label.configure(text="❌ Enter a word.")
        add_button.configure(state="disabled")
        return

    result_label.configure(text="⏳ Loading...")
    add_button.configure(state="disabled")

    app.after(100, lambda: perform_search(romaji))

def perform_search(romaji):
    kanji, reading, meaning = search_jisho(romaji)
    if kanji:
        result_label.configure(
            text=f"Kanji/Kana: {kanji}\nHiragana: {reading}\nMeaning: {meaning}",
            justify="left"
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
    if result.get("error"):
        result_label.configure(text=f"⚠️ {result['error']}")
    else:
        result_label.configure(text="✅ Added to Anki.")
    add_button.configure(state="normal")

def on_add_key():
    if all(last_result.values()):
        on_add(last_result["reading"], last_result["romaji"], last_result["meaning"])
    else:
        result_label.configure(text="❌ Nothing to add. Search first.")

# Buttons
search_button = ctk.CTkButton(app, text="Search", command=on_search, font=("Arial", 18))
search_button.pack(pady=(10, 5))

add_button = ctk.CTkButton(app, text="Add to Anki", command=lambda: on_add(
    last_result["reading"], last_result["romaji"], last_result["meaning"]
), font=("Arial", 18), state="disabled")
add_button.pack(pady=10)

# Keyboard shortcuts
app.bind("<Return>", lambda event: on_search())
app.bind("<Control-Return>", lambda event: on_add_key())

app.mainloop()
