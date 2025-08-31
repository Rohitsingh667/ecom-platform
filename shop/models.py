from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.FloatField(default=0.0)
    popularity_score = models.FloatField(default=0.0)
    tags = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'available']),
            models.Index(fields=['created_at']),
            models.Index(fields=['popularity_score']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id}"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.product.price

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.price

class UserInteraction(models.Model):
    INTERACTION_CHOICES = [
        ('view', 'View'),
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('purchase', 'Purchase'),
        ('add_to_cart', 'Add to Cart'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['product', 'interaction_type']),
        ]

    def __str__(self):
        return f"{self.user} {self.interaction_type} {self.product}"
