from django.urls import include, path

from . import views

app_name = 'blog'

post_urls = [
    path(
        'create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        '<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        '<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        '<int:post_id>/edit/',
        views.edit_post,
        name='edit_post'
    ),
]

profile_urls = [
    path(
        'edit/',
        views.edit_profile,
        name='edit_profile'
    ),
    path(
        '<slug:username>/',
        views.profile_user,
        name='profile'
    ),
]

comment_urls = [
    path(
        '',
        views.add_comment,
        name='add_comment'
    ),
    path(
        '<int:comment_id>/edit_comment/',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        '<int:comment_id>/delete_comment/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
]

urlpatterns = [
    path(
        '',
        views.PostListView.as_view(),
        name='index'
    ),
    path('posts/', include(post_urls)),
    path('profile/', include(profile_urls)),
    path('posts/<int:post_id>/comments/', include(comment_urls)),
    path(
        'category/<str:category_slug>/',
        views.category_posts,
        name='category_posts'
    ),


]
