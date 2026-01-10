from django.contrib import admin
from .models import NewsPost
# Register your models here.


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('title',)
    actions = ['publish_selected']

    def publish_selected(self, request, queryset):
        from django.utils import timezone
        from .tasks import publish_to_telegram

        for post in queryset:
            if not post.is_published:
                post.is_published = True
                post.published_at = timezone.now()
                post.save()
                publish_to_telegram.delay(post.id)

            self.message_user(request, f'Новостей опубликовано {queryset.count()}')
        publish_selected.short_description = 'Опубликовать выбранные новости'