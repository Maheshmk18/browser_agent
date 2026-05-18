# Browser Automation Agent

> Give it a task in plain English — it opens a browser, thinks, acts, and returns results. Automatically.

---

## How It Works — LangGraph Flow

```
START → Supervisor → Planner → Browser Action → Vision → Decision
                                      ↑_______________|
                                      (loop until done)
                                            ↓
                                       Extractor → Reflector → END
```

### 1. Supervisor Node
- Understands what the user wants
- Converts vague input into a clear task
- Example: `"hey search rebal movie"` → `"Search YouTube for Rebal movie trailer"`

### 2. Planner Node
- Breaks the task into browser steps
- Example:
  1. Navigate to `https://www.youtube.com/results?search_query=rebal+movie`
  2. Click first video result

### 3. Browser Action Node
- Actually performs the step like a human
- Can: navigate, click, type, scroll, press keys

### 4. Vision Node
- Takes a screenshot after each action
- Uses AI to check what happened
- Example: `"YouTube search results loaded successfully"`

### 5. Decision Node *(Brain of the system)*
- **Case 1 — Success:** Move to next step
- **Case 2 — Failed:** Retry same step
- **Case 3 — All steps done:** Move to Extractor

### 6. Extractor Node
- Scrapes the final data from the page
- Extracts: video titles, links, URLs

### 7. Reflector Node
- Scores how well the task was completed (1–10)
- Saves result to database
- Example: `"Result quality = 9/10"`

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| LangGraph | Agent workflow & node pipeline |
| LangChain | LLM integration & chains |
| Groq AI | Fast LLM (llama-3.3-70b) |
| Playwright | Browser automation (Chromium) |
| FastAPI | REST API |
| MongoDB Atlas | Data persistence |

---

## Quick Start

**1. Clone the repo**
```bash
git clone https://github.com/Maheshmk18/browser_agent.git
cd browser_agent/browser-agent
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Install browser**
```bash
playwright install chromium
```

**4. Create `.env` file**
```env
MONGO_URI=your_mongodb_atlas_url
MONGO_DB_NAME=browser_agent
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_VISION_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
BROWSER_HEADLESS=false
BROWSER_TIMEOUT_MS=30000
BROWSER_KEEP_OPEN_SECONDS=60
MAX_RETRIES=3
```

**5. Run the server**
```bash
python -m uvicorn api.main:app
```

Server starts at `http://localhost:8000`

## Tech Stack

| Tool | Purpose |
|------|---------|
| LangGraph | Agent workflow & node pipeline |
| LangChain | LLM integration & chains |
| Groq AI | Fast LLM (llama-3.3-70b) |
| Playwright | Browser automation (Chromium) |
| FastAPI | REST API |
| MongoDB Atlas | Data persistence |

---

## Quick Start

**1. Clone the repo**
```bash
git clone https://github.com/Maheshmk18/browser_agent.git
cd browser_agent/browser-agent
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Install browser**
```bash
playwright install chromium
```

**4. Create `.env` file**
```env
MONGO_URI=your_mongodb_atlas_url
MONGO_DB_NAME=browser_agent
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_VISION_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
BROWSER_HEADLESS=false
BROWSER_TIMEOUT_MS=30000
MAX_RETRIES=3
```

**5. Run the server**
```bash
python -m uvicorn api.main:app 
```

Server starts at `http://localhost:8000`

---

## API Usage

**Start a task**
```http
POST http://localhost:8000/agent/run
Content-Type: application/json

{
  "input": "Search YouTube for Rebal movie trailer and get the top 5 video titles"
}
```

**Check status**
```http
GET http://localhost:8000/agent/tasks/{task_id}/status
```

**Get results**
```http
GET http://localhost:8000/agent/tasks/{task_id}/result
```

**Get full session steps**
```http
GET http://localhost:8000/agent/tasks/{task_id}/session
```

**Get error details**
```http
GET http://localhost:8000/agent/tasks/{task_id}/error
```

**Swagger UI**
```
http://localhost:8000/docs
```

---

## File Structure

```
browser-agent/
│
├── run.py                        <- START HERE - launches the server
├── .env                          <- all secret keys & settings (never commit this)
│
├── config/
│   └── settings.py               <- reads .env and makes settings available everywhere
│
├── agent/
│   └── browser_agent.py          <- BRAIN - runs the full agent pipeline
│
├── api/                          <- everything the outside world talks to
│   ├── main.py                   <- creates the FastAPI app
│   ├── routers/
│   │   └── agent.py              <- all API endpoints
│   ├── controllers/
│   │   └── agent_controller.py   <- receives requests, starts agent in background
│   └── schemas/
│       └── agent.py              <- request/response JSON shapes
│
├── browser/                      <- controls the real browser
│   ├── engine.py                 <- opens & closes Chromium
│   ├── actions.py                <- click, type, navigate, scroll
│   └── screenshot.py             <- captures screenshots
│
├── graph/                        <- LangGraph pipeline
│   ├── state.py                  <- shared state between all nodes
│   ├── builder.py                <- connects nodes into a flow
│   └── nodes/
│       ├── supervisor.py         <- understands & clarifies task
│       ├── planner.py            <- creates action plan
│       ├── browser_action.py     <- executes one browser step
│       ├── vision.py             <- checks screenshot with AI
│       ├── decision.py           <- next step / retry / done
│       ├── extractor.py          <- scrapes results from page
│       └── reflector.py          <- scores & saves results
│
├── llm/                          <- AI / LLM layer
│   ├── client.py                 <- connects to Groq AI
│   ├── prompts.py                <- all AI instructions
│   ├── chains.py                 <- runs AI calls & parses responses
│   └── embeddings.py             <- text to vectors (for memory)
│
└── db/mongo/                     <- database layer
    ├── client.py                 <- MongoDB connection
    ├── models.py                 <- Task, Session, Result models
    └── repositories/
        ├── task_repo.py          <- save/get tasks
        ├── session_repo.py       <- save/get sessions & steps
        └── result_repo.py        <- save/get results
```

---

## Example Result

```json
{
  "extracted_data": {
    "page_title": "rebal movie - YouTube",
    "videos": [
      { "title": "Rebal Official Trailer", "url": "https://www.youtube.com/watch?v=abc123" },
      { "title": "Rebal Full Movie 2024", "url": "https://www.youtube.com/watch?v=xyz456" }
    ]
  },
  "score": 9,
  "metrics": {
    "total_steps": 2,
    "retries": 0,
    "duration_ms": 45000
  }
}
```

---

## Author

**Mahesh** — [GitHub](https://github.com/Maheshmk18) · [LinkedIn](https://linkedin.com/in/maheshmk18)

```

Server starts at `http://localhost:8000`

---

## API Usage

**Start a task**
```http
POST http://localhost:8000/agent/run
Content-Type: application/json

{
  "input": "Search YouTube for Rebal movie trailer and get the top 5 video titles"
}
```

**Check status**
```http
GET http://localhost:8000/agent/tasks/{task_id}/status
```

**Get results**
```http
GET http://localhost:8000/agent/tasks/{task_id}/result
```

**Get full session steps**
```http
GET http://localhost:8000/agent/tasks/{task_id}/session
```

**Get error details**
```http
GET http://localhost:8000/agent/tasks/{task_id}/error
```

**Swagger UI**
```
http://localhost:8000/docs
```

---

## File Structure

```
browser-agent/

│
├── config/
│   └── settings.py               <- reads .env and makes settings available everywhere
│
├── agent/
│   └── browser_agent.py          <- BRAIN - runs the full agent pipeline
│
├── api/                          <- everything the outside world talks to
│   ├── main.py                   <- creates the FastAPI app
│   ├── routers/
│   │   └── agent.py              <- all API endpoints
│   ├── controllers/
│   │   └── agent_controller.py   <- receives requests, starts agent in background
│   └── schemas/
│       └── agent.py              <- request/response JSON shapes
│
├── browser/                      <- controls the real browser
│   ├── engine.py                 <- opens & closes Chromium
│   ├── actions.py                <- click, type, navigate, scroll
│   └── screenshot.py             <- captures screenshots
│
├── graph/                        <- LangGraph pipeline
│   ├── state.py                  <- shared state between all nodes
│   ├── builder.py                <- connects nodes into a flow
│   └── nodes/
│       ├── supervisor.py         <- understands & clarifies task
│       ├── planner.py            <- creates action plan
│       ├── browser_action.py     <- executes one browser step
│       ├── vision.py             <- checks screenshot with AI
│       ├── decision.py           <- next step / retry / done
│       ├── extractor.py          <- scrapes results from page
│       └── reflector.py          <- scores & saves results
│
├── llm/                          <- AI / LLM layer
│   ├── client.py                 <- connects to Groq AI
│   ├── prompts.py                <- all AI instructions
│   ├── chains.py                 <- runs AI calls & parses responses
│   └── embeddings.py             <- text to vectors (for memory)
│
└── db/mongo/                     <- database layer
    ├── client.py                 <- MongoDB connection
    ├── models.py                 <- Task, Session, Result models
    └── repositories/
        ├── task_repo.py          <- save/get tasks
        ├── session_repo.py       <- save/get sessions & steps
        └── result_repo.py        <- save/get results
```

---

## Example Result

```json
{
  "extracted_data": {
    "page_title": "rebal movie - YouTube",
    "videos": [
      { "title": "Rebal Official Trailer", "url": "https://www.youtube.com/watch?v=abc123" },
      { "title": "Rebal Full Movie 2024", "url": "https://www.youtube.com/watch?v=xyz456" }
    ]
  },
  "score": 9,
  "metrics": {
    "total_steps": 2,
    "retries": 0,
    "duration_ms": 45000
  }
}
```

---

## Author

**Mahesh** — [GitHub](https://github.com/Maheshmk18) · [LinkedIn](https://linkedin.com/in/maheshmk18)
