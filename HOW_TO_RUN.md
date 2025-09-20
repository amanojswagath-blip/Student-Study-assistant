# 🚀 How to Run Student Study Assistant

## 📋 Prerequisites
- **Python 3.8+** installed on your system
- **Internet connection** (for AI features)
- **GROQ API Key** (free from [console.groq.com](https://console.groq.com/keys))

## ⚡ Quick Start (Windows)

### Step 1: Setup Environment
Run the setup script to install all dependencies:
```bash
setup.bat
```
This will:
- ✅ Create a Python virtual environment
- ✅ Install all required packages
- ✅ Create necessary directories
- ✅ Copy `.env.example` to `.env`

### Step 2: Configure API Key
1. Open `.env` file in any text editor
2. Replace `your_groq_api_key_here` with your actual GROQ API key
3. Save the file

**Get your free GROQ API key:**
- Visit: https://console.groq.com/keys
- Sign up (free)
- Create new API key
- Copy and paste into `.env` file

### Step 3: Start the Server
Run the server using either:
```bash
start_server.bat
```
**OR**
```bash
start_server.ps1
```

### Step 4: Open in Browser
- The application will start at: **http://localhost:8000**
- Open your web browser and go to that URL

## 🎯 Manual Installation (Alternative)

If the automatic setup doesn't work:

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows Command Prompt:
venv\Scripts\activate.bat
# Windows PowerShell:
venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
copy .env.example .env
# Edit .env and add your GROQ_API_KEY

# 5. Start server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🌟 Features to Test

### 1. **Beautiful Animations**
- Sine wave background animations
- Dark purple elegant theme
- Glass-morphism effects

### 2. **Document Upload**
- Drag & drop PDF, DOCX, or TXT files
- Automatic processing and chunking
- Support for multiple documents

### 3. **AI Chat**
- Ask questions about your documents
- Get intelligent summaries
- Context-aware responses
- Source attribution

### 4. **Sample Questions to Try:**
- "Summarize the main points"
- "What are the key findings?"
- "Explain the methodology"
- "List the important conclusions"

## 🛠️ Troubleshooting

### Common Issues:

**"Python is not installed"**
- Download Python from [python.org](https://python.org)
- Make sure to check "Add Python to PATH" during installation

**"Virtual environment not found"**
- Run `setup.bat` first before `start_server.bat`

**"AI responses not working"**
- Check your GROQ_API_KEY in `.env` file
- Ensure you have internet connection
- Verify API key is valid at console.groq.com

**"Port 8000 already in use"**
- Close any existing servers
- Or edit the port in start_server files (change 8000 to 3000, etc.)

**"Document upload fails"**
- Ensure `uploads` directory exists
- Check file permissions
- Try smaller files first

## 🎨 What You'll See

- 🌊 **Animated sine waves** in the background
- 💜 **Dark purple theme** with glass effects
- 📄 **Drag & drop file upload** with progress indicators
- 💬 **AI chat interface** with beautiful formatting
- ⚡ **Real-time responses** with source attribution

## 🔄 Stopping the Server

Press `Ctrl+C` in the terminal window to stop the server.

---

**Enjoy your beautiful AI-powered Student Study Assistant!** 🎉✨