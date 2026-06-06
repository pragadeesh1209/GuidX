from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .utils import get_bot_response
from .models import StudentProfile, SearchHistory
import json

def home_page(request):
    return render(request, "chatbot/home.html")

def login_page(request):
    if request.user.is_authenticated:
        return redirect("/chatbot/")
    error = None
    email_value = ""
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        email_value = email
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            if user:
                login(request, user)
                return redirect("/chatbot/")
            else:
                error = "Invalid email or password."
        except User.DoesNotExist:
            error = "Invalid email or password."
    return render(request, "chatbot/login.html", {"error": error, "email_value": email_value})

def signup_page(request):
    if request.user.is_authenticated:
        return redirect("/chatbot/")
    error = None
    email_value = ""
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        email_value = email
        if not email or not password:
            error = "Email and password are required."
        elif User.objects.filter(email=email).exists():
            error = "An account with this email already exists."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        else:
            username = email.split("@")[0] + str(User.objects.count())
            User.objects.create_user(username=username, email=email, password=password)
            return redirect("/chatbot/login/?signup=success")
    return render(request, "chatbot/signup.html", {"error": error, "email_value": email_value})

def logout_view(request):
    logout(request)
    return redirect("/chatbot/home/")

def chat_page(request):
    if not request.user.is_authenticated:
        return redirect("/chatbot/login/")
    if not request.session.session_key:
        request.session.create()
    
    # Group history by conversation_id for the sidebar
    # We take the first message of each conversation as the title
    from django.db.models import OuterRef, Subquery, Min
    
    # Get the earliest timestamp for each conversation to find the 'first' message
    first_msgs_ts = SearchHistory.objects.filter(
        user=request.user,
        conversation_id__isnull=False
    ).values('conversation_id').annotate(first_ts=Min('timestamp'))
    
    # Get the actual messages that match those first timestamps
    recent_conversations = SearchHistory.objects.filter(
        user=request.user,
        timestamp__in=Subquery(first_msgs_ts.values('first_ts'))
    ).order_by("-timestamp")[:15]
    
    return render(request, "chatbot/chat.html", {
        "recent_conversations": recent_conversations,
        "current_conv_id": request.session.get('current_conv_id')
    })

def new_chat_api(request):
    import uuid
    new_id = str(uuid.uuid4())
    request.session['current_conv_id'] = new_id
    return JsonResponse({"status": "success", "conversation_id": new_id})

def history_page(request):
    if not request.user.is_authenticated:
        return redirect("/chatbot/login/")
    history = SearchHistory.objects.filter(user=request.user).order_by("-timestamp")[:50]
    return render(request, "chatbot/history.html", {"history": history})

def chatbot_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message", "").strip()
            if not message:
                return JsonResponse({"reply": "Please say something!"})
            if not request.session.session_key:
                request.session.create()
            
            # Use provided conversation_id or current session one
            conv_id = data.get("conversation_id") or request.session.get('current_conv_id')
            if not conv_id:
                import uuid
                conv_id = str(uuid.uuid4())
                request.session['current_conv_id'] = conv_id

            session_id = request.session.session_key
            profile, created = StudentProfile.objects.get_or_create(session_id=session_id)
            if request.user.is_authenticated:
                profile.user = request.user
                profile.save()
            student_details = {
                "education_level": profile.education_level,
                "stream": profile.stream,
                "marks": profile.marks,
                "location": profile.location,
                "interests": profile.interests,
                "ug_degree": getattr(profile, "ug_degree", None),
                "current_subcategory": profile.current_subcategory,
                "current_course_index": profile.current_course_index,
            }
            student_details = {k: v for k, v in student_details.items() if v is not None}
            
            # Only fetch history for the CURRENT conversation
            history_objs = SearchHistory.objects.filter(
                profile=profile, 
                conversation_id=conv_id
            ).order_by("-timestamp")[:10]
            
            history = [{"user": h.query, "bot": h.response} for h in reversed(history_objs)]
            reply, suggestions, updated_details = get_bot_response(message, history, student_details)
            profile.education_level = updated_details.get("education_level", profile.education_level)
            profile.stream = updated_details.get("stream", profile.stream)
            profile.marks = updated_details.get("marks", profile.marks)
            profile.location = updated_details.get("location", profile.location)
            profile.interests = updated_details.get("interests", profile.interests)
            profile.ug_degree = updated_details.get("ug_degree", profile.ug_degree)
            profile.current_subcategory = updated_details.get("current_subcategory", profile.current_subcategory)
            profile.current_course_index = updated_details.get("current_course_index", profile.current_course_index)
            profile.save()
            
            history_obj = SearchHistory.objects.create(
                profile=profile, 
                query=message, 
                response=reply,
                conversation_id=conv_id
            )
            if request.user.is_authenticated:
                history_obj.user = request.user
                history_obj.save()
            safe_reply = reply.encode("utf-8", errors="ignore").decode("utf-8")
            return JsonResponse({"reply": safe_reply, "suggestions": suggestions, "conversation_id": conv_id})
        except Exception as e:
            import traceback
            print(f"Chatbot API Error: {e}")
            print(traceback.format_exc())
            return JsonResponse({"reply": f"Internal Error: {str(e)}", "suggestions": []})
    return JsonResponse({"reply": "Invalid request"}, status=400)

def conversation_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    conv_id = request.GET.get("conversation_id", "")
    conv_group = request.GET.get("group", "")
    
    qs = SearchHistory.objects.filter(user=request.user).order_by("timestamp")
    
    if conv_id:
        qs = qs.filter(conversation_id=conv_id)
    elif conv_group:
        from django.utils import timezone
        from datetime import timedelta
        now = timezone.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        if conv_group == "Today":
            qs = qs.filter(timestamp__date=today)
        elif conv_group == "Yesterday":
            qs = qs.filter(timestamp__date=yesterday)
        elif conv_group == "This Week":
            qs = qs.filter(timestamp__date__gte=week_ago, timestamp__date__lt=yesterday)
        elif conv_group == "Older":
            qs = qs.filter(timestamp__date__lt=week_ago)
    
    messages = [{"query": h.query, "response": h.response, "time": h.timestamp.strftime("%H:%M")} for h in qs[:50]]
    return JsonResponse({"messages": messages})
