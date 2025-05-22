from django.db import models
from subscribe.entity.subscribe import Subscribe
from orders.entity.orders import Orders


class OrderItems(models.Model):
    id = models.AutoField(primary_key=True)
    orders = models.ForeignKey(Orders, related_name="items", on_delete=models.PROTECT)
    plan = models.ForeignKey(Subscribe, related_name="items", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Item: {self.quantity} x {self.price}"

    class Meta:
        db_table = 'orders_items'
        app_label = 'orders'
