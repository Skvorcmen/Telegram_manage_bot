from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import NewsPostForm
from .models import NewsPost
from .tasks import publish_to_telegram
from django.utils import timezone


def news_list(request):
    """Показать список всех новостей"""
    posts = NewsPost.objects.all().order_by('-created_at')
    return render(request, 'news/news_list.html', {'posts': posts})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from .forms import NewsPostForm
from .models import NewsPost
from .tasks import publish_to_telegram


@login_required
def create_news(request):
    """Создание новой новости"""
    if request.method == 'POST':
        form = NewsPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()

            # Если нужно сразу публиковать
            if 'publish_now' in request.POST:
                post.is_published = True
                post.published_at = timezone.now()
                post.save()
                publish_to_telegram(post)

            # ВАЖНО: всегда возвращаем redirect после успешной обработки POST
            return redirect('news_list')
        else:
            # Если форма невалидна, показываем ее снова с ошибками
            return render(request, 'news/create_news.html', {'form': form})
    else:
        # GET запрос - показываем пустую форму
        form = NewsPostForm()
        return render(request, 'news/create_news.html', {'form': form})


@login_required
def publish_news(request, post_id):
    """Опубликовать существующую новость"""
    print(f"🔄 DEBUG: publish_news вызван для post_id={post_id}")

    try:
        post = NewsPost.objects.get(id=post_id)
        print(f"🔍 DEBUG: Найдена новость: '{post.title}'")
        print(f"🔍 DEBUG: Текущий статус is_published: {post.is_published}")

        if not post.is_published:
            post.is_published = True
            post.published_at = timezone.now()
            post.save()  # ← ВАЖНО: сохранить перед отправкой!
            print(f"💾 DEBUG: Новость сохранена, is_published={post.is_published}")

            # Вызываем отправку
            result = publish_to_telegram(post)
            print(f"📤 DEBUG: Результат отправки: {result}")
        else:
            print("ℹ️ DEBUG: Новость уже опубликована")

    except NewsPost.DoesNotExist:
        print(f"❌ DEBUG: Новость с id={post_id} не найдена")

    return redirect('news_list')
# Create your views here.
