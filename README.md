# Django Backend CV & AI RAG System

This repository contains a full-stack application featuring a **Django** backend and a **Vue.js** frontend. It is designed to serve as a comprehensive AI RAG (Retrieval-Augmented Generation) system, featuring a chatbot for interactive information retrieval and a messaging system. It leverages modern AI tools for natural language processing and integrates with a PostgreSQL database.

## Features

### Interactive Chatbot

The application includes an AI-powered chatbot built with `langgraph`, `langchain-groq`, `langchain-google-genai`, and `langchain_mistralai`, enabling advanced natural language processing and conversational AI capabilities. The chatbot provides real-time, context-aware responses based on information retrieved from a vector store.

The application also implements JWT-based authentication, vector embedding pipelines for both Supabase and Pinecone, and semantic, lexical, and hybrid search using the Reciprocal Rank Fusion (RRF) reranking algorithm. Additionally, it supports nearest-neighbor retrieval to enrich search results following the primary retrieval stage.

### Messaging System

A messaging system is integrated into the backend, allowing for communication functionalities. This system is handled by the `contact` Django app.

## Technologies Used

This project is built using the following key technologies:

### Backend

- **Django 5.2.3**: A high-level Python web framework that encourages rapid development and clean, pragmatic design.

- **PostgreSQL**: A powerful, open-source object-relational database system used for data storage.

- **pgvector 0.4.1**: PostgreSQL extension for vector similarity search, enabling storage and querying of vector embeddings.

- **LangChain Ecosystem**: Includes `langgraph`, `langsmith`, and integrations for Groq, Google Gemini, and Mistral AI.

- **Vector Search**: Managed services via **Pinecone** and **Supabase**.

### Frontend

- **Vue.js 3**: Modern JavaScript framework using the Composition API for a reactive UI.

- **TypeScript**: Provides static typing for improved developer experience and code reliability.

- **Vite**: Next-generation frontend build tool for fast development and optimized production builds.

- **Pinia**: Intuitive and flexible state management library for Vue.

- **Vue Router**: Official router for Vue.js to handle single-page application navigation.

---

## Dependencies

### Core Framework & Database

- **Django 5.2.3**

- **PostgreSQL**

- **psycopg2-binary 2.9.10**

- **python-dotenv 1.1.0**

### LangChain Ecosystem

- **langgraph 0.5.2**

- **langsmith 0.4.5**

- **langchain-groq 0.3.6**

- **langchain-google-genai 2.1.7**

- **langchain_mistralai 0.2.11**

### Vector Search & AI

- **pgvector 0.4.1**

- **cohere 5.16.1**

- **pinecone 9.1.0**

### Document & Image Processing

- **Pillow 11.3.0**

- **pdfplumber 0.11.7**

- **pymupdf 1.26.3**

### Authentication & Security

- **argon2-cffi 25.1.0**

- **pyjwt 2.10.1**

- **django-ratelimit 4.1.0**

- **cryptography 45.0.5**

### Backend & Database Services

- **supabase 2.24.0**

### Utilities

- **ipython 9.4.0**

- **colorama 0.4.6**

---

## Setup and Installation

To get this project up and running on your local machine, follow these steps:

### Backend Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Sveto-Ivanovic/django-be-cv.git
   cd django-be-cv/django-be
   ```

1. **Create a virtual environment and activate it:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

1. **Set up environment variables:**Create a `.env` file in the `django-be/` directory. Refer to `.env.example` for required variables.

1. **Run database migrations:**

   ```bash
   python manage.py migrate
   ```

1. **Start the Django development server:**

   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Navigate to the frontend directory:**

   ```bash
   cd ../vue-frontend
   ```

1. **Install dependencies:**

   ```bash
   pnpm install
   ```

1. **Start the development server:**

   ```bash
   pnpm dev
   ```

---

## Project Structure

### Root Directory

```
django-be-cv/
├── django-be/        # Django backend application
├── vue-frontend/     # Vue.js frontend application
├── .gitignore
└── README.md
```

vue-frontend/
├── src/
│   ├── components/       # Reusable UI components (e.g., ChatWindow.vue, LoadingSpinner.vue)
│   ├── views/            # Page-level components (e.g., Home.vue, Dashboard.vue, Chatbot.vue)
│   ├── services/         # API communication logic (e.g., auth.service.ts, chat.service.ts)
│   ├── stores/           # Pinia state management (e.g., user.ts, chatbot.ts)
│   ├── router/           # Vue Router configuration and navigation guards
│   ├── assets/           # Static assets like images, styles, and global icons
│   ├── App.vue           # Root component
│   └── main.ts           # Application entry point
├── public/               # Static public files
├── vite.config.ts        # Vite configuration
└── package.json          # Project dependencies and scripts



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
│   │   ├── evaluate/        # Django app for benchmark evaluation with vectorstore
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

### Frontend Structure (`vue-frontend/src/` )

The frontend is built with a modular architecture:

- **`components/`**: Reusable UI elements (e.g., `ChatWindow.vue`, `LoadingSpinner.vue`).

- **`views/`**: Page components representing different routes (e.g., `Home.vue`, `Dashboard.vue`, `Chatbot.vue`).

- **`services/`**: Modules for API calls and external integrations (e.g., `auth.service.ts`, `chat.service.ts`).

- **`stores/`**: Pinia state management for global application state.

- **`router/`**: Navigation configuration and route guards.

- **`assets/`**: Static files, global styles, and images.

### Backend Structure (`django-be/`)

- **`apps/`**: Modular Django applications containing core logic.

- **`config/`**: Global project settings and URL routing.

- **`Dockerfile`**: Container configuration for the backend service.

---

## License

This project is licensed under the MIT License.