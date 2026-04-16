from fastapi import APIRouter, Depends
from schemas.skill import ChatMessage, ChatResponse
from utils.security import get_current_user
from models.user import User
from services.ai_engine import chat_completion

router = APIRouter()

# Simple in-memory history per user for the session
chat_histories = {}

@router.post("", response_model=ChatResponse)
async def chat_with_bot(
    chat_req: ChatMessage,
    current_user: User = Depends(get_current_user)
):
    user_id = str(current_user.id)
    if user_id not in chat_histories:
        chat_histories[user_id] = []
        
    chat_histories[user_id].append({"role": "user", "content": chat_req.message})
    
    # Keep history short
    if len(chat_histories[user_id]) > 10:
        chat_histories[user_id] = chat_histories[user_id][-10:]
        
    sys_instruction = f"You are a career counselor and technical internship advisor. You are talking to {current_user.full_name}. Provide brief, helpful, an professional career advice."
    if chat_req.context:
         sys_instruction += f"\nContext: {chat_req.context}"
         
    reply_text = await chat_completion(chat_histories[user_id], sys_instruction)
    
    chat_histories[user_id].append({"role": "assistant", "content": reply_text})
    
    return {
        "reply": reply_text,
        "suggestions": ["How can I improve my resume?", "What are common interview questions?"]
    }
