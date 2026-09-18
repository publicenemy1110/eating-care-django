from django.contrib import admin

from .models import CustomQuestion, CustomTest


class CustomQuestionInline(admin.TabularInline):
    model = CustomQuestion
    extra = 1


@admin.register(CustomTest)
class CustomTestAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'answer_type', 'is_published', 'created_at')
    list_filter = ('is_published', 'answer_type')
    search_fields = ('title', 'author__username', 'author__email')
    prepopulated_fields = {'slug': ('title',)}
    inlines = (CustomQuestionInline,)


@admin.register(CustomQuestion)
class CustomQuestionAdmin(admin.ModelAdmin):

    list_display = ('test', 'order', 'text')
    list_filter = ('test',)
