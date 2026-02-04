from django.urls import path
from . import views

urlpatterns = [
    path('', views.go_home, name='go_home'),
    path('admin_panel/', views.go_home, name='go_admin_panel'),
    path('elementos/', views.mostrar_elementos, name='go_elementos'),
    path('categories/show', views.show_categories, name='show_categories'),
    path('data_load/', views.data_load, name='go_data_load'),
    path('rankings/<int:id>/', views.go_rankings, name='go_rankings'),
    path('login/', views.do_login, name='do_login'),
    path('register/', views.do_register, name='do_register'),
    path('logout/', views.logout_user, name='logout_user'),
]