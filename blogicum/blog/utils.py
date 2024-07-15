from django.db.models import Count
from django.core.paginator import Paginator
from django.utils import timezone

from .models import Post


def general_request(
        model_manager=Post.objects,
        hidden_post=True,
        comments=False
):
    # по умолчанию отдает все посты модели
    queryset = model_manager.select_related(
        'location',
        'category',
        'author',
    ).order_by('-pub_date')

    # фильтр убирающий выдачу скрытых от публикации и отложенных постов
    if hidden_post:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )

    # фильтр добавляющий счетчик комментариев к посту
    if comments:
        queryset = queryset.annotate(comment_count=Count('comments'))

    return queryset


def pagination(request, related_name, posts_on_page):
    paginator = Paginator(related_name, posts_on_page)
    page_number = request.GET.get('page')

    return paginator.get_page(page_number)
