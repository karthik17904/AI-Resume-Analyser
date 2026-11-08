from fastapi import APIRouter
from app.api.schemas import ChatPayload
from app.services.career_advice import chat as local_chat
router=APIRouter(prefix='/api',tags=['Career guidance'])
@router.post('/chat')
def chat(payload:ChatPayload):return local_chat(payload)
