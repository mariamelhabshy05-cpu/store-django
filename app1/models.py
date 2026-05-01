from django.db import models
from django.utils.translation import gettext_lazy as _


# التصنيف
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم التصنيف")
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = "تصنيف"
        verbose_name_plural = "التصنيفات"

    def __str__(self):
        return self.name


# المنتج
class Carpet(models.Model):
    category = models.ForeignKey(Category, related_name='carpets', on_delete=models.CASCADE, verbose_name="التصنيف")
    name = models.CharField(max_length=200, verbose_name="اسم السجادة")
    description = models.TextField(verbose_name="الوصف")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر")
    image_url = models.URLField(max_length=500, verbose_name="رابط صورة السجادة", blank=True, null=True)
    stock = models.PositiveIntegerField(default=10, verbose_name="الكمية المتاحة")

    length = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="الطول (بالمتر)", blank=True, null=True)
    width = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="العرض (بالمتر)", blank=True, null=True)
    material = models.CharField(max_length=100, verbose_name="الخامة", blank=True)

    available = models.BooleanField(default=True, verbose_name="متاح في المخزن")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "سجادة"
        verbose_name_plural = "السجاد"

    def __str__(self):
        return self.name


# الطلب
class Order(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'قيد الانتظار'),
        ('Processing', 'جاري التجهيز'),
        ('Shipped', 'تم الإرسال لشركة الشحن'),
        ('Delivered', 'تم التوصيل'),
        ('Cancelled', 'ملغي'),
    )

    # بيانات العميل
    first_name = models.CharField(max_length=50, verbose_name="الاسم الأول")
    last_name = models.CharField(max_length=50, verbose_name="الاسم الأخير")
    phone_number = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    email = models.EmailField(verbose_name="البريد الإلكتروني", blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name="المدينة / المحافظة")
    address = models.TextField(verbose_name="العنوان بالتفصيل")

    # بيانات الطلب
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الطلب")
    updated = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name="حالة الطلب")
    notes = models.TextField(verbose_name="ملاحظات إضافية من العميل", blank=True, null=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"

    def __str__(self):
        return f'طلب رقم {self.id}'

    def get_total_cost(self):
        # حساب التكلفة الإجمالية للطلب
        return sum(item.get_cost() for item in self.items.all())


# عناصر الطلب الي هتبقى في السلة
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="الطلب")
    carpet = models.ForeignKey(Carpet, related_name='order_items', on_delete=models.CASCADE, verbose_name="السجادة")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر وقت الشراء")
    quantity = models.PositiveIntegerField(default=1, verbose_name="الكمية")

    class Meta:
        verbose_name = "عنصر الطلب"
        verbose_name_plural = "عناصر الطلب"

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity
