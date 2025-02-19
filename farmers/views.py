from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .models import Farmer
from django.db.models import Q
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import Product, CartItem, Order, Review
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from django.core.mail import send_mail
from django.db.models import Count, Sum, Avg



def farmer_list(request):
    farmers = Farmer.objects.all()
    return render(request, 'farmers/farmer_list.html', {'farmers': farmers})

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to the login page
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

def farmer_search(request):
    query = request.GET.get('q', '')
    farmers = Farmer.objects.filter(
        Q(farm_name__icontains=query) |
        Q(location__icontains=query) |
        Q(category__icontains=query)
    )
    return render(request, 'farmers/search_results.html', {'farmers': farmers, 'query': query})

def track_order(request):
    order_id = request.GET.get('order_id', '')
    order = Order.objects.filter(id=order_id).first()
    return render(request, 'orders/track_order.html', {'order': order, 'order_id': order_id})



stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request, order_id):
    order = Order.objects.get(id=order_id)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': order.product},
                'unit_amount': int(order.price * 100),
            },
            'quantity': order.quantity,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/payment-success/'),
        cancel_url=request.build_absolute_uri('/payment-cancel/'),
    )

    return JsonResponse({'id': session.id})
@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})
@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/product_detail.html', {'product': product})


@login_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user.farmer
            product.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})

@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, farmer=request.user.farmer)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/update_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, farmer=request.user.farmer)

    if request.method == "POST":
        product.delete()
        return redirect('product_list')

    return render(request, 'products/delete_product.html', {'product': product})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Customer, CartItem

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Ensure the user has a Customer profile
    customer, created = Customer.objects.get_or_create(user=request.user)

    # Add product to cart or increase quantity
    cart_item, created = CartItem.objects.get_or_create(customer=customer, product=product)
    cart_item.quantity += 1
    cart_item.save()

    return redirect('cart_view')


@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(customer=request.user.customer)
    total_price = sum(item.get_total_price() for item in cart_items)
    return render(request, 'cart/cart_view.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def remove_from_cart(request, item_id):
    cart_item = CartItem.objects.get(id=item_id, customer=request.user.customer)
    cart_item.delete()
    return redirect('cart_view')



stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    cart_items = CartItem.objects.filter(customer=request.user.customer)
    total_price = sum(item.get_total_price() for item in cart_items)

    order = Order.objects.create(customer=request.user.customer, total_price=total_price)

    for item in cart_items:
        item.delete()  # Clear cart after order is placed

    return render(request, 'cart/checkout.html', {'order': order, 'total_price': total_price})

def process_payment(request, order_id):
    order = Order.objects.get(id=order_id)
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': f"Order {order.id}"},
                'unit_amount': int(order.total_price * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/payment-success/'),
        cancel_url=request.build_absolute_uri('/payment-cancel/'),
    )

    return JsonResponse({'id': session.id})



def checkout(request):
    cart_items = CartItem.objects.filter(customer=request.user.customer)
    total_price = sum(item.get_total_price() for item in cart_items)

    order = Order.objects.create(customer=request.user.customer, total_price=total_price)

    for item in cart_items:
        item.delete()  # Clear cart after order is placed

    # Send email notification
    subject = "Order Confirmation"
    message = f"Dear {request.user.username},\n\nYour order (ID: {order.id}) has been placed successfully!\nTotal: ${total_price}\n\nThank you for shopping with us!"
    recipient_email = request.user.email
    send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email])

    return render(request, 'cart/checkout.html', {'order': order, 'total_price': total_price})


def admin_dashboard(request):
    total_farmers = Farmer.objects.count()
    total_customers = Customer.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Order Analytics
    pending_orders = Order.objects.filter(status="pending").count()
    shipped_orders = Order.objects.filter(status="shipped").count()
    delivered_orders = Order.objects.filter(status="delivered").count()

    # Top Farmers based on ratings
    top_farmers = Farmer.objects.annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:5]

    context = {
        'total_farmers': total_farmers,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'top_farmers': top_farmers,
    }

    return render(request, 'admin_dashboard.html', context)

def farmer_products(request, username):
    farmer = get_object_or_404(Farmer, user__username=username)
    products = farmer.products.all()  # Access related products using the related_name
    return render(request, 'farmers/farmer_products.html', {'farmer': farmer, 'products': products})

def farmer_profile(request, username):
    # Retrieve the farmer profile based on the username
    farmer = get_object_or_404(Farmer, user__username=username)
    return render(request, 'farmers/farmer_profile.html', {'farmer': farmer})