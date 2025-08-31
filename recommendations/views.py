from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .ml_engine import get_recommendations, retrain_models, recommendation_engine
from shop.models import Product

@login_required
@api_view(['GET'])
def get_user_recommendations(request):
    algorithm = request.GET.get('algorithm', 'hybrid')
    limit = int(request.GET.get('limit', 10))
    
    recommendations = get_recommendations(request.user, algorithm, limit)
    
    products_data = []
    for product in recommendations:
        products_data.append({
            'id': str(product.id),
            'name': product.name,
            'slug': product.slug,
            'price': str(product.price),
            'description': product.description[:100] + '...' if len(product.description) > 100 else product.description,
            'category': product.category.name,
            'rating': product.rating,
            'image_url': product.image.url if product.image else None,
            'url': product.get_absolute_url(),
        })
    
    return Response({
        'recommendations': products_data,
        'algorithm_used': algorithm,
        'count': len(products_data)
    })

@api_view(['POST'])
@csrf_exempt
def retrain_recommendation_models(request):
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, status=403)
    
    try:
        retrain_models()
        return Response({'message': 'Models retrained successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def recommendation_stats(request):
    from shop.models import UserInteraction
    from .models import RecommendationHistory
    
    stats = {
        'total_interactions': UserInteraction.objects.count(),
        'total_recommendations_generated': RecommendationHistory.objects.count(),
        'unique_users_with_recommendations': RecommendationHistory.objects.values('user').distinct().count(),
        'algorithms_used': list(RecommendationHistory.objects.values_list('algorithm_used', flat=True).distinct()),
    }
    
    interaction_breakdown = {}
    for interaction_type in ['view', 'like', 'dislike', 'add_to_cart', 'purchase']:
        count = UserInteraction.objects.filter(interaction_type=interaction_type).count()
        interaction_breakdown[interaction_type] = count
    
    stats['interaction_breakdown'] = interaction_breakdown
    
    return Response(stats)

@login_required
@api_view(['GET'])
def user_recommendation_history(request):
    from .models import RecommendationHistory
    
    history = RecommendationHistory.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    history_data = []
    for record in history:
        products = record.recommended_products.all()[:5]
        history_data.append({
            'id': record.id,
            'algorithm_used': record.algorithm_used,
            'created_at': record.created_at.isoformat(),
            'products_count': record.recommended_products.count(),
            'sample_products': [
                {
                    'id': str(p.id),
                    'name': p.name,
                    'price': str(p.price)
                } for p in products
            ]
        })
    
    return Response({'history': history_data})

@api_view(['GET'])
def similar_products(request, product_id):
    try:
        product = Product.objects.get(id=product_id, available=True)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)
    
    if recommendation_engine.product_features is not None:
        product_id_str = str(product.id)
        if product_id_str in recommendation_engine.product_features.index:
            similar_scores = recommendation_engine.product_features.loc[product_id_str].sort_values(ascending=False)
            similar_product_ids = similar_scores.index[1:11]
            
            similar_products = Product.objects.filter(
                id__in=[pid for pid in similar_product_ids],
                available=True
            )[:5]
        else:
            similar_products = Product.objects.filter(
                category=product.category,
                available=True
            ).exclude(id=product.id)[:5]
    else:
        similar_products = Product.objects.filter(
            category=product.category,
            available=True
        ).exclude(id=product.id)[:5]
    
    products_data = []
    for p in similar_products:
        products_data.append({
            'id': str(p.id),
            'name': p.name,
            'slug': p.slug,
            'price': str(p.price),
            'description': p.description[:100] + '...' if len(p.description) > 100 else p.description,
            'category': p.category.name,
            'rating': p.rating,
            'image_url': p.image.url if p.image else None,
            'url': p.get_absolute_url(),
        })
    
    return Response({
        'similar_products': products_data,
        'base_product': {
            'id': str(product.id),
            'name': product.name,
            'category': product.category.name
        }
    })
