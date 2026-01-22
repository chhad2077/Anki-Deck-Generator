# 🗂️ Anki Chinese Deck Generator

An automated tool for generating high-quality Chinese vocabulary Anki decks using AI-powered enrichment. This generator transforms simple word lists into feature-rich flashcards including Pinyin, example sentences, high-quality audio, and AI-generated illustrations.

## 🚀 Quick Start Workflow

To generate a new Anki deck, follow these standard steps:

1.  **Prepare CSV**: Create a new CSV file in the `csv_files/` directory with headers: `Chinese, Pinyin, English, Sentence, Image`.
2.  **Fill Words**: Take a screenshot of your study material and ask the AI agent to fill the `Chinese` and `English` columns for you.
3.  **✨ Enrich CSV**: Use the AI-specific slash command `/enrich-csv` or ask the AI to "enrich [filename].csv". 
    - This will automatically generate **Pinyin**, **Example Sentences** (with translations), and **Minimalist Illustrations**.
    - Images are saved to the `images/` folder.
4.  **🎴 Generate Deck**: Run the generation script in your terminal:
    ```bash
    python generate_deck.py [filename].csv
    ```
    - This creates an `.apkg` file in the `output/` folder.
    - It generates high-quality **audio clips** for both words and sentences in the `audio/` folder.
5.  **📦 Archive**: After importing the `.apkg` file into Anki, move the processed CSV to the `archived_csvs/` folder to keep your workspace clean.

---

## 💻 Running the Web App Locally

We recommend using **[uv](https://docs.astral.sh/uv/)**, a modern, blazing-fast Python package manager that handles virtual environments and dependencies automatically.

### 1. Install `uv`
If you don't have `uv` installed yet:

```bash
# On macOS (Homebrew)
brew install uv

# On macOS/Linux (Standalone script)
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Launch the App (The Modern Way 🚀)
Simply run the following command in the project root. `uv` will automatically create a virtual environment, install dependencies, and start the app:

```bash
uv run streamlit run streamlit_app.py
```

---

### Alternative: Standard `pip` Setup
If you prefer traditional methods, follow these steps:

**1. Set Up Virtual Environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**2. Install Dependencies**
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**3. Launch Streamlit**
```bash
python -m streamlit run streamlit_app.py
```

---

## 📂 Directory Structure

- **`csv_files/`**: Active vocabulary lists waiting to be enriched or processed.
- **`archived_csvs/`**: A record of all previously processed and imported lessons.
- **`audio/`**: Centralized library of word and sentence audio files (Azure/Google TTS).
- **`images/`**: Centralized library of minimalist illustrations for vocabulary concepts.
- **`output/`**: Destination for the final generated `.apkg` Anki deck files.

---

## 💡 Archiving & Media Strategy

This project utilizes a **centralized media library** approach to ensure efficiency and organization:

- **Media Reuse**: Files in the `audio/` and `images/` folders are persistent. The scripts check for existing files before calling APIs, saving time and costs while preventing duplicate assets.
- **Clean Workspace**: By moving completed CSVs to `archived_csvs/`, the `csv_files/` directory only contains what you are currently working on.
- **Deterministic IDs**: Cards are generated with deterministic IDs based on the Chinese word, ensuring that updates to a deck won't create duplicate cards in Anki.
