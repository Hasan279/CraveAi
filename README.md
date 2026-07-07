# CraveAI — Intelligent Food Search & RAG Chatbot

🚀 **[Live Demo: craveai.streamlit.app](https://craveai.streamlit.app/)**


<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/ChromaDB-Vector%20DB-4A90D9?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Gemini%202.5%20Flash-AI%20Engine-4285F4?style=for-the-badge&logo=google&logoColor=white"/>
</p>

> A production-ready RAG (Retrieval-Augmented Generation) chatbot that gives intelligent, context-aware food recommendations from a curated database of **300+ dishes** across 30+ world cuisines — powered by **Google Gemini 2.5 Flash** (AI backbone) and ChromaDB (vector store).

---

## Features

- **Conversational RAG Chatbot** — Ask naturally ("spicy dinner under 400 calories") and get curated recommendations grounded in real food data
- **Semantic Vector Search** — ChromaDB embeddings find dishes based on meaning, not just keywords
- **Smart Query Rewriting** — Gemini rewrites vague queries into optimised vector search prompts
- **Side-by-Side Comparison Mode** — Compare two different cravings and get a ranked breakdown
- **300+ Curated Foods** — A rich dataset spanning Italian, Japanese, Indian, Mexican, Ethiopian, Korean, Thai, Peruvian, and many more cuisines
- **Gemini-Inspired UI** — Clean dark interface with animated gradient accents, built on Streamlit

---

## Architecture

```
User Query
    │
    ▼
Query Rewriter (Gemini 2.5 Flash)
    │
    ▼
ChromaDB Vector Search  ◄──── FoodDataset.json (300+ items)
    │
    ▼
Context Builder (top-k results)
    │
    ▼
Gemini 2.5 Flash (RAG generation)
    │
    ▼
Streamed Response → Streamlit UI
```

### Key Modules

| File | Purpose |
|---|---|
| `app.py` | Streamlit front-end & main application entry point |
| `enhanced_rag_chatbot.py` | Core RAG pipeline — embedding, retrieval, and generation |
| `shared_functions.py` | Shared ChromaDB utilities: collection management, similarity search |
| `advanced_search.py` | Advanced filtering: calorie range, cuisine type, dietary flags |
| `interactive_search.py` | Interactive CLI-based search (legacy exploration module) |
| `system_comparison.py` | Benchmarking: RAG vs. keyword search comparison |
| `FoodDataset.json` | 300+ food items with nutritional info, ingredients, and metadata |

---

## Getting Started

### Prerequisites

- Python 3.10+
- A [Google AI Studio](https://aistudio.google.com/) API key (free)

### 1. Clone the repo

```bash
git clone https://github.com/Hasan279/Vector-Database-for-RAG.git
cd "Vector-Database-for-RAG/Interactive Food Search and RAG Chatbot System"
```

### 2. Install dependencies

```bash
pip install streamlit chromadb google-generativeai python-dotenv
```

### 3. Configure your API key

Create a `.env` file in the project folder:

```env
GEMINI_API_KEY=your_api_key_here
```

### 4. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Dataset

`FoodDataset.json` contains **300 unique food items**, each with:

```json
{
  "food_name": "Pad Thai",
  "food_description": "...",
  "food_calories_per_serving": 450,
  "food_nutritional_factors": { "protein": "20g", "carbohydrates": "55g", "fat": "15g" },
  "food_ingredients": ["Rice noodles", "Shrimp", "Peanuts", "Egg", "Bean sprouts"],
  "food_health_benefits": "High protein, good source of complex carbohydrates",
  "cooking_method": "Stir-frying",
  "cuisine_type": "Thai",
  "food_features": {
    "taste": "savory, tangy, slightly sweet",
    "texture": "chewy noodles with crunchy peanuts",
    "appearance": "golden stir-fried noodles",
    "preparation": "stir-fried",
    "serving_type": "hot"
  }
}
```

Cuisines covered include: Italian, Japanese, Indian, Chinese, Mexican, Thai, Korean, Ethiopian, Peruvian, Greek, Turkish, Lebanese, Spanish, Vietnamese, French, American, and more.

---

## Example Queries

| Query | What it demonstrates |
|---|---|
| "Spicy dinner under 400 calories" | Calorie-aware retrieval |
| "Healthy Italian pasta" | Cuisine-specific filtering |
| "High-protein breakfast" | Nutritional goal matching |
| "Something warm and comforting for a cold night" | Emotion/context-based search |
| "Compare sushi vs tacos" | Comparison mode |

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit (Gemini-inspired dark theme) |
| Vector DB | ChromaDB (local, persistent) |
| LLM | Google Gemini 2.5 Flash |
| Embeddings | ChromaDB default (sentence-transformers) |
| Dataset | Custom curated JSON (300+ entries) |
| Language | Python 3.10+ |

---

## Project Structure

```
Vector-Database-for-RAG/
├── Interactive Food Search and RAG Chatbot System/
│   ├── app.py                    # Main Streamlit app
│   ├── enhanced_rag_chatbot.py   # RAG pipeline core
│   ├── shared_functions.py       # ChromaDB utilities
│   ├── advanced_search.py        # Advanced filtering
│   ├── interactive_search.py     # CLI search module
│   ├── system_comparison.py      # RAG vs keyword benchmark
│   └── FoodDataset.json          # 300+ food items dataset
├── Course_content/               # Coursera course notebooks
├── .gitignore
└── README.md
```

---

## Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

---

## License

[MIT](https://choosealicense.com/licenses/mit/)
