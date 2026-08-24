from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='organization_logos/', null=True, blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    tin = models.CharField(max_length=100, null=True, blank=True)
    bin = models.CharField(max_length=100, null=True, blank=True)
    trade_license = models.CharField(max_length=100, null=True, blank=True)
    vat_registration_number = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name