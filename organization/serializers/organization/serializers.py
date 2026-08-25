from rest_framework import serializers
from django.db import transaction
from organization.models import Organization
from accounts.services import create_default_chart_of_accounts

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        organization = super().create(validated_data)
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        create_default_chart_of_accounts(organization, created_by=user)
        if user:
            from organization.models.organizationmembership import OrganizationMembership
            OrganizationMembership.objects.get_or_create(
                user=user,
                organization=organization,
                defaults={"is_owner": True, "is_active": True}
            )
            user.organization = organization
            user.save(update_fields=['organization'])
        return organization