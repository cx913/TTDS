from django.contrib import admin

# Register your models here.
from .models import Recipe, TokenData


admin.site.register(Recipe)
admin.site.register(TokenData)
