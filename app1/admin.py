from django.contrib import admin
from .models import Category, Carpet, Order, OrderItem
# Register your models here.
admin.site.register(Category)
admin.site.register(Carpet)
admin.site.register(Order)
admin.site.register(OrderItem)



