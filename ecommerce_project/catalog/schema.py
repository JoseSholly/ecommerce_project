import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q # For advanced filtering

from .models import Category, Product

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = "__all__" # Expose all fields from the Django model

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__" # Expose all fields from the Django model

class Query(graphene.ObjectType):
    # Query for a single product by ID
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    # Query for all products with optional filters
    products = graphene.List(
        ProductType,
        category_id=graphene.ID(),
        min_price=graphene.Float(),
        max_price=graphene.Float(),
        search=graphene.String(), 
        order_by=graphene.String(),
    )

    # Query for a single category by ID
    category = graphene.Field(CategoryType, id=graphene.ID(required=True))
    # Query for all categories
    categories = graphene.List(CategoryType)

    def resolve_product(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None

    def resolve_products(self, info, category_id=None, min_price=None, max_price=None, search=None, order_by=None):
        queryset = Product.objects.all()

        if category_id:
            queryset = queryset.filter(category__id=category_id)
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        if order_by:
            # Basic ordering, can be extended for ascending/descending
            queryset = queryset.order_by(order_by)

        return queryset

    def resolve_category(self, info, id):
        try:
            return Category.objects.get(pk=id)
        except Category.DoesNotExist:
            return None

    def resolve_categories(self, info):
        return Category.objects.all()

# --- Mutation Types (for Create, Update, Delete) ---

class CreateCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()

    category = graphene.Field(CategoryType)

    def mutate(self, info, name, description=None):
        category = Category(name=name, description=description)
        category.save()
        return CreateCategory(category=category)

class UpdateCategory(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        description = graphene.String()

    category = graphene.Field(CategoryType)

    def mutate(self, info, id, name=None, description=None):
        try:
            category = Category.objects.get(pk=id)
            if name is not None:
                category.name = name
            if description is not None:
                category.description = description
            category.save()
            return UpdateCategory(category=category)
        except Category.DoesNotExist:
            return None

class DeleteCategory(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            category = Category.objects.get(pk=id)
            category.delete()
            return DeleteCategory(ok=True)
        except Category.DoesNotExist:
            return DeleteCategory(ok=False)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        price = graphene.Float(required=True)
        currency = graphene.String(required=True)
        image_url = graphene.String()
        stock_quantity = graphene.Int()
        category_id = graphene.ID(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, description, price, currency, image_url=None, stock_quantity=0, category_id=None):
        try:
            category = Category.objects.get(pk=category_id)
            product = Product(
                name=name,
                description=description,
                price=price,
                currency=currency,
                image_url=image_url,
                stock_quantity=stock_quantity,
                category=category
            )
            product.save()
            return CreateProduct(product=product)
        except Category.DoesNotExist:
            raise Exception("Category not found.")

class UpdateProduct(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        description = graphene.String()
        price = graphene.Float()
        currency = graphene.String()
        image_url = graphene.String()
        stock_quantity = graphene.Int()
        category_id = graphene.ID()

    product = graphene.Field(ProductType)

    def mutate(self, info, id, **kwargs):
        try:
            product = Product.objects.get(pk=id)
            if 'category_id' in kwargs:
                try:
                    category = Category.objects.get(pk=kwargs.pop('category_id'))
                    product.category = category
                except Category.DoesNotExist:
                    raise Exception("Category not found.")

            for field, value in kwargs.items():
                setattr(product, field, value)
            product.save()
            return UpdateProduct(product=product)
        except Product.DoesNotExist:
            return None

class DeleteProduct(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            product = Product.objects.get(pk=id)
            product.delete()
            return DeleteProduct(ok=True)
        except Product.DoesNotExist:
            return DeleteProduct(ok=False)


class Mutation(graphene.ObjectType):
    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()

    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)