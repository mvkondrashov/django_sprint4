from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.urls import reverse_lazy, reverse
from django.utils import timezone

from .models import Category, Post, Comment

from .forms import CommentForm, CreationForm, PostForm, UserEditForm

POSTS_ON_PAGE = 5

User = get_user_model()


def general_request(model_manager=Post.objects):
    return model_manager.select_related(
        'location',
        'category',
        'author',
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )


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
    paginator = Paginator(general_request(category.posts), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'blog/category.html',
        {'category': category, 'page_obj': page_obj, }
    )


def profile_user(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(
        author=author
    ).order_by(
        '-pub_date'
    ).annotate(comment_count=Count('comments'))
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    context = {'profile': get_object_or_404(User, username=username)}
    context['page_obj'] = paginator.get_page(page_number)

    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    form = UserEditForm(request.POST or None, instance=request.user)
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:profile', request.user)
    return render(request, 'blog/user.html', context)


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class ProfileListView(ListView):
    model = Post
    paginate_by = 10
    ordering = '-pub_date'
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = User.objects.get(
            username=self.request.GET.get('user')
        )

        return context


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    fields = 'text',
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


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
                Q(is_published=True) | Q(author=self.request.user),
            )
        else:
            return super().get_queryset().filter(
                Q(is_published=True),
            )


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(comment_count=Count('comments'))
