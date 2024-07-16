from django.db.models import Count
from django.utils import timezone

from .models import Post


def general_request(
        model_manager=Post.objects,
        hidden_post=True,
        comments=False
):
    queryset = model_manager.select_related(
        'location',
        'category',
        'author',
    ).order_by('-pub_date')

    if hidden_post:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )

    if comments:
        queryset = queryset.annotate(comment_count=Count('comments'))

    return queryset
