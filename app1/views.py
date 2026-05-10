from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Category, Carpet, Order, OrderItem
from .forms import CartAddProductForm, OrderCreateForm



# ==========================================
# 0. الصفحة الرئيسية (Home View)
# ==========================================
def home(request):
    # جلب أحدث 4 سجادات متاحة لعرضها في قسم "الأكثر مبيعاً" في الصفحة الرئيسية
    featured_carpets = Carpet.objects.filter(available=True)[:4]

    return render(request, 'shop/home.html', {
        'carpets': featured_carpets
    })


# كلاس السلة
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
            # هذا هو السطر الجديد لحساب مجموع سعر السجادة الواحدة حسب كميتها
            cart_items[str(carpet.id)]['total_price'] = float(cart_items[str(carpet.id)]['price']) * cart_items[str(carpet.id)]['quantity']
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

    # --- كود الفلترة ---
    search_query = request.GET.get('q')  # للبحث بالاسم
    min_price = request.GET.get('min_price')  # الحد الأدنى للسعر
    max_price = request.GET.get('max_price')  # الحد الأقصى للسعر

    if search_query:
        carpets = carpets.filter(name__icontains=search_query)
    if min_price:
        carpets = carpets.filter(price__gte=min_price)
    if max_price:
        carpets = carpets.filter(price__lte=max_price)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        carpets = carpets.filter(category=category)

    return render(request, 'shop/product_list.html', {
        'category': category,
        'categories': categories,
        'carpets': carpets
    })


def product_detail(request, id):
    carpet = get_object_or_404(Carpet, id=id, available=True)

    cart_product_form = CartAddProductForm()

    related_products = Carpet.objects.filter(category=carpet.category, available=True).exclude(id=carpet.id)[:4]

    return render(request, 'shop/product_detail.html', {
        'carpet': carpet,
        'cart_product_form': cart_product_form,
        'related_products': related_products
    })



# ==========================================
# 3. إدارة السلة (Cart Views)
# ==========================================
@require_POST
def cart_add(request, carpet_id):
    cart = Cart(request)
    carpet = get_object_or_404(Carpet, id=carpet_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        desired_quantity = cd['quantity']
        is_override = cd['override']

        current_qty_in_cart = cart.cart.get(str(carpet_id), {}).get('quantity', 0)

        if is_override:
            total_requested = desired_quantity
        else:
            total_requested = current_qty_in_cart + desired_quantity

        if total_requested > carpet.stock:
            if carpet.stock == 0:
                messages.error(request, f"عذراً، المنتج '{carpet.name}' قد نفذ من المخزن حالياً.")
            else:
                messages.error(request,
                               f"عذراً، أقصى كمية متاحة من '{carpet.name}' هي {carpet.stock}. (لديك {current_qty_in_cart} في السلة)")
        else:
            cart.add(carpet=carpet, quantity=desired_quantity, override_quantity=is_override)
            messages.success(request, f"تم تحديث السلة بنجاح.")

    return redirect('cart_detail')



def cart_remove(request, carpet_id):
    cart = Cart(request)
    carpet = get_object_or_404(Carpet, id=carpet_id)
    cart.remove(carpet)
    messages.success(request, "تم حذف المنتج من السلة.")
    return redirect('cart_detail')


def cart_detail(request):
    cart = Cart(request)
    cart_items = cart.get_items()

    for item in cart_items:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })

    return render(request, 'cart/cart_detail.html', {'cart': cart, 'cart_items': cart_items})


# ==========================================
# 4. الطلبات (Order Views)
# ==========================================
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
            # تفريغ السلة بعد إتمام الطلب
            cart.clear()

            return render(request, 'orders/order_success.html', {'order': order})
    else:
        form = OrderCreateForm()

    return render(request, 'orders/order_create.html', {'cart': cart, 'form': form})