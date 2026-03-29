"""Chatbot API for direct user interaction."""
import uuid
from fastapi import APIRouter, Depends
from app.api.schemas import ChatRequest, ChatResponse
from app.dependencies import get_env
from app.env.environment import SupportEnvironment
from app.models.ticket import Ticket
from app.core.constants import ResolutionStatus

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse, summary="Send a message to the support bot")
async def chat(body: ChatRequest, env: SupportEnvironment = Depends(get_env)):
    # 1. Initialize or retrieve session
    session_id = body.session_id
    is_new = False
    
    if not session_id or not env.sm.get(session_id):
        session_id = str(uuid.uuid4())
        is_new = True
        state = env.sm.create("custom-chat")
        state.session_id = session_id
        # We simulate a ticket just to keep the state working
        state.ticket = Ticket(
            task_id="custom-chat", 
            text=body.message, 
            category="general", 
            difficulty="medium"
        )
        env.sm.update(state)
    else:
        state = env.sm.get(session_id)
        if state.ticket:
            state.ticket.text += "\n" + body.message

    # 2. Classify intent
    result = await env.classifier.classify(body.message)
    category = result.get("category", "general")
    if state.ticket:
        state.ticket.category = category

    # 3. Retrieve Knowledge
    kb_results = env.retriever.retrieve(body.message)

    # 4. Generate Response
    history = env.conv.get_history(session_id)
    env.conv.add_turn(session_id, "user", body.message)
    
    response_text = await env.generator.generate(
        ticket_text=state.ticket.text if state.ticket else body.message,
        category=category,
        kb_results=kb_results,
        conversation_history=history,
    )
    
    # Check if resolved or escalated based on the response content
    detected_status = env.resolver.detect_resolution(response_text)
    
    env.conv.add_turn(session_id, "agent", response_text)
    
    is_resolved = (detected_status == ResolutionStatus.RESOLVED)
    is_escalated = (detected_status == ResolutionStatus.ESCALATED)
    
    return ChatResponse(
        session_id=session_id,
        response=response_text,
        category=category,
        is_resolved=is_resolved,
        is_escalated=is_escalated
    )
