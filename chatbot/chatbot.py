from fastapi import Depends, APIRouter
from google import genai
import os
from dotenv import load_dotenv
import redis
from auth.auth import get_current_user
from auth.models import User
from chatbot.schemas import PromptRequest

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# redis_client = redis.Redis(
#     host="localhost",
#     port=6379,
#     db=0,
#     decode_responses=True
# )
redis_client = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

TTL=600 # 10min

def save_to_memory(user_id: str, role: str, message: str):
    key = f"chat:memory:{user_id}"
    redis_client.rpush(key, f"{role}: {message}")
    redis_client.expire(key, TTL)

def get_memory(user_id: str):
    key = f"chat:memory:{user_id}"
    return redis_client.lrange(key, 0, -1)


def chat_with_gemini(prompt: str):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[f"answer like a financial advisor {prompt}"]
        )
        # print(response.text)
        return response.text
    except Exception as e:
        print(f"Error fetching response from AI: {e}")

router=APIRouter(
    tags=["chatbot"]
)

@router.post("/chat")
async def chat(request: PromptRequest, user: User = Depends(get_current_user)):
    return {"response": chat_with_gemini(request.prompt)}

@router.post("/memory-chat/")
async def chat(message: PromptRequest, user: User = Depends(get_current_user)):
    user_id = str(user.id)
    save_to_memory(user_id, "user", message.prompt)
    response = f"{chat_with_gemini(message.prompt)}"
    save_to_memory(user_id, "assistant", response)
    # history = get_memory(user_id)
    return {"response": response}

@router.get("/memory-chat/")
def get_chat_history(user: User = Depends(get_current_user)):
    user_id = str(user.id)
    history = get_memory(user_id)
    return {"chat_history": history}