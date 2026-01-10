from django.db import models


class NewsPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Текст новости")

    # НОВОЕ: Комментарий для внутреннего использования
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий/Заметки",
        help_text="Внутренние заметки о новости (не публикуется в Telegram)"
    )

    # Изображение
    image = models.ImageField(
        upload_to='news_images/',
        blank=True,
        null=True,
        verbose_name="Изображение"
    )

    # Видео
    video = models.FileField(
        upload_to='news_videos/',
        blank=True,
        null=True,
        verbose_name="Видео",
        help_text="Загрузите видеофайл (MP4, MOV, AVI)"
    )

    # URL на YouTube/Vimeo
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на видео",
        help_text="Или укажите ссылку на YouTube/Vimeo"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")
    published_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата публикации")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-created_at']  # Сортировка по дате создания

    # Метод для автоматического заполнения комментария
    def save(self, *args, **kwargs):
        # При первой публикации добавляем дату в комментарий
        if self.is_published and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()

            # Если комментарий пустой, добавляем дату публикации
            if not self.comment:
                self.comment = f"📅 Опубликовано: {timezone.now().strftime('%d.%m.%Y %H:%M')}"
            elif "📅 Опубликовано:" not in self.comment:
                # Добавляем дату к существующему комментарию
                self.comment += f"\n📅 Опубликовано: {timezone.now().strftime('%d.%m.%Y %H:%M')}"

        super().save(*args, **kwargs)