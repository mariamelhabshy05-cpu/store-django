from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # 0. الصفحة الرئيسية للموقع
    path('home/', views.home, name='home'),

    # 1. عرض المنتجات
    path('products/', views.product_list, name='product_list'), #تعرض كل السجاد
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'), # الفلترة
    path('product/<int:id>/', views.product_detail, name='product_detail'), # صفحة تفاصيل سجادة واحدة

    # 2. روابط سلة المشتريات
    path('cart/', views.cart_detail, name='cart_detail'), # صفحة عرض السلة
    path('cart/add/<int:carpet_id>/', views.cart_add, name='cart_add'), # رابط مخفي لإضافة منتج
    path('cart/remove/<int:carpet_id>/', views.cart_remove, name='cart_remove'), # رابط مخفي لحذف منتج

    # 3. روابط الطلبات والدفع
    path('checkout/', views.order_create, name='order_create'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)