import uuid

from django.conf import settings
from django.db import models


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    METHOD_CHOICES = [
        ('card', 'Credit / Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('credits_purchase', 'Credits Purchase'),
        ('subscription', 'Subscription'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    reference = models.CharField(max_length=40, unique=True, default=uuid.uuid4)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='card')
    description = models.CharField(max_length=255, blank=True)
    credits_awarded = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reference} - {self.user.username} - ${self.amount}'


class CreditPackage(models.Model):
    """Purchasable credit bundles shown on the Credits page."""

    name = models.CharField(max_length=50)
    credits = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_popular = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f'{self.name} - {self.credits} credits (${self.price})'
