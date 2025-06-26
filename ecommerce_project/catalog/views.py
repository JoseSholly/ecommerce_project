from django.views.generic import TemplateView # Import TemplateView
from django.db.models import Count, Sum, Avg, F
import json

from unfold.views import UnfoldModelAdminViewMixin # Import UnfoldMixin

from .models import Product, Category # Import your Django models

class AnalyticsDashboardView(UnfoldModelAdminViewMixin, TemplateView):
    # Required attributes for UnfoldModelAdminViewMixin
    title = "E-commerce Analytics Dashboard" # Custom page header title
    icon = "bar_chart" # Material Symbols icon name for the sidebar menu
    # permission_required is a tuple of permissions; for a dashboard view,
    # you typically want staff access. You can leave it empty if staff_member_required
    # decorator on the URL is enough, or define specific app/model permissions here.
    # For now, let's rely on admin_view, which implies staff access.
    permission_required = () 

    template_name = "admin/analytics_dashboard.html" # Path to your template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- 1. Overview Metrics (KPIs) ---
        total_products = Product.objects.count()
        products_in_stock = Product.objects.filter(stock_quantity__gt=0).count()
        products_out_of_stock = Product.objects.filter(stock_quantity=0).count()
        total_categories = Category.objects.count()

        # Handle cases where no products exist to prevent ZeroDivisionError or None
        if total_products > 0:
            average_product_price = Product.objects.aggregate(avg_price=Avg('price'))['avg_price'] or 0
            total_stock_value = Product.objects.annotate(
                item_value=F('price') * F('stock_quantity')
            ).aggregate(total=Sum('item_value'))['total'] or 0
        else:
            average_product_price = 0
            total_stock_value = 0

        # --- 2. Top/Bottom Lists ---
        top_expensive_products = Product.objects.order_by('-price')[:5]
        top_stocked_products = Product.objects.order_by('-stock_quantity')[:5]
        
        # Low stock: products between 1 and 10 in stock
        low_stock_products = Product.objects.filter(
            stock_quantity__gt=0, stock_quantity__lte=10
        ).order_by('stock_quantity')[:5]

        # Categories with most products
        categories_with_product_counts = Category.objects.annotate(
            product_count=Count('products')
        ).order_by('-product_count')[:5]

        # --- 3. Data for Charts ---
        # Product Count by Category for a bar chart
        category_product_counts = list(Category.objects.annotate(
            count=Count('products')
        ).order_by('name').values('name', 'count')) # Convert to list of dicts for JSON

        # Stock Distribution for a pie chart (In Stock vs. Out of Stock)
        stock_distribution_data = {
            'in_stock': products_in_stock,
            'out_of_stock': products_out_of_stock,
        }

        # Add all calculated data to the context
        context.update({
            # KPIs
            'total_products': total_products,
            'products_in_stock': products_in_stock,
            'products_out_of_stock': products_out_of_stock,
            'total_categories': total_categories,
            'average_product_price': average_product_price,
            'total_stock_value': total_stock_value,

            # Lists
            'top_expensive_products': top_expensive_products,
            'top_stocked_products': top_stocked_products,
            'low_stock_products': low_stock_products,
            'categories_with_product_counts': categories_with_product_counts,

            # Chart Data (JSON stringified for JavaScript)
            'category_chart_data_json': json.dumps(category_product_counts),
            'stock_distribution_data_json': json.dumps(stock_distribution_data),
        })

        return context