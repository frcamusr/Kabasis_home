from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import registro
from .views import verify_email

#vistas login customizado
from .views import CustomLoginView
from .views import custom_logout

from django.contrib.auth import views as auth_views



urlpatterns = [

    path('', registro, name= "registro"),

    

    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    #usuarios Alumnos
    path('usuarios_personalizados/', views.lista_usuarios_personalizados, name='lista_usuarios_personalizados'),
    path('usuarios_personalizados/crear/', views.crear_usuario_personalizado, name='crear_usuario_personalizado'),
    path('usuarios_personalizados/<int:id_usuario>/actualizar/', views.actualizar_usuario_personalizado, name='actualizar_usuario_personalizado'),
    path('usuarios_personalizados/<int:id_usuario>/eliminar/', views.eliminar_usuario_personalizado, name='eliminar_usuario_personalizado'),

    ##usuarios Asistentes
    path('usuarios_personalizados_asistentes/', views.lista_usuarios_personalizados_asistentes, name='lista_usuarios_personalizados_asistentes'),
    path('usuarios_personalizados_asistentes/crear/', views.crear_usuario_personalizado_asistente, name='crear_usuario_personalizado_asistente'),
    path('usuarios_personalizados_asistentes/<int:id_usuario>/actualizar/', views.actualizar_usuario_personalizado_asistente, name='actualizar_usuario_personalizado_asistente'),
    path('usuarios_personalizados_asistentes/<int:id_usuario>/eliminar/', views.eliminar_usuario_personalizado_asistente, name='eliminar_usuario_personalizado_asistente'),

    ##Usuarios Administradores
    path('usuarios_personalizados_administradores/', views.lista_usuarios_personalizados_administradores, name='lista_usuarios_personalizados_administradores'),
    path('usuarios_personalizados_administradores/crear/', views.crear_usuario_personalizado_administrador, name='crear_usuario_personalizado_administrador'),
    path('usuarios_personalizados_administradores/<int:id_usuario>/actualizar/', views.actualizar_usuario_personalizado_administrador, name='actualizar_usuario_personalizado_administrador'),
    path('usuarios_personalizados_administradores/<int:id_usuario>/eliminar/', views.eliminar_usuario_personalizado_administrador, name='eliminar_usuario_personalizado_administrador'),

    ##Áreas
    path('lista_areas/', views.lista_areas, name='lista_areas'),
    path('crear_area/', views.crear_area, name='crear_area'),
    path('areas/<int:id>/actualizar/', views.actualizar_area, name='actualizar_area'),
    path('areas/<int:id>/eliminar/', views.eliminar_area, name='eliminar_area'),
    
    #area inicio
    path('crear_area_inicio/', views.crear_area_inicio, name='crear_area_inicio'),

    ##menu administración

    path('menu_administracion/', views.menu_administracion, name='menu_administracion'),

    ###empresas##
    path('empresas/', views.listar_empresa, name='listar_empresa'),
    path('empresas/crear_empresa/', views.crear_empresa, name='crear_empresa'),
    path('empresas/<int:id>/actualizar/', views.actualizar_empresa, name='actualizar_empresa'),
    path('empresas/<int:id>/eliminar/', views.eliminar_empresa, name='eliminar_empresa'),

    ##carga de usuarios masivo##
    path('carga_masiva/', views.carga_masiva, name='carga_masiva'),

    ##Invitación por email
    path('invitacion_email/', views.invitacion_email, name='invitacion_email'),

    path('form_invitacion/', views.form_invitacion, name='form_invitacion'),

    ##verificar email
    path('verify-email/<uuid:token>/', verify_email, name='verify_email'),

    ##login customizado
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),


    ##Restablecer contraseña
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    ##formulario registro empresa
    path('registro_empresa/', views.registro_empresa, name='registro_empresa'),

    ##captcha
    path('captcha/', include('captcha.urls')),
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL[1:], document_root=settings.MEDIA_ROOT)
