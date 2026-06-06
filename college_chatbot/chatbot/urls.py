from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_page, name="chat"),
    path("chat/", views.chatbot_api, name="chatbot_api"),
    path("new_chat/", views.new_chat_api, name="new_chat_api"),
    path("login/", views.login_page, name="login"),
    path("signup/", views.signup_page, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("home/", views.home_page, name="home"),
    path("history/", views.history_page, name="history"),
    path("conversation/", views.conversation_api, name="conversation_api"),
]
