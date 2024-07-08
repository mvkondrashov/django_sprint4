from django.contrib import admin

from .models import Category, Location, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published'
    )
    list_editable = (
        'pub_date',
        'author',
        'category',
        'location',
        'is_published'
    )
    search_fields = ('title', 'text',)
    list_filter = ('author', 'category', 'location', 'is_published')
    list_display_links = ('title',)


admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Post, PostAdmin)
