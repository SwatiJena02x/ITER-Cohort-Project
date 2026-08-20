# DSA Coach — AI-Powered Coding Practice

## How to run locally

### 1. Backend Setup

1. Open a terminal and navigate to the `backend` folder:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - **Windows**: `.\venv\Scripts\activate`
   - **Mac/Linux**: `source venv/bin/activate`

4. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up your environment variables:
   - Copy `.env.example` to `.env`
   - Add your Gemini API key in the `.env` file (`GEMINI_API_KEY=your_key_here`)

6. Run the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   The backend will be running at `http://localhost:8000`.

### 2. Frontend Setup

1. Open a new terminal and navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`.
