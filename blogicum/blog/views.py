from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.conf import settings
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .query_utils import general_request

from .pages import pagination

from .forms import CommentForm, PostForm, UserEditForm

from .models import Category, Post

from .mixins import CommentMixin, OnlyAuthorMixin

User = get_user_model()


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_post(request, post_id):

    if not request.user.is_authenticated:
        return redirect('blog:post_detail', post_id=post_id)

    instance = get_object_or_404(Post, id=post_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    form = PostForm(request.POST or None, instance=instance)
    context = {'form': form}

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/create.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )

    page_obj = pagination(
        request,
        general_request(category.posts, hidden_post=True, comments=True),
        settings.POSTS_ON_PAGE
    )

    return render(
        request,
        'blog/category.html',
        {'category': category, 'page_obj': page_obj, }
    )


def profile_user(request, username):
    author = get_object_or_404(User, username=username)
    posts = general_request(
        model_manager=author.posts,
        hidden_post=(author != request.user),
        comments=True
    )

    page_obj = pagination(request, posts, settings.POSTS_ON_PAGE)
    context = {'profile': get_object_or_404(User, username=username)}
    context['page_obj'] = page_obj

    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    form = UserEditForm(request.POST or None, instance=request.user)
    context = {'form': form}

    if form.is_valid():
        form.save()
        return redirect('blog:profile', request.user)

    return render(request, 'blog/user.html', context)


class CommentUpdateView(OnlyAuthorMixin, CommentMixin, UpdateView):

    fields = 'text',


class CommentDeleteView(OnlyAuthorMixin, CommentMixin, DeleteView):

    pass


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):

        return reverse_lazy('blog:profile', args=[self.request.user.username])

    def form_valid(self, form):
        form.instance.author = self.request.user

        return super().form_valid(form)


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class PostDetailView(DetailView):
    model = Post
    ordering = '-pub_date'
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return super().get_queryset().filter(
                Q(author=self.request.user)
                | (
                    Q(is_published=True)
                    & Q(pub_date__lte=timezone.now())
                    & Q(category__is_published=True)
                )
            )

        else:
            return general_request(
                super().get_queryset(),
                hidden_post=True,
                comments=False,
            )


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = settings.POSTS_ON_PAGE

    def get_queryset(self):

        return general_request(
            super().get_queryset(),
            hidden_post=True,
            comments=True
        )
