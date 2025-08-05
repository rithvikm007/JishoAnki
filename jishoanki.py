import customtkinter as ctk
import requests

app = ctk.CTk()
app.title("Jisho to Anki")
app.geometry("650x600")

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

# Editable Fields
form_frame = ctk.CTkFrame(app)
form_frame.pack(pady=10)

label_font = ("Arial", 16)
entry_font = ("Arial", 16)

kanji_label = ctk.CTkLabel(form_frame, text="Kanji / Kana:", font=label_font)
kanji_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
kanji_entry = ctk.CTkEntry(form_frame, width=400, font=entry_font)
kanji_entry.grid(row=0, column=1, padx=10, pady=5)

hiragana_label = ctk.CTkLabel(form_frame, text="Hiragana:", font=label_font)
hiragana_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
hiragana_entry = ctk.CTkEntry(form_frame, width=400, font=entry_font)
hiragana_entry.grid(row=1, column=1, padx=10, pady=5)

meaning_label = ctk.CTkLabel(form_frame, text="Meaning:", font=label_font)
meaning_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
meaning_entry = ctk.CTkEntry(form_frame, width=400, font=entry_font)
meaning_entry.grid(row=2, column=1, padx=10, pady=5)


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
        kanji_entry.delete(0, "end")
        kanji_entry.insert(0, kanji)

        hiragana_entry.delete(0, "end")
        hiragana_entry.insert(0, reading)

        meaning_entry.delete(0, "end")
        meaning_entry.insert(0, meaning)

        result_label.configure(text="✅ Edit fields and click 'Add to Anki'.")
        add_button.configure(state="normal")
    else:
        result_label.configure(text="❌ Word not found on Jisho.")
        add_button.configure(state="disabled")

def on_add():
    kanji = kanji_entry.get().strip()
    hiragana = hiragana_entry.get().strip()
    romaji = entry.get().strip()
    meaning = meaning_entry.get().strip()

    if not (hiragana and romaji and meaning):
        result_label.configure(text="❌ Fill all fields before adding.")
        return

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

# Buttons
search_button = ctk.CTkButton(app, text="Search", command=on_search, font=("Arial", 18))
search_button.pack(pady=(10, 5))

add_button = ctk.CTkButton(app, text="Add to Anki", command=on_add, font=("Arial", 18), state="disabled")
add_button.pack(pady=10)

# Keyboard shortcuts
app.bind("<Return>", lambda event: on_search())
app.bind("<Control-Return>", lambda event: on_add())

app.mainloop()
