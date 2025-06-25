from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories" # Fixes admin pluralization

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD') # e.g., 'USD', 'NGN'
    image_url = models.URLField(blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL, # Products stay if category is deleted, but category becomes null
        related_name='products', # Allows category.products.all()
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name