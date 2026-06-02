from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, register_converter
from . import views

class AlphanumericConverter:
    regex = '[a-zA-Z0-9]+'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)

register_converter(AlphanumericConverter, 'alphanumeric')

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("aboutuser/", views.aboutuser, name="aboutuser"),
    path('indexadmin/', views.indexadmin, name='indexadmin'),
    path('admindashboard/', views.admindashboard, name='admindashboard'),
    path('indexuser/', views.indexuser, name='indexuser'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('useraccount/', views.useraccount, name='useraccount'),

    path('event/', views.event, name='event'),
    path('eventadmin/', views.eventadmin, name='eventadmin'),
    path('eventuser/', views.eventuser, name='eventuser'),

    path('adminaccount/', views.adminaccount, name='adminaccount'),
    path('adminregistration/<alphanumeric:event_id>/', views.adminregistration, name='adminregistration'),
    path('adminviewregistrations/<int:registration_id>/', views.adminviewregistrations, name='adminviewregistrations'),


    path('loginpageuser/', views.loginpageuser, name='loginpageuser'),
    path('loginpageuser/indexuser/', views.indexuser, name='indexuser'),

    path('loginpageadmin/', views.loginpageadmin, name='loginpageadmin'),
    path('loginpageadmin/indexadmin/', views.indexadmin, name='indexadmin'),
    path('event/registrations/<str:event_id>/', views.registrations, name='registrations'),
    path('eventuser/realregistrations/<str:event_id>/', views.realregistrations, name='realregistrations'),
    path('event/userregistrations/<str:event_id>/', views.userregistrations, name='userregistrations'),

    path('adminreport/', views.adminreport, name='adminreport'),
    path('admin/registration/update/<int:registration_id>/', views.update_registration_status, name='update_registration_status'),
    path('admineditevent/<str:event_id>/', views.admineditevent, name='admineditevent'),
    path('admincreateevent/', views.admincreateevent, name='admincreateevent'),
    path('adminfeedback/', views.adminfeedback, name='adminfeedback'),
    path('ajax_delete_event/', views.ajax_delete_event, name='ajax_delete_event'),


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)