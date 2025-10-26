from django.urls import path
from . import views

app_name = 'lungcancer'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('change-password/', views.change_password, name='change_password'),
    path('predict/', views.predict, name='predict'),
    path('result/<int:pk>/', views.result, name='result'),
    path('patients/result/<int:result_id>/', views.patient_detail, name='patient_result_detail'),
    path('patients/result/<int:result_id>/update/', views.patient_update, name='patient_result_update'),
    path('patients/result/<int:result_id>/delete/', views.patient_delete, name='patient_result_delete'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/update/', views.patient_update, name='patient_update'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    path('patients/', views.patient_list, name='patient_list'),
    path('visualization/', views.visualization, name='visualization'),
    path('add-notice/', views.add_notice, name='add_notice'),
    path('delete-notice/<int:notice_id>/', views.delete_notice, name='delete_notice'),
    path('qna/', views.qna_list, name='qna_list'),
    path('qna/ask/', views.qna_ask, name='qna_ask'),
    path('qna/<int:pk>/answer/', views.qna_answer, name='qna_answer'),
]

