# Nestlé Assignment – AI Chatbot with GraphRAG & Vector Search

This project aims to build a smart chatbot capable of answering questions about **madewithnestlé website**, using a hybrid approach combining **vector search**, **graph-based knowledge retrieval (GraphRAG)**, and **LLM-based generation** via **Gemini (Vertex AI)**.

## Overview

The system combines:
- **Semantic search** using vector embeddings
- **Graph reasoning** using Neo4j Aura 
- **LLM-based response generation** using Google's Gemini model

This allows the chatbot to answer complex queries like:
> “Give me a recipe with Smarties that contains no nuts.”

## Features

- Web scraping of product and recipe pages from madewithnestle.ca via the sitemap
- Graph construction linking products, brands, ingredients, and categories
- Embedding generation with `text-embedding-gecko` (Vertex AI)
- Graph database integration using Neo4j
- Hybrid retrieval with GraphRAG + vector database
- Response generation with Gemini (Vertex AI)

## Installation

- git clone https://github.com/Ozerg97/nestle_ai_bot_ozer.git
- install libraries from requirement.txt
- run the app.py file

