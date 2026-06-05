from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path("user_register/", views.user_register, name="user_register"),
    path('login/', views.login, name='login'),
    path('user_register', views.user_register, name='user_register'),
    path('advocate_register/', views.advocate_register, name='advocate_register'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add_categories/', views.add_categories, name='add_categories'),
    path('manage_court/', views.manage_court, name='manage_court'),
    path('approve_advocates/', views.approve_advocates, name='approve_advocates'),
    path('approve_advocates/<int:adv_id>/<str:action>/', views.approve_advocates, name='advocate_action'),
    path('blockchain_transactions/', views.blockchain_transactions, name='blockchain_transactions'),
    path('view_complaints/', views.view_complaints, name='view_users_accounts'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('advocate_dashboard/', views.advocate_dashboard, name='advocate_dashboard'),
    path('upload_evidence/', views.upload_evidence, name='upload_evidence'),
    path('submit_case_request/', views.submit_case_request, name='submit_case_request'),
    path('view_categories/', views.view_categories, name='view_categories'),
    path('view_users_accounts/',views.view_users_accounts,name='view_users_accounts'),
    path('delete_user/<int:id>/',views.delete_user,name='delete_user'),


    path('submit_case_request/', views.submit_case_request, name='submit_case_request'),
    path('view_case_requests/', views.view_case_requests, name='view_case_requests'),
    path('case_action/<int:case_id>/<str:action>/', views.case_action, name='case_action'),
    path('view_advocate_responses', views.view_advocate_responses, name='view_advocate_responses'),
    path('court_dashboard', views.court_dashboard, name='court_dashboard'),
    path('delete_court/<int:id>/', views.delete_court, name='delete_court'),
    path('delete_category/<int:id>/', views.delete_category, name='delete_category'),
    path('responded_cases',views.responded_cases,name='responded_cases'),
    path('assign_to_court/<int:case_id>/', views.assign_to_court, name='assign_to_court'),
    path('upload_documents',views.upload_documents,name='upload_documents'),
    path('assign_case/', views.assign_case, name='assign_case'),
    path('view_blockchain_cases/', views.view_blockchain_cases, name='view_blockchain_cases'),
    path('court_assign_advocate/<int:case_id>/', views.court_assign_advocate, name='court_assign_advocate'),
    path('court_case_action/<int:case_id>/<str:action>/', views.court_case_action, name='court_case_action'),
    path('update_hearing_schedule/', views.update_hearing_schedule, name='update_hearing_schedule'),
    path('court_updates/', views.court_updates, name='court_updates'),
    path('view_case_progress/', views.view_case_progress, name='view_case_progress'),
    path('view_assigned_cases/', views.view_assigned_cases, name='view_assigned_cases'),
    path('advocate_court_action/<int:case_id>/<str:action>/', views.advocate_court_action, name='advocate_court_action'),
    # 🔵 JSON chatbot (no reload)
    path('chat/', views.chat_bot, name='chat'),
    path('court_will_assign_case/', views.court_assign_case, name='court_will_assign_case'),
    path('advocate-court-cases/', views.advocate_court_cases, name='advocate_court_cases'),
    path('accept-case/<int:case_id>/', views.accept_court_case, name='accept_court_case'),
    path('reject-case/<int:case_id>/', views.reject_court_case, name='reject_court_case'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)