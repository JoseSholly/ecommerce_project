from django.contrib import admin
from .models import Category, Product
from unfold.admin import ModelAdmin
@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('name', 'price', 'category', 'stock_quantity', 'created_at')
    list_filter = ('category', 'currency')
    search_fields = ('name', 'description')
    raw_id_fields = ('category',) 