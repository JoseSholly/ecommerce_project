from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
import random
from catalog.models import Category, Product  


class Command(BaseCommand):
    help = 'Create products with different categories using batch creation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--products',
            type=int,
            default=100,
            help='Number of products to create (default: 100)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Batch size for bulk creation (default: 50)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing products and categories before creating new ones'
        )

    def handle(self, *args, **options):
        products_count = options['products']
        batch_size = options['batch_size']
        clear_existing = options['clear']

        if clear_existing:
            self.stdout.write('Clearing existing products and categories...')
            Product.objects.all().delete()
            Category.objects.all().delete()

        # Create categories first
        self.stdout.write('Creating categories...')
        categories_data = [
            {
                'name': 'Electronics',
                'description': 'Electronic devices and gadgets'
            },
            {
                'name': 'Clothing',
                'description': 'Apparel and fashion items'
            },
            {
                'name': 'Books',
                'description': 'Books and educational materials'
            },
            {
                'name': 'Home & Garden',
                'description': 'Home improvement and garden supplies'
            },
            {
                'name': 'Sports & Fitness',
                'description': 'Sports equipment and fitness gear'
            },
            {
                'name': 'Beauty & Health',
                'description': 'Beauty products and health supplements'
            },
            {
                'name': 'Toys & Games',
                'description': 'Toys and entertainment products'
            },
            {
                'name': 'Food & Beverages',
                'description': 'Food items and beverages'
            }
        ]

        # Create categories using bulk_create
        categories_to_create = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                categories_to_create.append(category)

        categories = list(Category.objects.all())
        self.stdout.write(f'Created/Found {len(categories)} categories')

        # Sample product data for each category
        product_templates = {
            'Electronics': [
                'Smartphone', 'Laptop', 'Headphones', 'Smart Watch', 'Tablet',
                'Camera', 'Gaming Console', 'Smart TV', 'Bluetooth Speaker', 'Power Bank'
            ],
            'Clothing': [
                'T-Shirt', 'Jeans', 'Dress', 'Jacket', 'Sneakers',
                'Hoodie', 'Shorts', 'Blouse', 'Suit', 'Hat'
            ],
            'Books': [
                'Programming Guide', 'Novel', 'Cookbook', 'Biography', 'Science Textbook',
                'History Book', 'Self-Help Book', 'Children\'s Book', 'Dictionary', 'Art Book'
            ],
            'Home & Garden': [
                'Garden Tools', 'Lamp', 'Cushion', 'Plant Pot', 'Kitchen Utensils',
                'Vacuum Cleaner', 'Curtains', 'Carpet', 'Storage Box', 'Wall Clock'
            ],
            'Sports & Fitness': [
                'Running Shoes', 'Yoga Mat', 'Dumbbells', 'Tennis Racket', 'Basketball',
                'Fitness Tracker', 'Protein Powder', 'Water Bottle', 'Gym Bag', 'Resistance Bands'
            ],
            'Beauty & Health': [
                'Face Cream', 'Shampoo', 'Lipstick', 'Vitamins', 'Perfume',
                'Sunscreen', 'Hair Mask', 'Body Lotion', 'Essential Oil', 'Makeup Brush'
            ],
            'Toys & Games': [
                'Board Game', 'Action Figure', 'Puzzle', 'Building Blocks', 'Doll',
                'Remote Control Car', 'Video Game', 'Stuffed Animal', 'Art Supplies', 'Musical Toy'
            ],
            'Food & Beverages': [
                'Organic Honey', 'Coffee Beans', 'Green Tea', 'Chocolate', 'Olive Oil',
                'Pasta', 'Spices Set', 'Energy Drink', 'Protein Bar', 'Fruit Juice'
            ]
        }

        # Currency options
        currencies = ['USD', 'NGN', 'EUR', 'GBP']

        self.stdout.write(f'Creating {products_count} products in batches of {batch_size}...')

        products_created = 0
        
        with transaction.atomic():
            while products_created < products_count:
                current_batch_size = min(batch_size, products_count - products_created)
                products_batch = []

                for i in range(current_batch_size):
                    # Select random category
                    category = random.choice(categories)
                    
                    # Get product templates for this category
                    templates = product_templates.get(category.name, ['Generic Product'])
                    base_name = random.choice(templates)
                    
                    # Add variation to product name
                    variations = ['Pro', 'Premium', 'Deluxe', 'Standard', 'Mini', 'Max', 'Plus']
                    product_name = f"{base_name} {random.choice(variations)} {random.randint(1, 999)}"
                    
                    # Generate random price based on category
                    price_ranges = {
                        'Electronics': (50, 2000),
                        'Clothing': (10, 300),
                        'Books': (5, 50),
                        'Home & Garden': (15, 500),
                        'Sports & Fitness': (20, 400),
                        'Beauty & Health': (8, 150),
                        'Toys & Games': (5, 100),
                        'Food & Beverages': (3, 80)
                    }
                    
                    min_price, max_price = price_ranges.get(category.name, (10, 100))
                    price = Decimal(str(round(random.uniform(min_price, max_price), 2)))
                    
                    # Generate product description
                    descriptions = [
                        f"High-quality {base_name.lower()} perfect for daily use.",
                        f"Premium {base_name.lower()} with excellent features and durability.",
                        f"Professional-grade {base_name.lower()} for enthusiasts.",
                        f"Affordable {base_name.lower()} with great value for money.",
                        f"Latest model {base_name.lower()} with advanced technology."
                    ]
                    
                    product = Product(
                        name=product_name,
                        description=random.choice(descriptions),
                        price=price,
                        currency=random.choice(currencies),
                        image_url=f"https://example.com/images/{base_name.lower().replace(' ', '-')}-{i+1}.jpg",
                        stock_quantity=random.randint(0, 1000),
                        category=category
                    )
                    
                    products_batch.append(product)

                # Bulk create the batch
                Product.objects.bulk_create(products_batch)
                products_created += len(products_batch)
                
                self.stdout.write(f'Created {products_created}/{products_count} products...')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {products_created} products across {len(categories)} categories'
            )
        )

        # Display summary
        self.stdout.write('\nSummary by category:')
        for category in categories:
            count = category.products.count()
            self.stdout.write(f'  {category.name}: {count} products')