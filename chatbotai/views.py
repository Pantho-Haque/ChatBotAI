from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import uuid
from langchain.messages import SystemMessage, HumanMessage
from .services import LLMService

# Store sessions per user (use Redis/database in production)
SESSIONS = {}

@csrf_exempt
@require_http_methods(["POST"])
def initialize(request):
    try:
        data = json.loads(request.body)
        content = data.get("content", "")

        if not content:
            return JsonResponse({"error": "Content is required"}, status=400)

        system_prompt = f"""
            You have this content and you have to answer only on this content:
            {content}
            anything external to this content should be unknown to you.if i ask you something that is not related to this content, you should not answer.And return with a gentel message that you cant answer any question outsife of this document.
        """
        
        message_for_topic_name = f"""
            give me only one topic name based on this content:
            {content}
            topic name should be short and within one word to 3 words.
        """
        
        llm = LLMService.get_llm()
        topicName = llm.invoke(message_for_topic_name)

        # Create unique session for this user
        session_id = str(uuid.uuid4())
        SESSIONS[session_id] = {"system_prompt": system_prompt}

        return JsonResponse(
            {
                "session_id": session_id,  # Frontend must save this
                "response": "Hi there! Lets talk about " + topicName.content.upper() + " today?",
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def ask(request):
    try:
        data = json.loads(request.body)
        message = data.get("message", "")
        session_id = data.get("session_id", "")

        if not message:
            return JsonResponse({"error": "Message is required"}, status=400)
        
        if not session_id:
            return JsonResponse({"error": "Session ID is required"}, status=400)

        # Get THIS user's system prompt
        session_data = SESSIONS.get(session_id)
        
        if not session_data:
            return JsonResponse({"error": "Invalid or expired session"}, status=400)

        system_prompt = session_data["system_prompt"]

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=message),
        ]

        llm = LLMService.get_llm()
        response = llm.invoke(messages)

        return JsonResponse({"response": response.content})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)