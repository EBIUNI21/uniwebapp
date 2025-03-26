from django.contrib import admin
from petpals.models import UserProfile, Category, Page

admin.site.register(UserProfile)

class PageAdmin (admin.ModelAdmin):
    list_display = ('title', 'category', 'url')

admin.site.register(Page, PageAdmin)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
admin.site.register(Category, CategoryAdmin)