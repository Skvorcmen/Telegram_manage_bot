from django.contrib import admin
from .models import NewsPost
from .tasks import publish_to_telegram
from django.utils import timezone


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    # Поля, которые отображаются в списке новостей
    list_display = ('title', 'is_published', 'created_at', 'published_at')

    # Фильтры в правой части админки
    list_filter = ('is_published', 'created_at')

    # Поиск по этим полям
    search_fields = ('title', 'content')

    # Действия, которые можно выполнять с выбранными записями
    actions = ['publish_selected']

    # Поля, которые нельзя редактировать (только для чтения)
    readonly_fields = ('created_at', 'published_at')

    # ПРАВИЛЬНЫЙ синтаксис fieldsets:
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'content', 'image')
        }),
        ('Статус и даты', {
            'fields': ('is_published', 'created_at', 'published_at')
        }),
    )

    def publish_selected(self, request, queryset):
        """
        Действие: опубликовать выбранные новости и отправить в Telegram
        """
        count = 0
        for post in queryset:
            if not post.is_published:
                post.is_published = True
                post.published_at = timezone.now()
                post.save()
                publish_to_telegram(post)
                count += 1

        # Сообщение об успехе
        if count == 1:
            message = "1 новость опубликована"
        elif count > 1:
            message = f"{count} новости опубликованы"
        else:
            message = "Нет новостей для публикации (возможно, они уже опубликованы)"

        self.message_user(request, message)

    # Описание действия в выпадающем меню
    publish_selected.short_description = "Опубликовать выбранные новости в Telegram"

    # Порядок сортировки по умолчанию
    ordering = ('-created_at',)