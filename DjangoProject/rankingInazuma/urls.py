from django.urls import path
from . import views

urlpatterns = [
    # --- Inicio y Autenticación ---
    path('', views.go_home, name='go_home'),
    path('login/', views.do_login, name='do_login'),
    path('registro/', views.do_register, name='do_register'),
    path('logout/', views.logout_user, name='logout_user'),

    # --- Panel de Administración (RF10 y RF4) ---
    path('admin-panel/', views.go_admin_panel, name='go_admin_panel'),
    path('admin-panel/carga-datos/', views.data_load, name='data_load'),
    path('admin-panel/categorias/', views.categories, name='categories'),
    path('admin-panel/eliminar-categoria/<int:code>/', views.delete_category, name='delete_category'),

    # --- Rankings y Visualización (RF8) ---
    path('categorias/', views.show_categories, name='show_categories'),
    path('ranking/<int:id>/', views.go_rankings, name='go_rankings'),
    path('guardar-ranking/', views.save_top, name='save_top'),
    path('mis-rankings/', views.rankings_usuario, name='rankings_usuario'),

    # --- Listado General ---
    path('explorar/', views.mostrar_elementos, name='mostrar_elementos'),
]