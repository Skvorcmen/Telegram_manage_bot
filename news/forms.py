from django import forms
from .models import NewsPost

class NewsPostForm(forms.ModelForm):
    class Meta:
        model = NewsPost
        fields = ['title', 'content', 'comment', 'image', 'video', 'video_url']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Текст новости, который увидят подписчики...'
            }),
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Внутренние заметки: дата постинга, особенности и т.д.'
            }),
            'video_url': forms.URLInput(attrs={
                'placeholder': 'https://youtube.com/watch?v=...'
            }),
        }
        help_texts = {
            'comment': 'Не публикуется в Telegram. Для внутреннего использования.',
            'video': 'Максимальный размер: 50MB. Форматы: MP4, MOV, AVI',
            'video_url': 'Альтернатива: ссылка на YouTube или Vimeo',
        }