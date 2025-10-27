from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from urllib.parse import unquote
from .form import CustomUserForm, CustomLoginForm, PasswordResetForm, SetNewPasswordForm
from .models import Product, Category
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


# Home page
def home(request):
    products = Product.objects.filter(trending=True, status=False)
    return render(request, 'shop/index.html', {'products': products})

# Register
def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = CustomUserForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    return render(request, 'shop/register.html', {"form": form})

# Login
def login(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = CustomLoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    return render(request, 'shop/login.html', {'form': form})

# Logout
def logout_view(request):
    auth_logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')

# Reset password
def reset_password(request):
    form = PasswordResetForm(request.POST or None)
    return render(request, 'shop/reset_password.html', {'form': form})

# Set new password
def set_new_password(request, uidb64, token):
    form = SetNewPasswordForm(request.POST or None)
    return render(request, 'shop/set_new_password.html', {'form': form})

# Collections
def collections(request):
    categories = Category.objects.filter(status=0)
    return render(request, 'shop/collections.html', {'categories': categories})

# Products in a category
def collectionsview(request, name):
    try:
        category = Category.objects.get(name=name, status=0)
        products = Product.objects.filter(category=category, status=0)
        return render(request, 'shop/products/index.html', {'products': products, 'category': category})
    except Category.DoesNotExist:
        messages.warning(request, "No such category found.")
        return redirect('collections')

# Product details
def productDetails(request, cname, pname):
    cname = unquote(cname)
    pname = unquote(pname)
    try:
        category = Category.objects.get(name=cname, status=0)
        product = Product.objects.get(category=category, name=pname, status=0)
        savings = product.original_price - product.selling_price
        return render(request, 'shop/products/productDetails.html', {'product': product, 'category': category, 'savings': savings})
    except Category.DoesNotExist:
        messages.warning(request, "No such category found.")
        return redirect('collections')
    except Product.DoesNotExist:
        messages.warning(request, "No such product found.")
        return redirect('collectionsview', name=cname)

def cart_view(request):
    cart_items = []
    total = 0
    for pid, qty in request.session.get('cart', {}).items():
        try:
            product = Product.objects.get(id=pid)
            subtotal = product.selling_price * qty
            total += subtotal
            cart_items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})
        except Product.DoesNotExist:
            continue

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

# Add to cart
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    messages.success(request, f"{product.name} added to cart!")
    return redirect('productDetails', cname=product.category.name, pname=product.name)

# Buy now
def buy_now(request, product_id):
    product = Product.objects.get(id=product_id)
    request.session['cart'] = {str(product_id): 1}  # Replace cart
    return redirect('checkout')  # Create a checkout page

def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)] = quantity
        request.session['cart'] = cart
    return redirect('cart')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('cart')


def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for pid, qty in cart.items():
        product = Product.objects.get(id=pid)
        subtotal = product.selling_price * qty
        cart_items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})
        total += subtotal

    # Create Razorpay order
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    order_amount = int(total * 100)  # Convert ₹ to paise
    order_currency = 'INR'
    order = client.order.create(dict(amount=order_amount, currency=order_currency, payment_capture=1))

    context = {
        'cart_items': cart_items,
        'total': total,
        'razorpay_order_id': order['id'],
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'order_amount': order_amount,
        'order_currency': order_currency
    }
    return render(request, 'shop/checkout.html', context)


@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        return JsonResponse({"status": "Payment successful!"})
