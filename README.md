# Nestlé Assignment – AI Chatbot with GraphRAG & Vector Search

This project showcases an AI chatbot capable of answering detailed and accurate questions about the **MadeWithNestle.ca** website. It combines **semantic search** (vector search), **graph-based knowledge retrieval (GraphRAG)**, and **LLM-based generation** using **Gemini (Vertex AI)**.

---

## Live Demo

| Service | URL (example) |
|---------|------------------|
| Front-end (React) | <https://nestle-ui-158884498350.us-central1.run.app> |
| Backend API (Python/Flask) | <https://nestle2-158884498350.us-central1.run.app> |
| Source Code | <https://github.com/Ozerg97/nestle-chat-bot> |

---

## Key Features

| Feature | Details |
|---------|---------|
| **Web Scraping** | Recursively scrapes the sitemap XML of MadeWithNestlé to extract product, recipe, article and information pages. |
| **Embeddings** | Generates embeddings using **`text-embedding-004`** (Vertex AI). |
| **Knowledge Graph** | Loads *Product*, *Recipe*, *Brand*, *Category*, *Ingredient* nodes (and their relations) into **Neo4j Aura** for cloud-based graph queries. |
| **Vector Store** | Uses Vector Search for fast top-k semantic retrieval. |
| **Hybrid Retrieval** | A router detects structured queries (“how many”, ” “where to buy,” etc.) and uses either Cypher queries or vector search to build context. |
| **LLM Generation** | Integrates **Gemini 2.0-Flash** (Vertex AI) with a custom prompt to produce clean, structured answers (e.g., bullet points, hyperlinks). |
| **Real-Time UI** | Built with React, supports streaming responses, user/model roles, auto-scrolling, and chat history. |

---

## Tools & Frameworks Used

| Layer | Technology |
|-------|------------|
| **Frontend** | React (Vite) · TypeScript |
| **Backend API** | Python 3.11 · Flask  |
| **LLM** | Google Vertex AI – Gemini Flash |
| **Embeddings** | text-embedding-004 |
| **Graph DB** | Neo4j Aura (free tier) |
| **Vector DB** | Vector Search (cloud) |

---

## How I Solved the **RAG Limitation Problem**

### 1. Structured Query Detection
I implemented a separate module (`structured_query_router.py`) that uses regex and text normalization to detect key phrases like **“how many,” “number of,” and “products”** in user questions.  
- If such keywords are detected, the module queries the **GraphRAG** (Neo4j) using Cypher queries to get exact counts.  
- Example queries:
  - **"How many products under the coffee category?"** triggers a Cypher query counting nodes with the `IN_CATEGORY` relationship.
  - **"How many products by KitKat?"** uses the `BRANDED_AS` relationship to filter products by brand.
  
### 2. Fallback to Vector Search
If no structured query keywords are found, the system falls back to the default **vector search pipeline**, combining semantic retrieval and generative answers via **Gemini (Vertex AI)**.

### 3. Controlled Fusion
Results from GraphRAG (exact counts) are formatted in a consistent style and returned directly to the user **without going through the LLM**.  
For unstructured or conversational questions, I combine semantic snippets and graph facts and send them to Gemini with a carefully crafted prompt.

### 4. Proof of Concept (POC)
I tested this module with a **sample dataset** of Nestlé products and categories, using questions like:

- “How many products under the Aero brand?”
- “How many products are there under the coffee category?”
- “How many products contain sugar?”

The module successfully identified the structured queries and returned precise counts, proving that this GraphRAG extension can effectively handle structured questions—addressing a known limitation of typical RAG pipelines.

---

## Assumptions and Limitations

### Assumptions
- I initially thought I could use **PriceSpider** to get real store links by extracting parameters from HTML elements. However, I didn't have enough data to fully implement this feature.
- For the **Intelligent Product Count** module, I assumed that users would use the correct keywords (e.g., “product,” “products”) for the system to detect structured queries properly. If users misspell words (e.g., “produvt”), the system might not detect the structured query and will default to a general count.
- I also assumed that category and brand names would be written correctly to match my stored data (e.g., "coffee" instead of "cofee").

### Limitations
- The store locator feature calculates distances between the user and the stores using latitude and longitude, but it does not give a perfectly accurate distance. I also limited this feature to only four stores.
- The Amazon purchase link integration currently only returns **general search results** instead of exact product pages due to missing product identifiers or structured links in the scraped data.
- If users don’t use the expected keywords (e.g., “how many products…”), the system defaults to returning the total number of products listed (e.g., “There are 606 products listed.”) instead of a more specific count.

---

## Future Improvements

- **Natural Language Handling in Product Count**  
  Expand the structured query module to handle more natural language variations (e.g., synonyms, typos, plural forms) so that users can ask product count questions in a more flexible way.
- **Fuzzy Matching for Brand and Category Names**  
  Add fuzzy string matching or NLP techniques to detect brand and category names even when they are misspelled (e.g., “cofee” → “coffee”).
- **Multilingual Support**  
  Extend the chatbot to support multiple languages (e.g., French and English) to better serve users in different regions.
- **Enhanced Amazon Links**  
  Implement more precise Amazon product search to link directly to exact product pages instead of general search results.

---

