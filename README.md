# Python Chatbot API

A complete, production-ready chatbot API built with FastAPI, MongoDB, and Google Gemini AI. Features a clean architecture with reusable utilities, proper error handling, and comprehensive logging.

## 🏗️ Project Structure

```
Python_Chatbot/
├── app/
│   ├── __init__.py
│   ├── config/              # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py     # Application settings
│   ├── models/              # Pydantic data models
│   │   ├── __init__.py
│   │   └── chat.py          # Chat-related models
│   ├── services/            # Business logic services
│   │   ├── __init__.py
│   │   ├── database.py     # MongoDB service
│   │   ├── gemini.py        # Gemini AI service
│   │   └── chat.py          # Chat orchestration service
│   ├── routes/              # API route handlers
│   │   ├── __init__.py
│   │   ├── chat.py          # Chat endpoints
│   │   ├── health.py        # Health check endpoints
│   │   └── ai.py            # AI info endpoints
│   ├── middleware/          # Custom middleware
│   │   ├── __init__.py
│   │   ├── error_handler.py # Error handling
│   │   └── logging.py       # Request logging
│   └── utils/               # Reusable utilities
│       ├── __init__.py
│       ├── logger.py        # Logging utilities
│       ├── response.py      # Response formatting
│       ├── validators.py    # Input validation
│       └── helpers.py       # Helper functions
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

## 🚀 Features

- **Clean Architecture**: Well-organized codebase with separation of concerns
- **Reusable Utilities**: Common functions for logging, validation, and responses
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **Logging**: Structured logging for debugging and monitoring
- **Type Safety**: Full type hints throughout the codebase
- **API Documentation**: Auto-generated Swagger/ReDoc documentation
- **MongoDB Integration**: Async MongoDB operations with Motor
- **Gemini AI**: Google Gemini Pro integration for chat responses
- **Conversation Management**: Store and retrieve chat history
- **CORS Support**: Configurable CORS for frontend integration

## 📦 Installation

1. **Install dependencies:**
```bash
python -m pip install -r requirements.txt
```

2. **Configure environment variables:**
   - Copy `.env` file and update with your credentials
   - Set `MONGO_URI` or MongoDB connection details
   - Set `GEMINI_API_KEY`

3. **Run the application:**
```bash
python -m uvicorn main:app --reload
```

## 🔧 Configuration

Edit `.env` file with your settings:

```env
# MongoDB Configuration
MONGO_URI=mongodb+srv://user:password@host/database

# Gemini API
GEMINI_API_KEY=your_api_key_here

# Application Settings
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

## 🖥️ Web Interface

A beautiful, modern web UI is included! Simply start the server and navigate to `http://localhost:8000` in your browser.

### UI Features:
- ✨ Modern dark theme interface
- 💬 Real-time chat with AI
- 📝 Conversation history management
- 📱 Fully responsive (mobile-friendly)
- ⚙️ Configurable settings
- 🎯 Quick suggestion buttons

The UI is automatically served when you start the server. See `UI_GUIDE.md` for detailed UI documentation.

## 📡 API Endpoints

### Chat Endpoints

- `POST /api/chat` - Send a message and get AI response
- `GET /api/chat/history/{conversation_id}` - Get conversation history
- `GET /api/chat/conversations` - List recent conversations
- `DELETE /api/chat/conversations/{conversation_id}` - Delete a conversation

### Health & Info

- `GET /api/health` - Health check
- `GET /api/health/db` - Database information
- `GET /api/ai/info` - AI model information

### Documentation

- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## 📝 Usage Examples

### Send a Chat Message

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "conversation_id": "conv_abc123"
  }'
```

### Get Conversation History

```bash
curl "http://localhost:8000/api/chat/history/conv_abc123?limit=50"
```

## 🛠️ Development

### Project Architecture

- **Config**: Centralized configuration using Pydantic Settings
- **Models**: Data models using Pydantic for validation
- **Services**: Business logic separated into service classes
- **Routes**: API endpoints organized by feature
- **Middleware**: Cross-cutting concerns (logging, error handling)
- **Utils**: Reusable utility functions

### Adding New Features

1. **New Model**: Add to `app/models/`
2. **New Service**: Add to `app/services/`
3. **New Route**: Add to `app/routes/` and include in `app/routes/__init__.py`
4. **New Utility**: Add to `app/utils/`

## 📚 Key Utilities

### Logger
```python
from app.utils.logger import get_logger
logger = get_logger(__name__)
logger.info("Message")
```

### Response Formatting
```python
from app.utils.response import success_response, error_response
return success_response(data={...}, message="Success")
```

### Validation
```python
from app.utils.validators import validate_message
is_valid, error = validate_message(message)
```

## 🔒 Security Notes

- Never commit `.env` file to version control
- Use environment variables for sensitive data
- Configure CORS origins in production
- Validate all user inputs
- Implement rate limiting for production use

## 📄 License

This project is open source and available for use.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

