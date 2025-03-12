import json
from django.shortcuts import render
import random
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import JsonResponse
from django.contrib.auth import login
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


def home(request):
    latest=Product.objects.all().order_by("-created")[:5]
    latest_two=Product.objects.all().order_by("-created")[5:9]
    top_rated_products = (
    Product.objects.annotate(avg_rating=Avg('review__star'))
    .order_by('-avg_rating')[:5]
)
    summer_pick = Product.objects.filter(summer_pick=True).first()
    summer_pick_all = Product.objects.filter(summer_pick=True)[1:5]

    return render(request,'user/home.html',{'latest':latest,'top_rated_products':top_rated_products,'summer_pick':summer_pick,'summer_pick_all':summer_pick_all,'latest_two':latest_two})



User = get_user_model()
otp_storage = {}  # Temporary storage for OTPs (use Redis in production)

def send_otp(phone):
    otp = random.randint(100000, 999999)
    otp_storage[phone] = otp
    print(f"OTP for {phone}: {otp}")  # Debugging, replace with SMS API
    return otp

def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        name=request.POST.get('name')
        password = request.POST.get("password")

        if CustomUser.objects.filter(phone=phone).exists():
            return JsonResponse({"error": "Phone number already registered"}, status=400)

        send_otp(phone)
        request.session["temp_user"] = {"email": email, "phone": phone, "password": password,'name':name}
        return redirect('verify_otp')
        
    

    return render(request, "user/register.html")

def verify_otp(request):
    if request.method == "POST":
        phone = request.session["temp_user"]["phone"]
        otp = int(request.POST.get("otp"))

        if phone in otp_storage and otp_storage[phone] == otp:
            user_data = request.session.get("temp_user")
            user = CustomUser.objects.create_user(
                name=user_data['name'],
                email=user_data['email'],
                phone=user_data["phone"],
                password=user_data["password"]
            )
            login(request, user)
            del otp_storage[phone]
            del request.session["temp_user"]
            return redirect('home')
        
        return JsonResponse({"error": "Invalid OTP"}, status=400)

    return render(request, "user/verify_otp.html")

def login_view(request):
    if request.method=='POST':
        phone=request.POST.get('phone')
        password=request.POST.get('password')

        try:
            user = CustomUser.objects.get(phone=phone)
            if user:
                if user.check_password(password):  # Verifies hashed password
                    login(request, user)  # Logs the user in
                    messages.success(request, "Login successful.")
                    return redirect('home')  # Replace with your home page route name
                else:
                    messages.error(request, "Invalid password.")
            else:
                messages.error("No user")
        except CustomUser.DoesNotExist:
            messages.error(request, "User with this phone number does not exist.")
    
    return render(request, 'user/login.html')

# def cart(request, id=None):
#     if not request.user.is_authenticated:
#         return redirect('login')  # Redirect to login if user not logged in

#     cart, created = Cart.objects.get_or_create(user=request.user)
#     cart_items = cart.cart_items.all()
#     total_price = cart.total_price()

#     for item in cart_items:
#         item.row_total = item.product.price * item.quantity

#     context = {
#         'cart_items': cart_items,
#         'total_price': total_price,
#     }
#     return render(request, 'user/cart.html', context)
    

# ✅ Add product to cart

# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     cart, created = Cart.objects.get_or_create(user=request.user)

#     cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

#     if not item_created:
#         cart_item.quantity += 1  # If item already exists, increase quantity
#         cart_item.save()
    
#     messages.success(request, "Product added to cart successfully!")
#     return redirect("")  

@csrf_exempt
def add_to_cart_ajax(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            data = json.loads(request.body)
            product_id = data.get("product_id")

            try:
                product = Product.objects.get(id=product_id)
                cart, _ = Cart.objects.get_or_create(user=request.user)
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

                if not created:
                    cart_item.quantity += 1
                    cart_item.save()

                return JsonResponse({"success": True})
            except Exception as e:
                return JsonResponse({"success": False, "error": str(e)})
    else:
        return redirect('login_view')

    return JsonResponse({"success": False, "error": "Invalid request"})# Redirect to cart page

# ✅ View cart




def checkout(request):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cart_items.all()

        if not cart_items:
            messages.error(request, "Your cart is empty!")
            return redirect("cart")

        # ✅ Create Order
        order = Order.objects.create(user=request.user, total_price=cart.total_price())

        # ✅ Move Cart Items to Order Items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # ✅ Clear the Cart after Checkout
        cart.cart_items.all().delete()

        messages.success(request, "Order placed successfully!")
        return redirect("order_summary", order_id=order.id)
    else:
        return redirect('login_view')
    
def add_address(request):
    if request.method=='POST':
        house_name=request.POST.get('house_name')
        pincode=request.POST.get('pincode')
        street=request.POST.get('street')
        city=request.POST.get('city')
        contact_no=request.POST.get('contact')
        contact_no2=request.POST.get('contact2')

        address=Address.objects.create(
            house_name=house_name,
            pincode=pincode,
            street=street,
            city=city,
            contact_no=contact_no,
            contact_no2=contact_no2
        )
        address.save()
        messages.success(request,'Address Added')
        return redirect('add_address')
    
    return render(request,'user/add_address.html')




def buy_now(request, product_id):
    
    product = get_object_or_404(Product, id=product_id)

    # ✅ Create a new order for the user
    order = Order.objects.create(user=request.user, total_price=product.price)

    # ✅ Create an order item for the selected product
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price
    )

    messages.success(request, "Order placed successfully!")
    return redirect("order_summary", order_id=order.id)

def order_summary(request,order_id):
    order=Order.objects.get(id=order_id)

    return render(request,'user/order_summary.html')

def product_detail(request,id):
    product=Product.objects.get(id=id)
    images = product.images.all()


    return render(request,'user/product_detail.html',{'product':product,'images':images})

def update_quantity(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        print(quantity)

        if request.user.is_authenticated:
            product = Product.objects.get(id=product_id)
            cart=Cart.objects.get(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
                return JsonResponse({'status': 'success', 'message': 'Quantity updated'})
            else:
                cart_item.quantity=quantity
                cart_item.save()
                return JsonResponse({'status': 'success', 'message': 'Quantity updated'})
        else:
            return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)