from django.db import models

# Create your models here.
from django.db import models

class NewsPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name='Текст новости')
    image = models.ImageField(upload_to='news_images/', blank=True, null=True, verbose_name='Изображение')
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

