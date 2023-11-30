from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from django.contrib.auth import views as auth_views

from enrichment.views import SignupView, UserLoginView
from enrichment.forms import UserPasswordResetForm, PasswordResetConfirmationForm

from django.urls import path
from . import views

urlpatterns = [
    path('analysis_progress/<uuid:task_id>', views.ResultView.as_view(), name='analysis_progress'),
    path('analysis_from_archive/<uuid:task_id>', views.ResultView.as_view(template_name='results_from_archive.html'), name='analysis_archive'),
    path('completed_results/<uuid:task_id>', views.ResultFromArchive.as_view(), name='completed_results'),

    path('', views.index, name='index'),
    path('analysis/', views.AnalysisFormView.as_view(), name='analysis'),
    path('get_record', views.SearchRecordView.as_view(), name='get_record'),
    path('get_record/<uuid:task_id>', views.RecordView.as_view(), name='record'),
    path('myrecords/', views.UserRecords.as_view(), name='user_records'),
    path('contact_us', views.ContactUsView.as_view(), name='contact_us'),

    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('reset_password/', views.CustomPasswordResetView.as_view(), name ='reset_password'),

    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='account/password_reset_done.html'), name ='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(
        template_name='account/password_reset_confirm.html',
        form_class=PasswordResetConfirmationForm), name ='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='account/password_reset_complete.html'
    ), name ='password_reset_complete'),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)