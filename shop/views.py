from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Product, Category, Cart, CartItem, Order, OrderItem, UserInteraction
from recommendations.ml_engine import get_recommendations
from django.shortcuts import render, get_object_or_404, redirect
import json

def product_list(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    
    selected_category = None
    category_slug = request.GET.get('category')
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)
    
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(tags__icontains=query)
        )
    
    recommendations = []
    if request.user.is_authenticated:
        recommendations = get_recommendations(request.user, limit=4)
    
    context = {
        'products': products,
        'categories': categories,
        'recommendations': recommendations,
        'query': query,
        'current_category': category_slug,
        'selected_category': selected_category,
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    
    if request.user.is_authenticated:
        UserInteraction.objects.create(
            user=request.user,
            product=product,
            interaction_type='view',
            session_key=request.session.session_key
        )
    
    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(id=product.id)[:4]
    
    recommendations = []
    if request.user.is_authenticated:
        recommendations = get_recommendations(request.user, limit=4)
    
    context = {
        'product': product,
        'related_products': related_products,
        'recommendations': recommendations,
    }
    return render(request, 'shop/product_detail.html', context)

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    cart = get_or_create_cart(request)
    
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    if request.user.is_authenticated:
        UserInteraction.objects.create(
            user=request.user,
            product=product,
            interaction_type='add_to_cart',
            session_key=request.session.session_key
        )
    
    messages.success(request, f'{product.name} added to cart!')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': cart.get_total_items(),
            'message': f'{product.name} added to cart!'
        })
    
    return redirect('shop:product_detail', slug=product.slug)

def cart_detail(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'shop/cart_detail.html', context)

@require_POST
def update_cart_item(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': cart.get_total_items(),
            'cart_price': str(cart.get_total_price())
        })
    
    return redirect('shop:cart_detail')

@require_POST
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    
    messages.success(request, f'{cart_item.product.name} removed from cart!')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': cart.get_total_items(),
            'cart_price': str(cart.get_total_price())
        })
    
    return redirect('shop:cart_detail')

@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()
    
    if not cart_items:
        messages.error(request, 'Your cart is empty!')
        return redirect('shop:cart_detail')
    
    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            total_amount=cart.get_total_price(),
            shipping_address=request.POST['shipping_address'],
            phone_number=request.POST['phone_number'],
            email=request.POST['email'],
        )
        
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            
            UserInteraction.objects.create(
                user=request.user,
                product=cart_item.product,
                interaction_type='purchase',
                session_key=request.session.session_key
            )
        
        cart.items.all().delete()
        
        messages.success(request, f'Order {order.id} placed successfully!')
        return redirect('shop:order_success', order_id=order.id)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'shop/checkout.html', context)

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'shop/order_success.html', context)

@csrf_exempt
@require_POST
def product_feedback(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    product = get_object_or_404(Product, id=product_id)
    data = json.loads(request.body)
    feedback_type = data.get('type')
    
    if feedback_type not in ['like', 'dislike']:
        return JsonResponse({'error': 'Invalid feedback type'}, status=400)
    
    UserInteraction.objects.filter(
        user=request.user,
        product=product,
        interaction_type__in=['like', 'dislike']
    ).delete()
    
    UserInteraction.objects.create(
        user=request.user,
        product=product,
        interaction_type=feedback_type,
        session_key=request.session.session_key
    )
    
    return JsonResponse({'success': True, 'message': f'Product {feedback_type}d!'})
