from django.core.paginator import Paginator

from yatube.settings import PAGINATOR


def paginate(request, posts):
    paginator = Paginator(posts, PAGINATOR)
    page_number = request.GET.get('page')

    return paginator.get_page(page_number)
