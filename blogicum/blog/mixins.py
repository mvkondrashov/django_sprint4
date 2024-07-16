from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.mixins import UserPassesTestMixin

from .models import Comment


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()

        return object.author == self.request.user

    def handle_no_permission(self):

        return redirect(
            'blog:post_detail',
            post_id=self.kwargs['post_id']
        )


class CommentMixin:
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):

        return get_object_or_404(
            Comment,
            id=self.kwargs['comment_id'],
            post=self.kwargs['post_id'],
        )

    def get_success_url(self):

        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
