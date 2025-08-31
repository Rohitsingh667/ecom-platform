from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('recommendations/', views.get_user_recommendations, name='get_recommendations'),
    path('retrain/', views.retrain_recommendation_models, name='retrain_models'),
    path('stats/', views.recommendation_stats, name='stats'),
    path('history/', views.user_recommendation_history, name='history'),
    path('similar/<uuid:product_id>/', views.similar_products, name='similar_products'),
]
