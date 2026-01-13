from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from news import views
from django.contrib.auth import views as auth_views  # ← ДОБАВЬТЕ

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.news_list, name='news_list'),
    path('create/', views.create_news, name='create_news'),
    path('publish/<int:post_id>/', views.publish_news, name='publish_news'),

    # Аутентификация ← ДОБАВЬТЕ ЭТИ СТРОКИ
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)