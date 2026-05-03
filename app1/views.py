from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Category, Carpet, Order, OrderItem
from .forms import CartAddProductForm, OrderCreateForm



# 1. كلاس السلة (Cart Session)

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, carpet, quantity=1, override_quantity=False):
        carpet_id = str(carpet.id)
        if carpet_id not in self.cart:
            self.cart[carpet_id] = {'quantity': 0, 'price': str(carpet.price)}
        if override_quantity:
            self.cart[carpet_id]['quantity'] = quantity
        else:
            self.cart[carpet_id]['quantity'] += quantity
        self.save()

    def remove(self, carpet):
        carpet_id = str(carpet.id)
        if carpet_id in self.cart:
            del self.cart[carpet_id]
            self.save()

    def clear(self):
        del self.session['cart']
        self.save()

    def save(self):
        self.session.modified = True

    def get_items(self):
        carpet_ids = self.cart.keys()
        carpets = Carpet.objects.filter(id__in=carpet_ids)
        cart_items = self.cart.copy()
        for carpet in carpets:
            cart_items[str(carpet.id)]['carpet'] = carpet
        return cart_items.values()

    def get_total_price(self):
        return sum(float(item['price']) * item['quantity'] for item in self.cart.values())


# ==========================================
# 2. عرض المنتجات (Shop Views)
# ==========================================
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    # جلب السجاد المتاح في المخزن فقط كبداية
    carpets = Carpet.objects.filter(available=True)

    # ==========================================
    # --- كود الفلترة الجديد ---
    # ==========================================
    search_query = request.GET.get('q')  # للبحث بالاسم
    min_price = request.GET.get('min_price')  # الحد الأدنى للسعر
    max_price = request.GET.get('max_price')  # الحد الأقصى للسعر

    # 1. الفلترة بكلمة البحث (إذا كتب العميل اسم السجادة)
    if search_query:
        carpets = carpets.filter(name__icontains=search_query)

    # 2. الفلترة بالحد الأدنى للسعر
    if min_price:
        carpets = carpets.filter(price__gte=min_price)

    # 3. الفلترة بالحد الأقصى للسعر
    if max_price:
        carpets = carpets.filter(price__lte=max_price)
    # ==========================================

    # الفلترة بال Category
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        carpets = carpets.filter(category=category)

    return render(request, 'HtmlPages/home.html', {
        'category': category,
        'categories': categories,
        'carpets': carpets
    })

def product_detail(request, id):
    carpet = get_object_or_404(Carpet, id=id, available=True)
    cart_product_form = CartAddProductForm()
    return render(request, 'HtmlPages/home.html', {
        'carpet': carpet,
        'cart_product_form': cart_product_form
    })



# 3. إدارة السلة (Cart Views)

@require_POST
def cart_add(request, carpet_id):
    cart = Cart(request)
    carpet = get_object_or_404(Carpet, id=carpet_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(carpet=carpet, quantity=cd['quantity'], override_quantity=cd['override'])
    return redirect('cart_detail')


def cart_remove(request, carpet_id):
    cart = Cart(request)
    carpet = get_object_or_404(Carpet, id=carpet_id)
    cart.remove(carpet)
    return redirect('cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})



# 4. الطلبات وإلغاء الطلب (Order Views)

def order_create(request):
    cart = Cart(request)
    if not cart.cart:
        return redirect('cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart.get_items():
                OrderItem.objects.create(
                    order=order,
                    carpet=item['carpet'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            cart.clear()


            request.session['last_order_id'] = order.id

            return render(request, 'orders/order_success.html', {'order': order})
    else:
        form = OrderCreateForm()

    return render(request, 'orders/order_create.html', {'cart': cart, 'form': form})


def order_cancel(request, order_id):
    # جلب الطلب
    order = get_object_or_404(Order, id=order_id)

    # التأكد أن من يطلب الإلغاء هو نفس المتصفح الذي قام بالطلب (أمان)
    if request.session.get('last_order_id') == order.id:
        # لا يمكنه الإلغاء إلا إذا كان الطلب لسه قيد الانتظار أو التجهيز
        if order.status in ['Pending', 'Processing']:
            order.status = 'Cancelled'
            order.save()
            # إرسال رسالة نجاح تظهر في الـ HTML
            messages.success(request, "تم إلغاء طلبك بنجاح.")
        else:
            messages.error(request, "عذراً، لا يمكن إلغاء الطلب لأنه تم شحنه بالفعل.")
    else:
        messages.error(request, "غير مصرح لك بإلغاء هذا الطلب.")

    # توجيه العميل للصفحة الرئيسية أو لصفحة نجاح الإلغاء
    return redirect('product_list')
