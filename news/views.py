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
from django.contrib.auth.decorators import login_required



@login_required
def create_news(request):
    if request.method == 'POST':
        form = NewsPostForm(request.POST, request.FILES)

        if form.is_valid():
            # ВАЖНО: commit=False чтобы можно было обработать файл
            post = form.save(commit=False)

            # Если есть файл, сохраняем его отдельно
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                post.image = image_file  # Django сам сохранит файл

            # Теперь сохраняем
            post.save()

            # Форма сохранит ManyToMany связи если они есть
            form.save_m2m()

            # Публикация
            if 'publish_now' in request.POST:
                post.is_published = True
                post.published_at = timezone.now()
                post.save()
                publish_to_telegram(post)

            return redirect('news_list')
    else:
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


def news_list(request):
    """Показать список всех новостей."""
    posts = NewsPost.objects.all().order_by('-created_at')

    # Рассчитываем статистику
    total = posts.count()

    # Способ 1: Используем QuerySet
    published_count = NewsPost.objects.filter(is_published=True).count()
    draft_count = NewsPost.objects.filter(is_published=False).count()

    # Или Способ 2: Вручную (если posts уже получен)
    # published_count = sum(1 for post in posts if post.is_published)
    # draft_count = total - published_count

    context = {
        'posts': posts,
        'total_count': total,
        'published_count': published_count,
        'draft_count': draft_count,
    }

    return render(request, 'news/news_list.html', context)
# Create your views here.
