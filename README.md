# Django Backend CV

This repository contains a Django backend application designed to serve as a comprehensive AI RAG system, featuring a chatbot for interactive information retrieval and a messaging system. It leverages modern AI tools for natural language processing and integrates with a PostgreSQL database.




## Features

### Interactive Chatbot

The application includes an AI-powered chatbot that can answer questions about the CV content. It utilizes `langgraph`, `langchain-groq`, `langchain-google-genai`, and `langchain_mistralai` for advanced natural language processing and conversational AI capabilities. The chatbot is designed to provide real-time, context-aware responses based on the information retrieved from vector store.

### Messaging System

A messaging system is integrated into the backend, allowing for communication functionalities. This system is handled by the `sendmessages` Django app.




## Technologies Used

This project is built using the following key technologies:

## Dependencies

### Core Framework & Database
- **Django 5.2.3**: A high-level Python web framework that encourages rapid development and clean, pragmatic design.
- **PostgreSQL**: A powerful, open-source object-relational database system used for data storage.
- **psycopg2-binary**: A PostgreSQL adapter for Python.
- **python-dotenv**: For loading environment variables from a `.env` file.

### LangChain Ecosystem
- **langgraph**: For building robust and stateful multi-actor applications with LLMs.
- **langsmith**: For debugging, testing, evaluating, and monitoring LLM applications.
- **langchain-groq**: Integration with Groq for fast LLM inference.
- **langchain-google-genai**: Integration with Google's Generative AI models.
- **langchain_mistralai**: Integration with Mistral AI models.

### Vector Search & AI
- **pgvector 0.4.1**: PostgreSQL extension for vector similarity search, enabling storage and querying of vector embeddings.
- **cohere 5.16.1**: SDK for Cohere's NLP models, supporting embeddings, reranking, and text generation.
- **pinecone[asyncio] 7.3.0**: A managed vector database client with async support for scalable similarity search.

### Document & Image Processing
- **Pillow 11.3.0**: A Python imaging library for opening, manipulating, and saving image files.
- **pdfplumber 0.11.7**: For extracting text, tables, and metadata from PDF files with fine-grained control.
- **pymupdf 1.26.3**: A high-performance PDF and document processing library (also known as fitz).

### Authentication & Security
- **argon2-cffi 25.1.0**: A secure password hashing library implementing the Argon2 algorithm.
- **pyjwt 2.10.1**: For encoding and decoding JSON Web Tokens (JWT) in Python.
- **django-ratelimit 4.1.0**: A Django decorator/middleware for rate limiting views to prevent abuse.

### Backend & Database Services
- **supabase 2.24.0**: Python client for Supabase, providing access to its database, auth, storage, and realtime features.

### Utilities
- **ipython**: An interactive computing environment.
- **colorama 0.4.6**: For adding colored terminal text.




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
    DB_HOST=your_db_host
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_PORT=your_db_port

    SUPABASE_URL=
    SUPABASE_KEY=
    SUPABASE_REDIRECT_URL=

    ```

5.  **Run database migrations:**

    Navigate into the `cv-django-project` directory and apply the database migrations:

    ```bash
    cd cv-django-project
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
├── chatbot/                 # Django app for the AI chatbot
│   ├── services/            # Contains LangChain/LangGraph related services
│   ├── views.py             # Chatbot API endpoints
│   └── ...
├── cvendpoints/             # Main Django project configuration
│   ├── settings.py          # Project settings
│   ├── urls.py              # Main URL routing
│   └── ...
├── sendmessages/            # Django app for messaging functionalities
│   └── ...
├── usermanagment/           # Django app for managing uset authentication 
│   └── ...
├── embed/                   # Django app for embeding text images and pdfs into supabase or pinecone 
│   └── ...
├── manage.py                # Django's command-line utility
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment variables file
└── README.md                # This README file
```


