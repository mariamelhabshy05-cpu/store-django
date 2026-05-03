from django.urls import path
from . import views


app_name = 'app1'

urlpatterns = [
    # 1. عرض السجاد
    path('', views.product_list, name='product_list'), # الصفحة الرئيسية (تعرض كل السجاد)
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'), # عرض قسم معين
    path('product/<int:id>/', views.product_detail, name='product_detail'), # صفحة تفاصيل سجادة واحدة

    # 2. روابط سلة المشتريات
    path('cart/', views.cart_detail, name='cart_detail'), # صفحة عرض السلة
    path('cart/add/<int:carpet_id>/', views.cart_add, name='cart_add'), # رابط مخفي لإضافة منتج
    path('cart/remove/<int:carpet_id>/', views.cart_remove, name='cart_remove'), # رابط مخفي لحذف منتج

    # 3. روابط الطلبات والدفع
    path('checkout/', views.order_create, name='order_create'), # صفحة إتمام الطلب (الدفع)
    path('order/cancel/<int:order_id>/', views.order_cancel, name='order_cancel'), # رابط إلغاء الطلب
]
