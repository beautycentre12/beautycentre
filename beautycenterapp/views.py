from django.shortcuts import render, redirect
from django.http import HttpResponseServerError
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.hashers import check_password
from .models import *
from .forms import CategoryForm, ProductForm
from .models import Category
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
import socket
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
import razorpay
from BeautyCenter import settings
from BeautyCenter.settings import RAZORPAY_KEY_ID,RAZORPAY_KEY_SECRET
from django.views.decorators.csrf import csrf_exempt
import datetime
import json
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from django.http import Http404,response
from .utils import send_whatsapp_message
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from django.db import transaction
from .forms import *
import plivo
import random
from datetime import datetime, timedelta
from .send_whatsapp import *
from django_select2 import forms as s2forms
from django.core.paginator import Paginator

@csrf_exempt  # Only for testing; remove in production
def get_subcategories(request):
    if request.method == 'POST':
        body = json.loads(request.body)  # Parse JSON body
        category_id = body.get('category_id')  # Get category_id from the POST data
        subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'title')
        return JsonResponse({'subcategories': list(subcategories)})
    

def load_categories(request):
    categories = Category.objects.filter(is_hidden=False).order_by('created_at')
    paginator = Paginator(categories, 8)  # Show 6 categories per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Return JSON response
    categories_data = [
        {
            'id': category.id,
            'title': category.title,
            'subcategories': [
                {'id': sub.id, 'title': sub.title} for sub in category.subcategories.filter(is_hidden=False)
            ]
        }
        for category in page_obj
    ]
    return JsonResponse({
        'categories': categories_data,
        'has_next': page_obj.has_next(),
    })


def load_categories_browser(request):
    categories = Category.objects.filter(is_hidden=False).order_by('created_at')
    paginator = Paginator(categories, 6)  # Show 6 categories per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    categories_data = [
        {
            'id': category.id,
            'title': category.title,
            'icon_url': category.image.url if category.image else '',  # Icon for the category
        }
        for category in page_obj
    ]

    return JsonResponse({
        'categories': categories_data,
        'has_next': page_obj.has_next(),
    })


# ------- Authentication system -------
def send_otp_to_phone(phone_number, otp):
    """Function to send OTP via SMS using Plivo"""
    client = plivo.RestClient(settings.PLIVO_AUTH_ID, settings.PLIVO_AUTH_TOKEN)

    # Create a friendly and clear OTP message with a 2-minute validity warning
    message = (
        f"Hello! Your One-Time Password (OTP) is {otp}. "
        f"Please use this code to complete your verification. "
        f"Note: This OTP is valid for only 2 minutes. "
        f"Do not share it with anyone for your security. - Team BeautyCenter"
    )
    
    try:
        response = client.messages.create(
            src=settings.SENDER_PHONE_NUMBER,  # Your verified Plivo phone number
            dst=f'+91{phone_number}',  # Assuming Indian numbers
            text=message,
        )
        return response
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return None


def signin(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == 'POST':
        # Check if OTP is requested
        if 'get_otp' in request.POST:
            phone_number = request.POST.get('username')

            if not phone_number:
                return JsonResponse({'status': 'error', 'message': 'Phone number is required.'})

            # Check if the phone number exists in the CustomUser model
            try:
                user = CustomUser.objects.get(phone_number=phone_number)
            except CustomUser.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Phone number not registered.'})

            # If the phone number exists, generate and send OTP
            otp = random.randint(100000, 999999)

            # Save OTP, phone number, and timestamp in session
            request.session['otp'] = otp
            request.session['phone_number'] = phone_number
            request.session['otp_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Send OTP to the phone
            send_result = send_otp_to_phone(phone_number, otp)

            if send_result:
                return JsonResponse({'status': 'success', 'message': 'OTP sent successfully! It will expire in 2 minutes.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Phone number not registered.'})

        # Handle OTP login
        elif 'login' in request.POST:
            phone_number = request.POST.get('username')
            otp_input = request.POST.get('password')  # OTP entered by the user

            # Verify OTP and check if it hasn't expired
            stored_otp = request.session.get('otp')
            stored_phone_number = request.session.get('phone_number')
            otp_timestamp = request.session.get('otp_timestamp')

            if stored_otp and stored_phone_number == phone_number:
                # Check if OTP has expired
                otp_time = datetime.strptime(otp_timestamp, '%Y-%m-%d %H:%M:%S')
                current_time = datetime.now()

                if current_time - otp_time > timedelta(minutes=2):
                    return JsonResponse({'status': 'error', 'message': 'OTP has expired. Please request a new one.'})

                # Verify OTP if it's still valid
                if otp_input == str(stored_otp):
                    try:
                        user = CustomUser.objects.get(phone_number=phone_number)
                        login(request, user)

                        # Clear session data
                        del request.session['otp']
                        del request.session['phone_number']
                        del request.session['otp_timestamp']

                        return JsonResponse({'status': 'success'})
                    except CustomUser.DoesNotExist:
                        return JsonResponse({'status': 'error', 'message': 'User not found.'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Invalid OTP.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid OTP or phone number.'})

    return render(request, 'beautycenterapp/page-login.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        username = request.POST.get('username')  # Optional: Keep a username
        
        if password == cpassword:
            # Check if the phone number already exists
            if not CustomUser.objects.filter(phone_number=phone_number).exists():
                user = CustomUser.objects.create_user(
                    phone_number=phone_number,
                    email=email,
                    password=password,
                    username=username,  # If you want to keep a separate username field
                )
                user.save()
                login(request, user)
                return redirect('home')
            else:
                print("User with this phone number already exists!")
                # Add your message logic here, such as showing a message in the template.
        else:
            print("Passwords do not match!")
            # Add logic to handle mismatched passwords.
            
    return render(request, 'beautycenterapp/page-register.html')

# logout function
@login_required(login_url="signin")
def signout(request):
    try:
        # Save the URL of the current page in the session
        request.session['last_url'] = request.get_full_path()
        logout(request)
        messages.success(request,"Logged Out successfully!")
        # return redirect('login')  # Redirect to your login page
        return redirect("/")
    except socket.gaierror:
        return HttpResponseServerError("Internet connection error")

# ------- End Authentication system -------
from django.db.models import Prefetch
from django.core.cache import cache


# def home(request):
#     categories = Category.objects.all()
#     populor_products = ProductItems.objects.all()[:10]
#     new_products = ProductItems.objects.all().order_by('-created')[:4]
#     random_populor_products = ProductItems.objects.all().order_by('?')[:5]

#     # Dynamically fetch all categories and map them to their products
#     category_products = {}
#     for category in categories:
#         category_products[category.title] = ProductItems.objects.filter(category=category)


#     # Fetch all brand items and their associated products
#     brand_items = BrandItem.objects.prefetch_related('categories', 'divisions').all()
#     # Ads
#     adss = Ads.objects.all().order_by('-created_at')[:3]
#      # Fetch all divisions
#     divisions = Division.objects.all()
#     main_banner=ProductItems.objects.all().order_by('?')[:1]
#     # Context
#     context = {
#         'categories': categories,
#         'p_prodcuts': populor_products,
#         'rp_prodcuts': random_populor_products,
#         'new_products': new_products,
#         'category_products': category_products,  # Pass products by category dynamically
#         'ads': adss,
#         'divisions': divisions,
#         'brand_items': brand_items,
#         'main_banner':main_banner
#     }
#     return render(request, 'beautycenterapp/index.html', context)

def home(request):
    # Check if the cached context exists to reduce query load
    cached_context = cache.get('home_page_context')
    if cached_context:
        print("comming from cache db.")
        return render(request, 'beautycenterapp/index.html', cached_context)

    # Fetch categories and prefetch related products for each category
    categories = Category.objects.prefetch_related(
        Prefetch('products', queryset=ProductItems.objects.select_related('category', 'subcategory').all())
    ).all()

    # Optimized product queries with `select_related` for ForeignKey relationships and `prefetch_related` for ManyToMany
    populor_products = ProductItems.objects.select_related('category', 'subcategory').prefetch_related('brand_items').all()[:10]
    new_products = ProductItems.objects.select_related('category', 'subcategory').prefetch_related('brand_items').order_by('-created')[:4]
    random_populor_products = ProductItems.objects.select_related('category', 'subcategory').prefetch_related('brand_items').order_by('?')[:5]

    # Dynamically fetch all categories and map them to their products
    category_products = {
        category.title: category.products.all()  # Use `products` related_name to reduce query count
        for category in categories
    }

    # Prefetch related categories and divisions for brand items
    brand_items = BrandItem.objects.prefetch_related('categories', 'divisions', 'subdivisions').all()

    # Fetch ads and divisions (use caching if appropriate)
    adss = Ads.objects.all().order_by('-created_at')[:3]
    divisions = Division.objects.prefetch_related('subdivisions').all()

    # Fetch the main banner with random products
    main_banner = ProductItems.objects.select_related('category', 'subcategory').order_by('?')[:1]

    # Context for template rendering
    context = {
        'categories': categories,
        'p_prodcuts': populor_products,
        'rp_prodcuts': random_populor_products,
        'new_products': new_products,
        'category_products': category_products,  # Pass products by category dynamically
        'ads': adss,
        'divisions': divisions,
        'brand_items': brand_items,
        'main_banner': main_banner,
    }

    # Cache the context for future requests to reduce query load
    cache.set('home_page_context', context, timeout=60 * 15)  # Cache for 15 minutes

    return render(request, 'beautycenterapp/index.html', context)


from django.core.cache import cache

def category_pdo(request, p_id=None):
    category = None
    cache_key = f"category_pdo_{p_id}" if p_id else "category_pdo_all"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        print("Serving from cache")
        products, category = cached_data
    else:
        print("Fetching from database")
        if p_id:
            # Fetch category by ID
            category = Category.objects.get(id=p_id)
            print("category title:- ", category.title)
            # Fetch products for the category
            products = ProductItems.objects.filter(category=category).order_by("-created")[:10]
        else:
            products = ProductItems.objects.all().order_by("-created")[:10]

        # Store the result in cache for future requests
        cache.set(cache_key, (products, category), timeout=60 * 15)  # Cache for 15 minutes
    
    # Render the partial template with the products
    return render(request, 'beautycenterapp/partials/category_pdo.html', {'p_products': products, "cat": category if category else None})


def division_detail(request, division_id):
    division = get_object_or_404(Division, id=division_id)
    context = {'division': division}
    return render(request, 'beautycenterapp/division_detail.html', context)


def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    # Filter products related to the category
    products = ProductItems.objects.filter(category=category)
    paginator = Paginator(products, 10)  # Show 10 products per page

    # Get the current page number
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # For related and new products
    related_prod = len(products)
    new_products = ProductItems.objects.all().order_by('?')[:5]
    categories = Category.objects.all()

    context = {
        'category': category,
        'categories': categories,
        'products': page_obj, 
        'page_obj': page_obj,  # Paginated products
        'new_products': new_products,
        'related_prod': related_prod,
    }

    return render(request, 'beautycenterapp/shop-grid-right.html', context)



def subcategory_detail(request, subcategory_id):
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)

    # Filter products related to the category
    products = ProductItems.objects.filter(subcategory=subcategory)
    paginator = Paginator(products, 10)  # Show 10 products per page

    # Get the current page number
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    related_prod=len(products)
    new_products = ProductItems.objects.all().order_by('-created')[:3]
    categories=Category.objects.all()
    dealofday= ProductItems.objects.all().order_by('?')[:5]


    context = {
        'subcategory': subcategory,
        'categories': categories,
        'products': page_obj,
        'page_obj': page_obj,
        'new_products':new_products,
        'related_prod': related_prod,
        'new_products': new_products,
        'dealofday': dealofday
    }
    
    return render(request, 'beautycenterapp/shop-grid-right-subcat.html', context)



def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_category')
    else:
        form = CategoryForm()
    return render(request, 'beautycenterapp/add_category.html', {'form': form})

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_product')
    else:
        form = ProductForm()
    return render(request, 'beautycenterapp/add_product.html', {'form': form})

@login_required(login_url='signin')
def update_user_profile(request):
    user = request.user
    user_phone, created = UserPhone.objects.get_or_create(user=user)
    user_detail = get_object_or_404(User, username=request.user.username)

    if request.method == 'POST':
        # Handle user data
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        # Handle phone number data
        phone_no = request.POST.get('phone_no')
        alternate_phone = request.POST.get('alt_phone_no')
        gst_no = request.POST.get('gst_no')

        # Update user model
        user_detail.first_name = first_name
        user_detail.last_name = last_name
        user_detail.email = email
        user_detail.username= username
        user_detail.save()

        # Update UserPhone model
        user_phone.phone_no = phone_no
        user_phone.alternate_phone = alternate_phone
        user_phone.gst_no= gst_no
        user_phone.save()

        return redirect('account')  # Redirect to the profile page or any other page


@login_required(login_url='signin')
def change_password(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_new_password = request.POST.get('confirm_new_password')

            user = request.user

            if not check_password(current_password, user.password):
                messages.error(request, "Current password is incorrect.")
            elif new_password != confirm_new_password:
                messages.error(request, "New passwords do not match.")
            elif len(new_password) < 8:
                messages.error(request, "New password must be at least 8 characters long.")
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Important for keeping the user logged in
                messages.success(request, "Password changed successfully!")
                return redirect('account')  # Redirect to the account page or any other page

        return redirect('account')
    else:
        return redirect('signin')

def get_user_confirmed_order_items(user):
    confirmed_order_items = OrderItem.objects.filter(
        order__payment_status=PaymentStatus.SUCCESS,
        order__user=user
    ).distinct('order')
    
    return confirmed_order_items

from django.contrib.auth import get_user_model
User = get_user_model()  # Use this to reference the custom user model

@login_required(login_url='signin')
def account(request):
    user_detail = get_object_or_404(CustomUser, username=request.user.username)
    
    try:
        phone_no_detail = get_object_or_404(UserPhone, user=request.user)
        phone_no = phone_no_detail.phone_no
        alter_phone_no = phone_no_detail.alternate_phone
        gst_no = phone_no_detail.gst_no
    except Http404:
        phone_no = None
        alter_phone_no = None
        gst_no = None

    confirmed_order_items = OrderItem.objects.filter(order__user=request.user)
    for c in confirmed_order_items:
        print("order confirmed items- ", c.order.payment_status)

    context = {
        'user_detail': user_detail,
        'phone_no': phone_no,
        'alter_phone_no': alter_phone_no,
        'gst_no': gst_no,
        'confirmed_order_items': confirmed_order_items,
    }

    if request.user.is_superuser:
        if request.method == 'POST':
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            cpassword = request.POST.get('cpassword')

            if password == cpassword:
                # Create a new staff user
                CustomUser.objects.create_user(
                    first_name=fname,
                    last_name=lname,
                    username=username,
                    email=email,
                    password=password,
                    is_staff=True
                )
        
        # Get staff users to display
        staff_users = CustomUser.objects.filter(is_staff=True).exclude(is_superuser=True)
        Productform = ProductForm()  # Handle file upload with request.FILES
        FormCategory=CategoryForm()
        FormsubCategory=subCategoryForm()
        FormBrandItem=BrandItemForm()
        return render(request, "beautycenterapp/page-account-credits.html", {'context': context, 'staffs': staff_users, 'form': Productform,'catForm':FormCategory,'FormsubCat':FormsubCategory,'ForomBrand':FormBrandItem})
    
    elif request.user.is_staff:
        return render(request, "beautycenterapp/page-account.html", context)
    
    else:
        return render(request, "beautycenterapp/page-account.html", context)


# def add_product(request):
#     if request.method == "POST":
#         form = ProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             # Return a success message to replace the form content
#             return HttpResponse("<p class='alert alert-success'>Product added successfully!</p>")
#         else:
#             # Return form errors inline if form is invalid
#             errors_html = "".join([
#                 f"<p class='alert alert-danger'>{error}</p>"
#                 for error in form.errors.values()
#             ])
#             return JsonResponse({
#                 "html": errors_html,
#                 "success": False
#             })
#     else:
#         # Handle GET request by rendering the form
#         form = ProductForm()
#         return render(request, "partials/product_form.html", {"form": form})


from django.views.decorators.http import require_POST


def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Return a success message to replace the form content
            return HttpResponse("<p class='alert alert-success'>Category added successfully!</p>")
        else:
            # Return form errors inline if form is invalid
            errors_html = "".join([
                f"<p class='alert alert-danger'>{error}</p>"
                for error in form.errors.values()
            ])
            return JsonResponse({
                "html": errors_html,
                "success": False
            })
    else:
        # Handle GET request by rendering the form
        form = ProductForm()
        return render(request, "partials/product_form.html", {"form": form})

def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Return a success message to replace the form content
            return HttpResponse("<p class='alert alert-success'>Category added successfully!</p>")
        else:
            # Return form errors inline if form is invalid
            errors_html = "".join([
                f"<p class='alert alert-danger'>{error}</p>"
                for error in form.errors.values()
            ])
            return JsonResponse({
                "html": errors_html,
                "success": False
            })
    else:
        # Handle GET request by rendering the form
        form = CategoryForm()
        return render(request, "partials/category_form_partial.html", {"form": form})

def add_subcategory(request):
    if request.method == "POST":
        form = subCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Return a success message to replace the form content
            return HttpResponse("<p class='alert alert-success'>Category added successfully!</p>")
        else:
            # Return form errors inline if form is invalid
            errors_html = "".join([
                f"<p class='alert alert-danger'>{error}</p>"
                for error in form.errors.values()
            ])
            return JsonResponse({
                "html": errors_html,
                "success": False
            })
    else:
        # Handle GET request by rendering the form
        form = subCategoryForm()
        return render(request, "partials/subcategory.html", {"form": form})

def add_brand(request):
    if request.method == "POST":
        form = BrandItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Return a success message to replace the form content
            return HttpResponse("<p class='alert alert-success'>Brand added successfully!</p>")
        else:
            # Return form errors inline if form is invalid
            errors_html = "".join([
                f"<p class='alert alert-danger'>{error}</p>"
                for error in form.errors.values()
            ])
            return JsonResponse({
                "html": errors_html,
                "success": False
            })
    else:
        # Handle GET request by rendering the form
        form = BrandItemForm()
        return render(request, "partials/brand_form.html", {"form": form})



def search_order_by_id(request):
    if request.method == "POST":
        print("Request method is POST")

        # Checking if it's an AJAX request (modern method)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            print("Request is an AJAX request")

            provider_order_id = request.POST.get("order_id")
            print(f"Order ID received: {provider_order_id}")

            if not provider_order_id:
                return JsonResponse({'success': False, 'message': 'Order ID is required'})

            try:
                order_item = get_object_or_404(OrderItem, provider_order_id=provider_order_id)
                order_data = {
                    'provider_order_id': order_item.provider_order_id,
                    'product_title': order_item.product.title,
                    'date': order_item.created_at.strftime("%Y-%m-%d"),
                    'delivery_status': order_item.delivery_status,
                    'payment_status': order_item.order.payment_status,
                    'total': order_item.price * order_item.quantity,
                    'quantity': order_item.quantity,
                }
                return JsonResponse({'success': True, 'order': order_data})
            except OrderItem.DoesNotExist:
                print("Order not found")
                return JsonResponse({'success': False, 'message': 'Order not found'})
        else:
            print("Not an AJAX request")
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def about(request):
    return render(request,"beautycenterapp/page-about.html")


#---------- start cart functionality----------------
@login_required(login_url='signin')
def increase_quantity(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    print('id of cart item- ',cart_item_id)
    return redirect('addCart')

@login_required(login_url='signin')
def decrease_quantity(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()  # Remove the item if the quantity becomes zero
    return redirect('addCart')


@login_required(login_url="signin")
def add_to_cart(request, product_id):
    product = ProductItems.objects.get(pk=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    else:
        # Create an entry in the Checkout model only if a new cart item is created
        checkout.objects.create(user=request.user, cart_item=cart_item)
    
        # Remove the product from the wishlist if it exists
    # wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
    # if wishlist_item:
    #     wishlist_item.delete()
    return redirect('addCart')

@login_required(login_url="signin")
def addCart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    counter_items = len(cart_items)
    total_price = 0

    for ct in cart_items:
        if ct.product.updated_price:
            total_price += float(ct.product.updated_price) * ct.quantity
        elif ct.product.discount:
            total_price += ct.quantity * ct.product.discount
        else:
            total_price += ct.quantity * ct.product.price

    return render(request, 'beautycenterapp/shop-cart.html', {'cart_items': cart_items, 'total_price': total_price, 'counter': counter_items})

@login_required(login_url='signin')
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.delete()
    return redirect('addCart')

@login_required(login_url='signin')
def remove_all_from_cart(request):
    CartItem.objects.filter(user=request.user).delete()
    return redirect('addCart')
# ----------- End cart functionality -------------

#------------ start wishlist functionality ------------
def check_wishlist_status(request):
    product_id = request.GET.get('product_id')
    user = request.user
    is_wishlisted = False  # Default status

    if user.is_authenticated:
        # Perform the logic to check if the product is wishlisted in your database
        is_wishlisted = Wishlist.objects.filter(user=user, product_id=product_id).exists()
    
    return JsonResponse({'status': 'success', 'is_wishlisted': is_wishlisted})

@login_required(login_url='signin')
def add_to_wishlist(request,product_id):
        user = request.user
        is_wishlisted = False  # Default status
        
        if user.is_authenticated:
            wishlist_item, created = Wishlist.objects.get_or_create(user=user, product_id=product_id)

            if created:
                # is_wishlisted = True
                return redirect('wishlist')
        return redirect('signin')
            

def remove_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        try:
            # Get the product instance
            product = ProductItems.objects.get(pk=product_id)
            
            # Filter wishlist item based on user and product instance
            wishlist_item = Wishlist.objects.get(user=request.user, product=product)
            wishlist_item.delete()
            
            return redirect('wishlist')
        except ProductItems.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'})
        except Wishlist.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found in wishlist'})
    else:
        return redirect('signin')


@login_required(login_url='signin')
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    wishlist_count=len(wishlist_items)
    context = {
        'wishlist_items': wishlist_items,
        'wishlist_count': wishlist_count,
    }
    return render(request,"beautycenterapp/shop-wishlist.html",context)

#---------- Start Order function functions ------------
CustomUser = get_user_model()  # CustomUser model reference
@login_required(login_url='signin')
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    count_cart_items = len(cart_items)
    total_price = 0

    for ct in cart_items:
        if ct.product.updated_price:
            total_price += float(ct.product.updated_price) * ct.quantity
        elif ct.product.discount:
            total_price += ct.quantity * ct.product.discount
        else:
            total_price += ct.quantity * ct.product.price

    total_amount = int(total_price * 100)  # Razorpay expects amount in paise

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        client.utility.verify_payment_signature({})  # Test credentials
    except Exception as e:
        print(f"Credential Error: {str(e)}")

    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        billing_address = request.POST.get('billing_address')
        billing_address2 = request.POST.get('billing_address2')
        country = request.POST.get('country')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        phone = request.POST.get('phone')
        cname = request.POST.get('cname')
        email = request.POST.get('email')
        add_info = request.POST.get('add_info')
        payment_option = request.POST.get('payment_option')

        # Wrap in transaction
        with transaction.atomic():
            order_instance = Order(user=request.user, payment_status='Pending')
            order_instance.save()

            billing_address_instance = Billing_Address.objects.create(
                user=request.user, name=name, address=billing_address, address2=billing_address2,
                country=country, city=city, state=state, pincode=zipcode, phone=phone,
                email=email, company_name=cname, additional_info=add_info
            )

            def create_order_items(order, cart_items, billing_address, provider_order_id):
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order, product=item.product, quantity=item.quantity,
                        price=item.product.price, ordered_address=billing_address,
                        provider_order_id=provider_order_id, delivery_status='Pending'
                    )

            if payment_option == 'online_gateway':
                print(f"online mood order amount - {total_amount}")
                try:
                    razorpay_order = client.order.create({
                        "amount": total_amount,
                        "currency": "INR",
                        "payment_capture": "1"
                    })
                    print("Razorpay Order Created:", razorpay_order)
                    create_order_items(order_instance, cart_items, billing_address_instance, razorpay_order["id"])
                    cart_items.delete()
                    context = {
                        "callback_url": "https://beautycentre.in/success/",
                        "razorpay_key": settings.RAZORPAY_KEY_ID,
                        "order": order_instance,
                        "amount": total_amount,
                    }
                    return render(request, "beautycenterapp/orders/payment.html", context)
                except Exception as e:
                    print(f"Razorpay Order Creation Failed: {str(e)}")
                    return render(request, 'beautycenterapp/orders/payment.html', {"error": "Payment gateway error. Please try again."})

            elif payment_option == 'bank_transfer':
                provider_order_id = f'order_{get_random_string(length=14)}'
                create_order_items(order_instance, cart_items, billing_address_instance, provider_order_id)
                cart_items.delete()
                context = {
                    'order': order_instance,
                    'bank_transfer_details': 'Bank transfer instructions go here.',
                }
                return render(request, "beautycenterapp/orders/bank_transfer.html", context)

            elif payment_option == 'cod':
                provider_order_id = f'order_{get_random_string(length=14)}'
                create_order_items(order_instance, cart_items, billing_address_instance, provider_order_id)
                cart_items.delete()
                return redirect('orderTrack')  # Redirect to order tracking page

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'count_cart_items': count_cart_items,
    }
    return render(request, 'beautycenterapp/shop-checkout.html', context)
#======== Start Payments Gateway funcation =========#

@login_required(login_url='signin')
def confirm_bank_transfer(request):
    if request.method == 'POST':
        utr_number = request.POST.get('utr_number')
        order_id = request.POST.get('order_id')

        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Update UTR number for each order item
        order_items = order.items.all()
        for item in order_items:
            item.urt_no = utr_number
            item.save()

        # Update order status
        order.payment_status = PaymentStatus.SUCCESS  # or SUCCESS based on your logic
        order.save()

        return redirect('orderTrack')

    return redirect('checkout')

@csrf_exempt
def callback(request):
    RAZORPAY_KEY_ID = settings.RAZORPAY_KEY_ID
    RAZORPAY_KEY_SECRET = settings.RAZORPAY_KEY_SECRET

    def verify_signature(response_data):
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        return client.utility.verify_payment_signature(response_data)

    try:
        if "razorpay_signature" in request.POST:
            payment_id = request.POST.get("razorpay_payment_id", "")
            provider_order_id = request.POST.get("razorpay_order_id", "")
            signature_id = request.POST.get("razorpay_signature", "")
            order_item = OrderItem.objects.get(provider_order_id=provider_order_id)
            order_item.payment_id = payment_id
            order_item.signature_id = signature_id
            order_item.save()

            if verify_signature(request.POST):
                order_item.order.payment_status = PaymentStatus.SUCCESS
            else:
                order_item.order.payment_status = PaymentStatus.FAILURE
            order_item.order.save()

            if order_item.order.payment_status == PaymentStatus.SUCCESS:
                return redirect('orderTrack')
            else:
                return render(request, "checkout.html", context={"status": order_item.order.payment_status})

        else:
            error_metadata = json.loads(request.POST.get("error[metadata]"))
            payment_id = error_metadata.get("payment_id")
            provider_order_id = error_metadata.get("order_id")
            order_item = OrderItem.objects.get(provider_order_id=provider_order_id)
            order_item.payment_id = payment_id
            order_item.order.payment_status = PaymentStatus.FAILURE
            order_item.order.save()
            return render(request, "checkout.html", context={"status": order_item.order.payment_status})

    except OrderItem.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('checkout')
    except Exception as e:
        messages.error(request, "An error occurred. Please try again.")
        return redirect('checkout')    
    
#---------- End Order function functions --------------

@login_required(login_url='signin')
def OrderTrack(request):
    user = request.user  # Get the current logged-in user
    confirmed_order_items = OrderItem.objects.filter(
        order__user=user
    )

    # Calculate the estimated delivery dates and collect invoice numbers
    estimated_delivery_dates = []
    invoice_numbers = []
    tracking_ids = []
    delivery_statuses = []

    for order_item in confirmed_order_items:
        estimated_delivery_dates = order_item.order.created_at + timedelta(days=5)
        # estimated_delivery_dates=estimated_delivery_date
        # invoice_numbers=order_item.invoice_number
        # delivery_statuses=order_item.order.delivery_status

    total_price = sum(float(item.price) * item.quantity for item in confirmed_order_items)

    sample_items = ProductItems.objects.all().order_by('?')[:6]

    gst_on_total_price = total_price * 18 / 100
    total_price_due = total_price + gst_on_total_price + 5

    context = {
        'sample_items': sample_items,
        'confirmed_order_items': confirmed_order_items,
        'estimated_delivery_dates': estimated_delivery_dates,
        'invoice_numbers': invoice_numbers,
        'tracking_ids': tracking_ids,
        'total_price': total_price,
        'total_price_due': total_price_due,
        'gst_charge': gst_on_total_price,
        'delivery_statuses': delivery_statuses,
    }
    return render(request, 'beautycenterapp/orders/order_tracker.html', context)

@login_required(login_url='signin')
def get_invoice_details(request, provider_order_id):
    order_item = get_object_or_404(OrderItem, provider_order_id=provider_order_id)

    invoice_details = {
        'invoice_number': order_item.invoice_number,
        'tracking_id': order_item.tracking_id,
        'estimated_delivery_date': (order_item.created_at + timedelta(days=5)).strftime('%Y-%m-%d'),
        'delivery_status': order_item.delivery_status,
        'payment_status': order_item.order.payment_status,  # Assuming payment_status is a field in Order
        'order_id': order_item.order.id,  # Assuming id is a field in Order
        'billing_address': {
            'name': order_item.ordered_address.name,
            'address': order_item.ordered_address.address,
            'city': order_item.ordered_address.city,
            'country': order_item.ordered_address.country,
            'pincode': order_item.ordered_address.pincode,
        },
        'items': [
            {
                'title': item.product.title,
                'quantity': item.quantity,
                'unit_price': item.price,
                'total': item.price * item.quantity,
            } for item in OrderItem.objects.filter(provider_order_id=provider_order_id)
        ],
        'subtotal': sum(item.price * item.quantity for item in OrderItem.objects.filter(provider_order_id=provider_order_id)),
        'gst_charge': sum(item.price * item.quantity for item in OrderItem.objects.filter(provider_order_id=provider_order_id)) * 0.18,
        'shipping': 5.00,
        'total_due': sum(item.price * item.quantity for item in OrderItem.objects.filter(provider_order_id=provider_order_id)) * 1.18 + 5.00,
    }
    return JsonResponse(invoice_details)

def contact(request):
    return render(request,'beautycenterapp/page-contact.html')


def product_detail(request, p_id):
    single_product = get_object_or_404(ProductItems, pk=p_id)
    
    # Fetch related brand items
    brand_items = single_product.brand_items.all()
    
    # Gather related divisions and subdivisions for all brand items
    divisions = set()
    subdivisions = set()
    for brand in brand_items:
        divisions.update(brand.divisions.all())
        subdivisions.update(brand.subdivisions.all())
    # Split tags of the single product into a list, if available
    tags_list = [tag.strip() for tag in single_product.tags.split(',')] if single_product.tags else []
    # Fetch the 3 most recently created products
    new_products = ProductItems.objects.all().order_by('-created')[:3]
     # Fetch related products (4 random products)
    related_products = ProductItems.objects.all().order_by('?')[:4]
    # Fetch all categories
    categories = Category.objects.all()
    prod_img=ProductImage.objects.filter(product=single_product)
    context = {
        'categories': categories,
        'r_prod': related_products,
        'new_products': new_products,
        'single_prod': single_product,
        'selected_brand': brand_items,
        'selected_divisions': divisions,
        'selected_subdivisions': subdivisions,
        "tag_list":tags_list,
        "prod_img":prod_img,
    }
    return render(request, "beautycenterapp/shop-product-right.html", context)


# def products_market(request):
#     products=ProductItems.objects.all().order_by('created')
#     category=Category.objects.all()
#     context={
#         'products':products,
#         'categories':category,
#     }
#     return render(request,'beautycenterapp/shop-list-right.html',context)


# def products_market(request, category_id=None):
#     if category_id:
#         # Get the selected subcategory by ID
#         selected_category = get_object_or_404(Category, id=category_id)
#         # Filter products by the selected subcategory
#         products = ProductItems.objects.filter(category=selected_category).order_by('created')
#     else:
#         # If no subcategory is selected, show all products
#         products = ProductItems.objects.all().order_by('created')
#         selected_category = None

#     categories = Category.objects.all()

#     context = {
#         'products': products,
#         'categories': categories,
#         'selected_category': selected_category,
#         'product_count':len(products)
#     }
    
#     return render(request, 'beautycenterapp/shop-list-right.html', context)

def products_market(request, brand_id=None):
    if brand_id:
        # Get the selected subcategory by ID
        selected_brand = get_object_or_404(BrandItem, id=brand_id)
        # Filter products by the selected subcategory
        products = ProductItems.objects.filter(brand_items=selected_brand).order_by('created')
    else:
        # If no subcategory is selected, show all products
        products = ProductItems.objects.all().order_by('created')
        selected_brand = None


    paginator = Paginator(products, 10)  # Show 10 products per page

    # Get the current page number
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    new_products = ProductItems.objects.all().order_by('-created')[:3]
    dealofday= ProductItems.objects.all().order_by('?')[:5]


    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_brand,
        'product_count':len(products),
        'new_products': new_products,
        'dealofday': dealofday
    }
    
    return render(request, 'beautycenterapp/shop-list-right.html', context)




def get_cart_and_wishlist_counts(user):
    cart_count = CartItem.objects.filter(user=user).count()
    carts_item = CartItem.objects.filter(user=user).order_by('-added_at')[:2]
    wishlist_count = Wishlist.objects.filter(user=user).count()
    cart_data = [{
        'product_name': item.product.title,
        'quantity': item.quantity,
        'price': item.product.price,
        'product_image': item.product.image.url,  # Assuming you have a field 'image' in your Product model
    } for item in carts_item]
    return cart_count, wishlist_count, cart_data

@login_required(login_url='signin')
def get_cart_and_wishlist_counts_view(request):
    if request.method == 'GET':
        cart_count, wishlist_count, carts = get_cart_and_wishlist_counts(request.user)
        data = {
            'cart_count': cart_count,
            'wishlist_count': wishlist_count,
            'cart': carts,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)    

def items_categories(request):
    # Get offset from request
    offset = int(request.GET.get('offset', 0))  # Default to 0 if not provided
    limit = 7  # Number of brands to return at a time
    categories = Category.objects.all().values('id', 'title')[offset:offset + limit]  # Pagination
    return JsonResponse(list(categories), safe=False)

# def items_brand(request):
#     # Get offset from request
#     offset = int(request.GET.get('offset', 0))  # Default to 0 if not provided
#     limit = 7  # Number of brands to return at a time
#     brands = brandItem.objects.all().values('id', 'title')[offset:offset + limit]  # Pagination
#     return JsonResponse(list(brands), safe=False)

def items_brand(request):
    # Get offset from request
    brands = BrandItem.objects.all().order_by("-created_at")
    return render(request,"beautycenterapp/shop-grid-right-brand.html")
    
def brand_filtered(request, pk=None):
    if pk:
        # If `pk` is provided, fetch the specific brand
        brand = get_object_or_404(BrandItem, id=pk)
        categories = Category.objects.filter(brand=brand)
        products = ProductItems.objects.filter(category__in=categories).order_by('?')
    else:
        # If `pk` is not provided, fetch all brands, categories, and products
        brand = BrandItem.objects.all().order_by("-created_at")
        categories = Category.objects.all()
        products = ProductItems.objects.order_by('?')

    paginator = Paginator(brand, 12)  # Show 10 products per page

    # Get the current page number
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Count the related products for the brands
    new_products = ProductItems.objects.all().order_by('?')[:5]
    related_prod_count = products.count()
    for i in brand:
        print(i.title)  
    context = {
        'brand': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'products': products,
        'new_products':new_products,
        'related_prod_count': len(brand),
    }

    return render(request, "beautycenterapp/shop-grid-right-brand.html", context)




def brand_filtered_professional(request, name=None):
    # Fetch the "Professional" division, or any division using division_id if provided
    # if division_id:
    #     division = get_object_or_404(Division, id=division_id)
    # else:
    if name:
        division = Division.objects.filter(name=name).first()
        print("division:- ",division)

    # Filter brands associated with the specific division
    brands = BrandItem.objects.filter(divisions=division, is_hidden=False).distinct()

    # Fetch categories and products linked to these brands
    categories = Category.objects.filter(brand_items__in=brands, is_hidden=False).distinct()
    products = ProductItems.objects.filter(category__in=categories, is_hidden=False).order_by('?')

    print("products :- ",products)
    prodLen=len(products)
    # Fetch 4 new random products
    new_products = ProductItems.objects.filter(is_hidden=False).order_by('?')[:5]
    paginator = Paginator(products, 12)  # Show 10 products per page

    # Get the current page number
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    category=Category.objects.all().order_by("-created_at")
    print(page_obj)
    # Context preparation
    context = {
        'brand': brands,
        'categories': category,
        'products': page_obj,
        'page_obj': page_obj,
        'new_products': new_products,
        'related_prod_count': brands.count(),
        'division': name,
        'count_item':prodLen,
    }

    return render(request, "beautycenterapp/shop-grid-right-brand-profess.html", context)


def search_items(request):
    query = request.GET.get('q')
    category_title = request.GET.get('category')
    categories = Category.objects.all()
    items = ProductItems.objects.all()
    new_products = ProductItems.objects.all().order_by('?')[:5]

    # Filter items based on query and category
    query=query.strip()
    if query:
        items = items.filter(title__icontains=query)
    if category_title and category_title != "All Categories":
        items = items.filter(category__title=category_title)

    # Apply pagination: Show 10 items per page
    paginator = Paginator(items, 10)  # 10 items per page
    page_number = request.GET.get('page')  # Get the current page number
    page_obj = paginator.get_page(page_number)  # Paginated items

    count_item = items.count()

    context = {
        'items': page_obj,  # Paginated object
        'page_obj': page_obj,  # Paginated object
        'categories': categories,
        "count_item": count_item,
        'new_products': new_products,
        'query': query,  # Pass the query back to retain the search input
        'category_title': category_title,  # Pass selected category back
    }
    return render(request, 'beautycenterapp/shop-grid-right.html', context)




#blog code
def blog_list(request):
    blogs = Blog.objects.all().order_by('-published_date')
    return render(request, 'beautycenterapp/blog_list.html', {'blogs': blogs})

def blog_detail(request, id):
    blog = get_object_or_404(Blog, id=id)
    blog.views += 1  # Increment views count each time a blog is accessed
    blog.save()
    return render(request, 'beautycenterapp/blog_detail.html', {'blog': blog})





def compare_products(request, *product_ids):
    # Retrieve the selected products for comparison
    products = ProductItems.objects.filter(id__in=product_ids)
    context = {
        'products': products,
    }
    return render(request, 'beautycenterapp/compare_products.html', context)