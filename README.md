# BundleWWW

> Generate complete, AI-powered static websites about any topic in minutes

![BundleWWW Architecture](BundleWWW%20Image.jpg)

BundleWWW is a powerful web application that uses AI to create fully functional, self-contained static websites on any topic you choose. From initial structure to final content, everything is generated automatically.

## ✨ Features

- **🤖 AI-Powered Generation**: Leverages multiple LLM providers through OpenRouter
- **📦 Complete Websites**: Generates structure, content, navigation, and styling
- **📱 Static Output**: Self-contained HTML/CSS websites that work offline
- **📝 Rich Content**: Supports prose, timelines, tables, callouts, statistics, and code blocks
- **🎨 Optional AI Images**: Generate hero images for each chapter (requires FAL API key)
- **⚡ Multiple AI Models**: Choose from 9 different LLM models based on your needs
- **📊 Real-time Progress**: Watch your website being built with streaming updates
- **💾 Downloadable**: Export complete websites as ZIP files
- **🔄 Re-renderable**: Update styling without regenerating content

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **OpenRouter API Key** (required) - [Get one here](https://openrouter.ai/keys)
- **FAL API Key** (optional, for image generation) - [Get one here](https://fal.ai)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/bundlewww.git
   cd bundlewww
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   FAL_KEY=your_fal_api_key_here  # Optional
   ```

3. **Run the application**

   **Windows:**
   ```bash
   start.bat
   ```

   **macOS/Linux:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

4. **Open your browser**

   Navigate to: `http://localhost:3000`

That's it! The startup script handles all dependencies automatically.

## 📖 Usage

### Creating a Website

1. **Create New Project**
   - Click "Create New Project"
   - Enter your topic (e.g., "History of Coffee", "Quantum Computing")
   - Configure settings:
     - **Depth**: Overview, Deep Dive, or Comprehensive
     - **Tone**: Introductory, Professional, Academic, or Casual
     - **AI Model**: Choose from 9 available models
     - **Generate Images**: Optionally enable AI image generation

2. **Review Blueprint**
   - AI generates a structured outline with chapters and sections
   - Review and approve the structure
   - Regenerate if needed

3. **Generate Content**
   - AI creates all content for each chapter
   - Watch real-time progress as each section is completed
   - AI images are generated in parallel (if enabled)

4. **Render Website**
   - Final HTML pages are created
   - Navigation, styling, and assets are assembled

5. **Preview & Download**
   - Preview the website in your browser
   - Download as a ZIP file
   - Re-render anytime to apply style updates

### Available AI Models

BundleWWW supports the following models through OpenRouter:

| Model | Input Cost | Output Cost | Speed |
|-------|-----------|-------------|--------|
| **xAI: Grok Code Fast** | $0.20/1M | $1.50/1M | ⚡ Fast |
| **Google: Gemini 2.5 Flash** | $0.30/1M | $2.50/1M | ⚡ Fast |
| **Anthropic: Claude Sonnet 4.5** | $3.00/1M | $15.00/1M | 🎯 High Quality |
| **Xiaomi: MiMo-V2-Flash** | FREE | FREE | ⚡ Fast |
| **DeepSeek: DeepSeek V3.2** | $0.25/1M | $0.38/1M | 💰 Cheap |
| **Google: Gemini 3 Flash Preview** | $0.50/1M | $3.00/1M | ⚡ Fast |
| **xAI: Grok 4.1 Fast** | $0.20/1M | $0.50/1M | ⚡⚡ Very Fast |
| **Anthropic: Claude Opus 4.5** | $5.00/1M | $25.00/1M | 🎯🎯 Best Quality |
| **Google: Gemini 2.5 Flash Lite** | $0.10/1M | $0.40/1M | 💰 Very Cheap |

Choose based on your speed, cost, and quality preferences.

## 📁 Project Structure

```
bundlewww/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── agents/       # AI agents (Architect, Constructor, Renderer, Illustrator)
│   │   ├── models/       # Data models (Pydantic)
│   │   ├── services/     # External API integrations (OpenRouter, FAL)
│   │   └── main.py       # FastAPI application
├── frontend/             # React frontend
│   └── src/
│       ├── components/   # UI components
│       ├── App.jsx       # Main application
│       └── index.css     # Global styles
├── data/                 # Generated project data (gitignored)
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── start.bat             # Windows startup script
├── start.sh              # Unix startup script
├── pyproject.toml        # Python dependencies
└── README.md             # This file
```

## 🏗️ Architecture

### Four-Agent Pipeline

1. **Architect Agent**: Creates structural blueprints with chapters and sections
2. **Constructor Agent**: Generates rich content for each section
3. **Illustrator Agent**: Generates AI images for chapters (optional)
4. **Renderer Agent**: Assembles static HTML/CSS websites

### Technology Stack

**Backend:**
- FastAPI (modern Python web framework)
- Pydantic (data validation)
- OpenRouter API (multi-LLM access)
- FAL API (image generation)
- Server-Sent Events (real-time streaming)
- JSON flat-file storage

**Frontend:**
- React 19 (latest features)
- Vite (fast build tool)
- Modern CSS with design system
- Real-time SSE integration

### Data Flow

```
User Input → Blueprint → Approval → Content Schema → Static Website
                                    ↓
                              (Optional) AI Images
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required - Get from https://openrouter.ai/keys
OPENROUTER_API_KEY=your_key_here

# Optional - Enables AI image generation
# Get from https://fal.ai
FAL_KEY=your_key_here
```

### Customization

- **Models**: Models are defined in `Available Models and Price.csv`
- **Styling**: Customize website appearance in `backend/app/agents/renderer.py`
- **Content Types**: Add new content blocks in `backend/app/models/schema.py`
- **Agents**: Modify generation logic in `backend/app/agents/`

## 🔧 Troubleshooting

### Port Already in Use

If ports 3000 or 8000 are in use:
- Close other applications using these ports
- Or modify the ports in `start.bat`/`start.sh`

### API Key Issues

- Verify your OpenRouter API key is valid at [OpenRouter Dashboard](https://openrouter.ai/keys)
- Check your account has available credits
- FAL_KEY is optional - leave empty to disable image generation

### Windows Permission Errors

When deleting projects:
- Close the preview window before deletion
- Wait a moment for file locks to release
- Try again

### Generation Fails

- Check API key is correctly set in `.env`
- Verify you have internet connection
- Check OpenRouter service status
- Try a different model

## 🛠️ Development

### Manual Setup

If you prefer to run services separately:

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Building for Production

```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
pip install build
python -m build
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/bundlewww/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/bundlewww/discussions)

## 🙏 Acknowledgments

- Powered by [OpenRouter](https://openrouter.ai) for multi-LLM access
- Image generation via [FAL.ai](https://fal.ai)
- Built with [FastAPI](https://fastapi.tiangolo.com) and [React](https://react.dev)
- Vibe coded using [Claude Code](https://claude.com/code) and [Cline](https://github.com/cline/cline)

---

**Made with ❤️ for content creators and knowledge sharers**
