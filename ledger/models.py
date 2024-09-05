from django.db import models

class Ledger(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    LEDGER_CHOICES = [
        ('Given', 'Given'),
        ('Taken', 'Taken'),
    ]
    ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    type = models.CharField(max_length=10, choices=LEDGER_CHOICES)

    def __str__(self):
        return f"{self.ledger.name} - {self.amount} - {self.type}"
