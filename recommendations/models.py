from django.db import models
from django.contrib.auth.models import User
from shop.models import Product

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

class RecommendationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendation_history')
    recommended_products = models.ManyToManyField(Product, related_name='recommendation_history')
    algorithm_used = models.CharField(max_length=50, default='collaborative_filtering')
    created_at = models.DateTimeField(auto_now_add=True)
    accuracy_score = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Recommendations for {self.user.username} at {self.created_at}"
