from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField( blank=True, null=True)
    start_date = models.DateField( blank=True, null=True)
    end_date = models.DateField( blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    contribution_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.amount}"
    
    def total_billed_amount(self):
        return self.billings.aggregate(total=models.Sum('amount'))['total'] or 0
    
    def contribution_amount(self):
        if self.amount and self.amount > 0:
            charge = (self.amount / 100) * 20
            out_charge = self.amount - charge
            percentage = self.contribution_percentage or 0
            return round((out_charge / 100) * percentage, 2)
        return 0

    def total_contribution_amount(self):
        return self.contribution_amount()
        
        


class ProjectBilling(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='billings')
    billing_date = models.DateField()
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    order_id = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.project.name} - {self.amount} on {self.billing_date}"
    
    def total_billed_amount(self):
        return self.project.billings.aggregate(total=models.Sum('amount'))['total'] or 0