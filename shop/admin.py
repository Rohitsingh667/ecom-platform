from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem, UserInteraction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_inr', 'stock', 'available', 'rating', 'popularity_score']
    list_filter = ['available', 'category', 'created_at']
    list_editable = ['stock', 'available', 'rating']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    def price_inr(self, obj):
        return f"₹{obj.price}"
    price_inr.short_description = "Price (INR)"

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'get_total_items', 'get_total_price_inr']
    list_filter = ['created_at']
    inlines = [CartItemInline]

    def get_total_price_inr(self, obj):
        return f"₹{obj.get_total_price()}"
    get_total_price_inr.short_description = "Total Price (INR)"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_amount_inr', 'created_at']
    list_filter = ['status', 'created_at']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]

    def total_amount_inr(self, obj):
        return f"₹{obj.total_amount}"
    total_amount_inr.short_description = "Total Amount (INR)"

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'interaction_type', 'timestamp']
    list_filter = ['interaction_type', 'timestamp']
    readonly_fields = ['timestamp']
