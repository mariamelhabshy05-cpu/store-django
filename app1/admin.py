# from django.contrib import admin
# from .models import Category, Carpet, Order, OrderItem
#
# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ['name', 'slug']
#     prepopulated_fields = {'slug': ('name',)}
#
# @admin.register(Carpet)
# class CarpetAdmin(admin.ModelAdmin):
#     list_display = ['name', 'category', 'price', 'stock', 'available', 'created']
#     list_filter = ['available', 'created', 'updated', 'category']
#     list_editable = ['price', 'stock', 'available']
#
# # عرض المنتجات داخل صفحة الطلب
# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     raw_id_fields = ['carpet']
#     extra = 0
#
# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['id', 'first_name', 'phone_number', 'city', 'status', 'created']
#     list_filter = ['status', 'created', 'city']
#     list_editable = ['status']
#     inlines = [OrderItemInline]
from django.contrib import admin
# التعديل هنا: استدعاء الدوال الصحيحة لدمج النصوص بأمان
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from .models import Category, Carpet, Order, OrderItem


# ==========================================
# 1. إدارة الأقسام
# ==========================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


# ==========================================
# 2. إدارة السجاد (المنتجات)
# ==========================================
@admin.register(Carpet)
class CarpetAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'available', 'created']
    list_filter = ['available', 'created', 'updated', 'category', 'material']
    list_editable = ['price', 'stock', 'available']
    search_fields = ['name', 'description']
    readonly_fields = ['created', 'updated']


# ==========================================
# 3. محتويات الطلب (السلة) داخل صفحة الطلب
# ==========================================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['carpet']
    extra = 0
    readonly_fields = ['get_subtotal']

    def get_subtotal(self, obj):
        if obj.price and obj.quantity:
            return obj.get_cost()
        return 0

    get_subtotal.short_description = 'الإجمالي الفرعي'


# ==========================================
# 4. إدارة الطلبات
# ==========================================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'phone_number', 'city', 'get_order_items', 'status', 'order_total',
                    'created']
    list_filter = ['status', 'created', 'city']
    list_editable = ['status']
    search_fields = ['first_name', 'last_name', 'phone_number', 'email', 'id']
    readonly_fields = ['created', 'updated']
    inlines = [OrderItemInline]

    fieldsets = (
        ('بيانات العميل', {
            'fields': ('first_name', 'last_name', 'phone_number', 'email')
        }),
        ('عنوان الشحن', {
            'fields': ('city', 'address')
        }),
        ('حالة وتفاصيل الطلب', {
            'fields': ('status', 'notes', 'created', 'updated')
        }),
    )

    def order_total(self, obj):
        return f"{obj.get_total_cost()} ج.م"

    order_total.short_description = 'إجمالي الطلب'

    # الدالة المصححة لجلب المنتجات بأمان
    def get_order_items(self, obj):
        items = obj.items.all()
        if not items:
            return "لا توجد منتجات"

        # استخدام format_html_join لطباعة كل منتج بشكل آمن ومنسق
        return format_html_join(
            mark_safe('<br>'),  # الفاصل بين المنتجات (سطر جديد)
            '• {} (الكمية: {})',  # شكل النص
            ((item.carpet.name, item.quantity) for item in items)  # البيانات
        )

    get_order_items.short_description = 'محتويات الطلب'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('items__carpet')