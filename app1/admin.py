from django.contrib import admin
from .models import Category, Carpet, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Carpet)
class CarpetAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'available', 'created']
    list_filter = ['available', 'created', 'updated', 'category']
    list_editable = ['price', 'stock', 'available']

# عرض المنتجات داخل صفحة الطلب
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['carpet']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'phone_number', 'city', 'status', 'created']
    list_filter = ['status', 'created', 'city']
    list_editable = ['status']
    inlines = [OrderItemInline]
