# Django Backend CV

This repository contains a Django backend application designed to serve as a comprehensive AI RAG system, featuring a chatbot for interactive information retrieval and a messaging system. It leverages modern AI tools for natural language processing and integrates with a PostgreSQL database.




## Features

### Interactive Chatbot

The application includes an AI-powered chatbot built with `langgraph`, `langchain-groq`, `langchain-google-genai`, and `langchain_mistralai`, enabling advanced natural language processing and conversational AI capabilities. The chatbot provides real-time, context-aware responses based on information retrieved from a vector store.

The application also implements JWT-based authentication, vector embedding pipelines for both Supabase and Pinecone, and semantic, lexical, and hybrid search using the Reciprocal Rank Fusion (RRF) reranking algorithm. Additionally, it supports nearest-neighbor retrieval to enrich search results following the primary retrieval stage.

### Messaging System

A messaging system is integrated into the backend, allowing for communication functionalities. This system is handled by the `contact` Django app.




## Technologies Used

This project is built using the following key technologies:

## Dependencies
## Core Framework & Database

- **Django 5.2.3**: A high-level Python web framework that encourages rapid development and clean, pragmatic design.
- **PostgreSQL**: A powerful, open-source object-relational database system used for data storage.
- **psycopg2-binary 2.9.10**: A PostgreSQL adapter for Python.
- **python-dotenv 1.1.0**: Loads environment variables from a `.env` file.

## LangChain Ecosystem

- **langgraph 0.5.2**: Framework for building robust, stateful, multi-agent applications powered by LLMs.
- **langsmith 0.4.5**: Platform for debugging, testing, evaluating, and monitoring LLM applications.
- **langchain-groq 0.3.6**: Integration with Groq for high-performance LLM inference.
- **langchain-google-genai 2.1.7**: Integration with Google's Generative AI models.
- **langchain_mistralai 0.2.11**: Integration with Mistral AI models.

## Vector Search & AI

- **pgvector 0.4.1**: PostgreSQL extension for vector similarity search, enabling storage and querying of vector embeddings.
- **cohere 5.16.1**: SDK for Cohere's NLP models, supporting embeddings, reranking, and text generation.
- **pinecone 9.1.0**: Managed vector database client for scalable similarity search and vector storage.

## Document & Image Processing

- **Pillow 11.3.0**: Python imaging library for opening, manipulating, and saving image files.
- **pdfplumber 0.11.7**: Extracts text, tables, and metadata from PDF files with fine-grained control.
- **pymupdf 1.26.3**: High-performance PDF and document processing library (also known as `fitz`).

## Authentication & Security

- **argon2-cffi 25.1.0**: Secure password hashing library implementing the Argon2 algorithm.
- **pyjwt 2.10.1**: Library for encoding and decoding JSON Web Tokens (JWT).
- **django-ratelimit 4.1.0**: Django middleware/decorator for rate limiting and abuse prevention.
- **cryptography 45.0.5**: Provides cryptographic recipes and primitives for secure application development.

## Backend & Database Services

- **supabase 2.24.0**: Python client for Supabase, providing access to database, authentication, storage, and realtime features.

## Utilities

- **ipython 9.4.0**: Interactive Python computing environment.
- **colorama 0.4.6**: Cross-platform colored terminal text support.



## Setup and Installation

To get this project up and running on your local machine, follow these steps:

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Sveto-Ivanovic/django-be-cv.git
    cd django-be-cv
    ```

2.  **Create a virtual environment and activate it:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**

    Create a `.env` file in the root directory of the `django-be-cv` project (the same directory as `requirements.txt`) and add your database credentials and any other necessary environment variables. Refer to `.env.example` for required variables.

    ```
    # Database configuration
    DB_HOST=
    DB_NAME=
    DB_USER=
    DB_PASSWORD=
    DB_PORT=
    
    # Supabase configuration
    SUPABASE_URL=
    SUPABASE_KEY=
    SUPABASE_REDIRECT_URL=
    
    # Secret keys
    SECRET_AES_KEY=
    SECRET_DJANGO_KEY=

    ```

5.  **Run database migrations:**

    Navigate into the `cv-django-project` directory and apply the database migrations:

    ```bash
    cd django-be-cv
    python manage.py migrate
    ```

6.  **Start the Django development server:**

    ```bash
    python manage.py runserver
    ```

    The application will be accessible at `http://127.0.0.1:8000/`.




## Project Structure

```
django-be-cv/
├── django-be/               # Main Django project directory
│   ├── apps/                # Directory for Django applications
│   │   ├── chatbot/         # Django app for the AI chatbot
│   │   │   ├── services/    # Contains LangChain/LangGraph related services
│   │   │   ├── views.py     # Chatbot API endpoints
│   │   │   └── ...
│   │   ├── contact/         # Django app for contact functionalities
│   │   ├── core/            # Django app for core functionalities
│   │   ├── embed/           # Django app for embedding text, images, and pdfs into Supabase or Pinecone
│   │   ├── usermanagement/  # Django app for managing user authentication
│   │   ├── vector_search/   # Django app for vector search functionalities
│   │   └── __init__.py      # Python package initialization file
│   ├── config/              # Main Django project configuration
│   │   ├── __init__.py      # Python package initialization file
│   │   ├── asgi.py          # ASGI configuration for Django
│   │   ├── settings.py      # Project settings
│   │   ├── urls.py          # Main URL routing
│   │   └── wsgi.py          # WSGI configuration for Django
│   └── manage.py            # Django's command-line utility
├── .env.example             # Example environment variables file
├── .gitignore               # Specifies intentionally untracked files to ignore
├── README.md                # Project README file
└── requirements.txt         # Python dependencies
```


