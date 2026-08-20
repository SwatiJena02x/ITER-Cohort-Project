# 🧠 DSA Coach AI — Intelligent DSA Interview Feedback Generator

An AI-powered DSA Interview Coach that analyzes coding solutions, evaluates problem-solving approaches, identifies mistakes, and provides progressive hints without immediately revealing the complete solution.

## 🚀 Live Demo

**Application:** https://dsa-coach-frontend-5raf.onrender.com/

**Backend API Documentation:** https://dsa-coach-backend.onrender.com/docs

## ✨ Features

- 🤖 AI-powered DSA solution analysis
- 🧠 Correctness and algorithmic reasoning feedback
- ⏱️ Time and space complexity analysis
- ⚠️ Identification of potential issues
- 💡 Optimization suggestions
- 📈 Improvement recommendations
- 💭 Progressive AI hints
- 🔌 FastAPI REST backend
- ⚛️ React + Vite frontend
- 🎨 Tailwind CSS interface
- 🐳 Docker support
- ☁️ Render deployment

## 🏗️ System Architecture

```text
User
  │
  ▼
React + Vite Frontend
  │
  │ REST API
  ▼
FastAPI Backend
  │
  ▼
AI Workflow / LangGraph
  │
  ▼
Groq LLM
  │
  ▼
AI Feedback
```

## 🛠️ Tech Stack

### Frontend
- React.js
- Vite
- JavaScript
- Axios
- React Router
- Tailwind CSS
- Nginx

### Backend
- Python
- FastAPI
- Pydantic
- Uvicorn
- REST API

### AI
- LangGraph
- AI Agents
- LLM-based reasoning
- Progressive hint generation
- Groq API

### Deployment
- GitHub
- Docker
- Render

## 📂 Project Structure

```text
DSA-Coach-Feedback-Generator/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   └── ...
│
├── frontend/
│   └── frontend/
│       ├── public/
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── services/
│       │   │   └── api.js
│       │   ├── App.jsx
│       │   ├── main.jsx
│       │   └── index.css
│       ├── package.json
│       ├── vite.config.js
│       ├── tailwind.config.js
│       ├── Dockerfile
│       └── nginx.conf
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

## 🔌 API Endpoints

### Health Check

```http
GET /health
```

Example:

```bash
curl https://dsa-coach-backend.onrender.com/health
```

### Analyze DSA Solution

```http
POST /feedback/analyze
```

Example request:

```json
{
  "problem": "Two Sum",
  "language": "Python",
  "code": "def twoSum(nums, target): ...",
  "approach": "Using a hashmap to store previously visited values."
}
```

### Generate Hint

```http
POST /feedback/hint
```

Example request:

```json
{
  "problem": "Two Sum",
  "language": "Python",
  "code": "def twoSum(nums, target): ...",
  "approach": "Using nested loops.",
  "hint_level": 1
}
```

## 💡 Progressive Hint Levels

### Level 1 — Conceptual
Provides a small conceptual direction.

### Level 2 — Algorithm
Suggests an appropriate data structure or algorithm.

### Level 3 — Detailed Guidance
Provides detailed implementation direction while encouraging independent problem solving.

## 🧪 Example

### Problem

```text
Given an array of integers nums and an integer target,
return the indices of the two numbers that add up to target.
```

### Submitted Code

```python
def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
```

### Approach

```text
Use two nested loops and check every pair.
```

Possible AI feedback:

```text
Time Complexity:
O(n²)

Space Complexity:
O(1)

Optimization:
Use a hashmap to reduce lookup time.
```

## 💻 Local Development

### Clone Repository

```bash
git clone https://github.com/TPS1234795/DSA-Coach-Feedback-Generator.git
cd DSA-Coach-Feedback-Generator
```

### Backend

```bash
cd backend
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
uvicorn main:app --reload --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend/frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## 🔐 Environment Variables

Create `.env` inside the backend directory:

```env
GROQ_API_KEY=your_groq_api_key
MODEL=openai/gpt-oss-20b
```

Never commit real API keys to GitHub.

## 🔗 API Configuration

The frontend API wrapper uses:

```javascript
const BASE_URL =
  import.meta.env.VITE_API_BASE_URL || '/api'
```

Local development:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Deployed frontend-to-backend configuration:

```env
VITE_API_BASE_URL=https://dsa-coach-backend.onrender.com
```

## 🐳 Docker

### Backend

```bash
docker build -t dsa-coach-backend ./backend
docker run -p 8000:8000 dsa-coach-backend
```

### Frontend

```bash
docker build -t dsa-coach-frontend ./frontend/frontend
docker run -p 10000:10000 dsa-coach-frontend
```

### Docker Compose

```bash
docker compose up --build
```

Stop:

```bash
docker compose down
```

## ☁️ Deployment

```text
GitHub
   ↓
Docker
   ↓
Render
   ↓
Frontend + Backend
```

The frontend and backend are deployed on Render.

The public application is:

https://dsa-coach-frontend-5raf.onrender.com/

## 🔒 Security

Do not expose API keys in:
- GitHub
- Source code
- Committed `.env` files
- README files
- Frontend JavaScript bundles

Store secrets as environment variables.

## 📊 API Flow

```text
User
 │
 ▼
React Frontend
 │
 ▼
Axios Request
 │
 ▼
FastAPI
 │
 ▼
Request Validation
 │
 ▼
AI / LangGraph Workflow
 │
 ▼
Groq LLM
 │
 ▼
AI Feedback
 │
 ▼
FastAPI Response
 │
 ▼
React UI
```

## 🎯 Project Goals

- Improve DSA problem-solving skills
- Encourage independent thinking
- Provide interview-style feedback
- Explain algorithmic trade-offs
- Identify complexity issues
- Provide progressive hints
- Help users prepare for technical interviews

## 🔮 Future Improvements

- [ ] User authentication
- [ ] User progress dashboard
- [ ] DSA topic tracking
- [ ] Difficulty-based recommendations
- [ ] Code execution and test-case validation
- [ ] Automatic complexity analysis
- [ ] Interview simulation mode
- [ ] Voice-based AI interviewer
- [ ] Performance analytics
- [ ] Leaderboard
- [ ] Personalized learning roadmap
- [ ] Multi-language code support
- [ ] Persistent conversation history
- [ ] Advanced multi-agent architecture

## 🧠 AI Coaching Philosophy

DSA Coach AI focuses on learning rather than simply providing answers.

```text
Understand
   ↓
Analyze
   ↓
Identify Mistake
   ↓
Give Hint
   ↓
Guide
   ↓
Improve
```

## 👨‍💻 Author

**DSA Coach AI**

An AI-powered Data Structures and Algorithms interview coaching platform.

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

## 📜 License

This project is intended for educational and portfolio purposes.
