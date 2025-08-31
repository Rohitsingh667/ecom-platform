import numpy as np
import pandas as pd
from django.contrib.auth.models import User
from django.db.models import Count
from shop.models import Product, UserInteraction
from .models import UserProfile, RecommendationHistory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from typing import List

try:
    from .fast_similarity import cosine_similarity_optimized as cython_cosine
    CYTHON_SIM_AVAILABLE = True
except Exception:
    CYTHON_SIM_AVAILABLE = False

class RecommendationEngine:
    
    def __init__(self):
        self.user_item_matrix = None
        self.svd_model = None
        self.product_features = None
        self.tfidf_vectorizer = None
        self.content_similarity_matrix = None
        
    def prepare_user_item_matrix(self) -> np.ndarray:
        interactions = UserInteraction.objects.select_related('user', 'product').all()
        
        interaction_weights = {
            'view': 1.0,
            'like': 3.0,
            'dislike': -2.0,
            'add_to_cart': 2.0,
            'purchase': 5.0
        }
        
        user_product_scores = {}
        for interaction in interactions:
            user_id = interaction.user.id
            product_id = str(interaction.product.id)
            weight = interaction_weights.get(interaction.interaction_type, 1.0)
            
            key = (user_id, product_id)
            if key in user_product_scores:
                user_product_scores[key] += weight
            else:
                user_product_scores[key] = weight
        
        data = []
        for (user_id, product_id), score in user_product_scores.items():
            data.append({'user_id': user_id, 'product_id': product_id, 'score': score})
        
        if not data:
            return None
            
        df = pd.DataFrame(data)
        
        user_item_matrix = df.pivot_table(
            index='user_id', 
            columns='product_id', 
            values='score', 
            fill_value=0
        )
        
        self.user_item_matrix = user_item_matrix
        return user_item_matrix.values
    
    def train_collaborative_filtering(self, n_components: int = 50):
        matrix = self.prepare_user_item_matrix()
        if matrix is None:
            return
            
        self.svd_model = TruncatedSVD(n_components=min(n_components, matrix.shape[1]-1))
        self.svd_model.fit(matrix)
    
    def prepare_content_features(self):
        products = Product.objects.filter(available=True)
        
        product_features = []
        product_ids = []
        
        for product in products:
            features = f"{product.name} {product.description} {product.category.name} {product.tags}"
            product_features.append(features)
            product_ids.append(str(product.id))
        
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(product_features)
        
        if CYTHON_SIM_AVAILABLE:
            dense = tfidf_matrix.toarray().astype(np.float64, copy=False)
            self.content_similarity_matrix = cython_cosine(dense)
        else:
            self.content_similarity_matrix = cosine_similarity(tfidf_matrix)
        
        self.product_features = pd.DataFrame(
            self.content_similarity_matrix,
            index=product_ids,
            columns=product_ids
        )
    
    def get_collaborative_recommendations(self, user: User, n_recommendations: int = 10) -> List[Product]:
        if self.user_item_matrix is None or self.svd_model is None:
            return []
            
        if user.id not in self.user_item_matrix.index:
            return self.get_popular_products(n_recommendations)
        
        user_idx = list(self.user_item_matrix.index).index(user.id)
        
        user_vector = self.user_item_matrix.iloc[user_idx:user_idx+1].values
        user_transformed = self.svd_model.transform(user_vector)
        
        all_products_transformed = self.svd_model.transform(self.user_item_matrix.values)
        
        similarities = cosine_similarity(user_transformed, all_products_transformed)[0]
        
        similar_user_indices = np.argsort(similarities)[::-1][1:21]
        
        product_scores = {}
        user_products = set(self.user_item_matrix.columns[self.user_item_matrix.iloc[user_idx] > 0])
        
        for similar_user_idx in similar_user_indices:
            similar_user_products = self.user_item_matrix.iloc[similar_user_idx]
            similarity_score = similarities[similar_user_idx]
            
            for product_id, score in similar_user_products.items():
                if score > 0 and product_id not in user_products:
                    if product_id not in product_scores:
                        product_scores[product_id] = 0
                    product_scores[product_id] += score * similarity_score
        
        top_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
        
        product_ids = [product_id for product_id, _ in top_products]
        return Product.objects.filter(id__in=product_ids, available=True)[:n_recommendations]
    
    def get_content_based_recommendations(self, user: User, n_recommendations: int = 10) -> List[Product]:
        if self.product_features is None:
            return []
        
        user_interactions = UserInteraction.objects.filter(
            user=user,
            interaction_type__in=['like', 'purchase', 'add_to_cart']
        ).select_related('product')
        
        if not user_interactions.exists():
            return self.get_popular_products(n_recommendations)
        
        product_scores = {}
        user_product_ids = set()
        
        for interaction in user_interactions:
            product_id = str(interaction.product.id)
            user_product_ids.add(product_id)
            
            if product_id in self.product_features.index:
                similar_products = self.product_features.loc[product_id].sort_values(ascending=False)
                
                for similar_product_id, similarity in similar_products.items():
                    if similar_product_id != product_id and similar_product_id not in user_product_ids:
                        if similar_product_id not in product_scores:
                            product_scores[similar_product_id] = 0
                        product_scores[similar_product_id] += similarity
        
        top_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
        
        product_ids = [product_id for product_id, _ in top_products]
        return Product.objects.filter(id__in=product_ids, available=True)[:n_recommendations]
    
    def get_popular_products(self, n_recommendations: int = 10) -> List[Product]:
        return Product.objects.filter(available=True).annotate(
            interaction_count=Count('interactions')
        ).order_by('-popularity_score', '-rating', '-interaction_count')[:n_recommendations]
    
    def get_hybrid_recommendations(self, user: User, n_recommendations: int = 10) -> List[Product]:
        collab_recs = self.get_collaborative_recommendations(user, n_recommendations * 2)
        content_recs = self.get_content_based_recommendations(user, n_recommendations * 2)
        popular_recs = self.get_popular_products(n_recommendations)
        
        product_scores = {}
        
        for i, product in enumerate(collab_recs):
            score = (len(collab_recs) - i) * 0.4
            if product.id not in product_scores:
                product_scores[product.id] = 0
            product_scores[product.id] += score
        
        for i, product in enumerate(content_recs):
            score = (len(content_recs) - i) * 0.4
            if product.id not in product_scores:
                product_scores[product.id] = 0
            product_scores[product.id] += score
        
        for i, product in enumerate(popular_recs):
            score = (len(popular_recs) - i) * 0.2
            if product.id not in product_scores:
                product_scores[product.id] = 0
            product_scores[product.id] += score
        
        top_product_ids = sorted(product_scores.keys(), key=lambda x: product_scores[x], reverse=True)
        
        products = []
        for product_id in top_product_ids[:n_recommendations]:
            try:
                product = Product.objects.get(id=product_id, available=True)
                products.append(product)
            except Product.DoesNotExist:
                continue
        
        return products
    
    def train_models(self):
        self.train_collaborative_filtering()
        self.prepare_content_features()

recommendation_engine = RecommendationEngine()

def get_recommendations(user: User, algorithm: str = 'hybrid', limit: int = 10) -> List[Product]:
    try:
        if algorithm == 'collaborative':
            recommendations = recommendation_engine.get_collaborative_recommendations(user, limit)
        elif algorithm == 'content':
            recommendations = recommendation_engine.get_content_based_recommendations(user, limit)
        elif algorithm == 'popular':
            recommendations = recommendation_engine.get_popular_products(limit)
        else:
            recommendations = recommendation_engine.get_hybrid_recommendations(user, limit)
        
        if recommendations:
            history = RecommendationHistory.objects.create(
                user=user,
                algorithm_used=algorithm
            )
            history.recommended_products.set(recommendations)
        
        return recommendations
        
    except Exception as e:
        return recommendation_engine.get_popular_products(limit)

def retrain_models():
    recommendation_engine.train_models()
