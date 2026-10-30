
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from carbon_agent import root_agent


APP_NAME = "carbon_coach"

# Store conversations and activities in ADK sessions.
session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)

app = FastAPI(title="Carbon Coach")


class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str = Field(min_length=1, max_length=2000)


@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "Carbon Coach"}


@app.post("/api/session")
async def create_session():
    user_id = f"user_{uuid.uuid4().hex}"
    session_id = f"session_{uuid.uuid4().hex}"

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    return {
        "user_id": user_id,
        "session_id": session_id,
    }


@app.post("/api/chat")
async def chat(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(400, "Message cannot be empty.")

    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=request.user_id,
        session_id=request.session_id,
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Please start a new conversation.",
        )

    try:
        response_text = ""

        async for event in runner.run_async(
            user_id=request.user_id,
            session_id=request.session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part.from_text(text=message)],
            ),
        ):
            if event.is_final_response() and event.content:
                response_text = "\n".join(
                    part.text
                    for part in event.content.parts
                    if part.text
                )

        if not response_text:
            raise HTTPException(
                status_code=502,
                detail="The agent did not return a response.",
            )

        return {"response": response_text}

    except HTTPException:
        raise
    except Exception:
        # Keep internal errors and API credentials out of public responses.
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while contacting Carbon Coach.",
        )


HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carbon Coach | AI Carbon Assistant</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f0f7f2;
            color: #183b2b;
        }

        header {
            background: #176b45;
            color: white;
            padding: 22px;
            text-align: center;
        }

        header h1 {
            margin: 0;
            font-size: 27px;
        }

        header p {
            margin-bottom: 0;
            opacity: 0.9;
        }

        .container {
            max-width: 760px;
            margin: 35px auto;
            padding: 20px;
        }

        .chat-card {
            background: white;
            border-radius: 16px;
            padding: 22px;
            box-shadow: 0 5px 25px rgba(0,0,0,0.07);
        }

        #messages {
            height: 430px;
            overflow-y: auto;
            padding: 10px;
            border: 1px solid #e1eee5;
            border-radius: 10px;
            margin-bottom: 18px;
        }

        .message {
            padding: 12px 15px;
            border-radius: 12px;
            margin: 12px 0;
            max-width: 85%;
            white-space: pre-wrap;
            line-height: 1.5;
            overflow-wrap: anywhere;
        }

        .bot {
            background: #e7f5eb;
            margin-right: auto;
        }

        .user {
            background: #176b45;
            color: white;
            margin-left: auto;
        }

        .input-area {
            display: flex;
            gap: 10px;
        }

        input {
            flex: 1;
            min-width: 0;
            padding: 14px;
            border: 1px solid #cbdccf;
            border-radius: 9px;
            font-size: 15px;
        }

        button {
            border: none;
            border-radius: 9px;
            background: #176b45;
            color: white;
            padding: 0 22px;
            cursor: pointer;
            font-size: 15px;
        }

        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .status {
            color: #64776a;
            font-size: 13px;
            margin-top: 12px;
        }

        footer {
            text-align: center;
            color: #718277;
            font-size: 13px;
            margin-top: 22px;
        }

        @media (max-width: 500px) {
            .container {
                margin: 15px auto;
                padding: 12px;
            }

            #messages {
                height: 55vh;
            }

            button {
                padding: 0 14px;
            }
        }
    </style>
</head>

<body>

<header>
    <h1>🌱 Carbon Coach</h1>
    <p>Your AI-powered personal carbon footprint assistant</p>
</header>

<div class="container">
    <div class="chat-card">

        <div id="messages">
            <div class="message bot">
                Hello! I'm Carbon Coach 🌍

                Tell me about your daily activities.
                For example:
                • I travelled 10 km by bus.
                • I used 5 kWh of electricity.
                • I used my 1.5 kW AC for 4 hours.

                I'll help you understand and reduce your carbon footprint!
            </div>
        </div>

        <form id="chat-form" class="input-area">
            <input
                id="message-input"
                type="text"
                placeholder="Tell me about your activity..."
                maxlength="2000"
                required
            >
            <button id="send-button" type="submit">Send</button>
        </form>

        <div id="status" class="status">Connecting to Carbon Coach...</div>
    </div>

    <footer>
        Carbon Coach | Measure. Understand. Reduce.
    </footer>
</div>

<script>
    let userId = null;
    let sessionId = null;

    const messages = document.getElementById("messages");
    const form = document.getElementById("chat-form");
    const input = document.getElementById("message-input");
    const button = document.getElementById("send-button");
    const status = document.getElementById("status");

    function addMessage(text, sender) {
        const div = document.createElement("div");
        div.className = "message " + sender;
        div.textContent = text;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }

    async function startSession() {
        try {
            const response = await fetch("/api/session", {
                method: "POST"
            });

            if (!response.ok) {
                throw new Error("Could not create session.");
            }

            const data = await response.json();

            userId = data.user_id;
            sessionId = data.session_id;

            status.textContent = "Connected to Carbon Coach 🌱";
        } catch (error) {
            status.textContent = "Connection failed. Refresh the page to retry.";
        }
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const message = input.value.trim();

        if (!message || !userId || !sessionId) {
            return;
        }

        addMessage(message, "user");
        input.value = "";
        button.disabled = true;
        status.textContent = "Carbon Coach is thinking...";

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    user_id: userId,
                    session_id: sessionId,
                    message: message
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Request failed.");
            }

            addMessage(data.response, "bot");
            status.textContent = "Connected to Carbon Coach 🌱";

        } catch (error) {
            addMessage("Sorry, something went wrong: " + error.message, "bot");
            status.textContent = "Please try again.";
        }

        button.disabled = false;
        input.focus();
    });

    startSession();
</script>

</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE
