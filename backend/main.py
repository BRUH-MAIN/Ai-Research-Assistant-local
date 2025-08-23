from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

app = FastAPI(title="Chatbot API", version="1.0.0")

# Configure CORS to allow requests from your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port and common React port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq LLM
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("Warning: GROQ_API_KEY not found in environment variables")
    llm = None
else:
    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama-3.1-8b-instant"  # You can change this to other Groq models
    )

# Pydantic models for request/response
class PromptRequest(BaseModel):
    prompt: str

class PromptResponse(BaseModel):
    response: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Chatbot API is running!"}

@app.post("/api/chat", response_model=PromptResponse)
async def process_prompt(request: PromptRequest):
    """
    Process a prompt using Langchain Groq and return the response
    """
    try:
        if not llm:
            raise HTTPException(status_code=500, detail="Groq API key not configured")
        
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        # Process the prompt with Groq
        response = llm.invoke(request.prompt)
        
        # Extract the content from the response
        response_content = response.content if hasattr(response, 'content') else str(response)
        
        print(f"User prompt: {request.prompt}")
        print(f"Groq response: {response_content}")
        
        return PromptResponse(response=response_content)
    
    except Exception as e:
        print(f"Error processing prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing prompt: {str(e)}")

@app.get("/api/status")
async def get_status():
    """
    Get API status
    """
    return {
        "status": "online",
        "groq_configured": llm is not None,
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
