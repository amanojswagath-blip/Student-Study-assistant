# 🎓 Student Study Assistant

A beautiful AI-powered study assistant with animated interface that processes documents and provides intelligent answers using advanced AI technology.

## ✨ Features

- 🌊 **Beautiful Animated Interface**: Stunning sine wave animations with dark purple theme
- 📄 **Document Processing**: Support for PDF, DOCX, and TXT files
- 🔍 **Intelligent Analysis**: Smart document chunking with keyword extraction
- 🎯 **Semantic Search**: Advanced context retrieval for relevant information
- 🤖 **AI-Powered Chat**: Lightning-fast responses using Groq API
- 📚 **Source Attribution**: Answers linked to original document sections
- 🎨 **Glass-morphism Design**: Modern UI with elegant visual effects

## 🚀 Quick Start

### 1. **Auto Setup (Recommended)**
```bash
setup.bat
```

### 2. **Add Your API Key**
- Edit `.env` file
- Get free API key from: https://console.groq.com/keys

### 3. **Start the Application**
```bash
start_server.bat
```

### 4. **Open in Browser**
Go to: **http://localhost:8000**

**That's it!** 🎉

## 📖 Detailed Instructions

See [HOW_TO_RUN.md](HOW_TO_RUN.md) for complete setup instructions and troubleshooting.

## 🛠️ Tech Stack

- **Frontend**: Beautiful animated HTML/CSS/JavaScript interface
- **Backend**: FastAPI (Python) with async processing  
- **Document Processing**: PyMuPDF, python-docx with intelligent chunking
- **AI**: Groq API (llama-3.1-8b-instant) for fast LLM inference
- **Search**: Semantic similarity with sentence-transformers
- **Storage**: File-based persistence (no database required)

## 🎯 Sample Usage

1. **Upload Documents**: Drag & drop your PDF, DOCX, or TXT files
2. **Ask Questions**: Try these examples:
   - "Summarize the main points"
   - "What are the key findings?"
   - "Explain the methodology"
   - "List important conclusions"

## 🌟 What Makes It Special

- **Zero Database Setup**: Works immediately without complex database installation
- **Beautiful Animations**: Professional sine wave background animations  
- **Intelligent Formatting**: AI responses with proper spacing, headings, and bullet points
- **Fast & Reliable**: Uses Groq API for lightning-fast AI responses
- **Modern UI**: Dark purple theme with glass-morphism effects
- **Smart Search**: Finds relevant context even with partial matches

## 📁 Project Structure

```
📦 student-study-assistant
├── 📄 README.md              # You are here!
├── 📄 HOW_TO_RUN.md          # Detailed running instructions  
├── 📄 setup.bat              # Automatic setup script
├── 📄 start_server.bat       # Start the application
├── 📄 requirements.txt       # Python dependencies
├── 📄 .env.example           # Configuration template
└── 📁 app/                   # Main application
    ├── 📁 static/            # Beautiful animated frontend
    ├── 📁 services/          # AI & document processing
    ├── 📁 api/               # REST API endpoints
    └── main.py               # FastAPI application
```

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests!

## 📜 License

MIT License - see LICENSE file for details.

---

**Made with ❤️ and lots of ☕**