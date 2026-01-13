from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views  # ← ДОБАВЬТЕ ЭТУ СТРОКУ
from news import views
from django.http import JsonResponse

def debug_info(request):
    info = {
        'database_tables': list(NewsPost.objects.values_list('id', flat=True)[:5]),
        'user_count': User.objects.count(),
        'admin_exists': User.objects.filter(username='admin').exists(),
        'static_files': 'check',
    }
    return JsonResponse(info)

urlpatterns = [
    path('debug/', debug_info, name='debug'),
    path('admin/', admin.site.urls),
    path('', views.news_list, name='news_list'),
    path('create/', views.create_news, name='create_news'),
    path('publish/<int:post_id>/', views.publish_news, name='publish_news'),

    # Аутентификация - КРИТИЧЕСКИ ВАЖНО!
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)