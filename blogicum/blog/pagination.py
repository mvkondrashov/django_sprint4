from django.core.paginator import Paginator


def pagination(request, related_name, posts_on_page):
    paginator = Paginator(related_name, posts_on_page)
    page_number = request.GET.get('page')

    return paginator.get_page(page_number)
