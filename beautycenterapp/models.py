from django.db import models
from ckeditor.fields import RichTextField  # Import RichTextField for rich text descriptions
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.utils.translation import gettext_lazy as _
import uuid
from datetime import datetime
from beautycenterapp.utils import send_whatsapp_message
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum, F
from decimal import Decimal
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    address=models.TextField(null=True,blank=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'username']  # Add other required fields if necessary

    def __str__(self):
        return f"{self.get_full_name()} - {self.email} - {self.username}"
    
    
class UserPhone(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True)
    phone_no = models.CharField(max_length=15, null=True, blank=True, unique=True, help_text='Enter your primary phone number')
    alternate_phone = models.CharField(max_length=15, null=True, blank=True, help_text='Enter an alternate phone number if any')
    gst_no = models.CharField(max_length=15, null=True, blank=True, help_text='Enter an GST NO. if any')

    def __str__(self):
        return f"UserPhone - {self.user.username}"

class Ads(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='ads/')
    created_at = models.DateTimeField(auto_now_add=True)
    company_brand = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title



# Division model
class Division(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# SubDivision model
class SubDivision(models.Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='subdivisions')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.division.name} - {self.name}'

# BrandItem model
class BrandItem(models.Model):
    title = models.CharField(max_length=50)
    image=models.ImageField(upload_to="brands/",null=True,blank=True)
    sku = models.CharField(max_length=10, null=True, unique=True) 
    created_at = models.DateTimeField(auto_now=True)
    divisions = models.ManyToManyField(Division, related_name='brand_items')  # Many-to-Many relationship with Division
    subdivisions = models.ManyToManyField(SubDivision, related_name='brand_items')  # Many-to-Many relationship with SubDivision
    categories = models.ManyToManyField('Category', related_name='brand_items')  # Many-to-Many relationship with Category
    subcategories = models.ManyToManyField('SubCategory', related_name='brand_items')
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title}"

    @property
    def categories_count(self):
        return self.categories.count()
    
    @property
    def product_count(self):
        return self.products.count()
        
    def save(self, *args, **kwargs):
        """Override the save method to generate a unique SKU within 10 characters."""
        if not self.sku:
            base_sku = slugify(self.title)[:4].upper()  # Slugify and take only the first 4 characters
            unique_id = uuid.uuid4().hex[:5].upper()  # Generate a 5-character unique ID
            self.sku = f"{base_sku}-{unique_id}"  # Combine and ensure it's no longer than 10 characters

            # Ensure SKU length does not exceed 10 characters
            if len(self.sku) > 10:
                self.sku = self.sku[:10]

            # Check if the SKU is unique
            if BrandItem.objects.filter(sku=self.sku).exists():
                raise ValidationError("SKU must be unique. Try saving again.")
            
        super().save(*args, **kwargs)
    
# Category model
class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/')
    brand = models.ForeignKey(BrandItem, on_delete=models.CASCADE, related_name="brandName", null=True)
    created_at = models.DateTimeField(auto_now=True, null=True)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    @property
    def product_count(self):
        return self.products.count()

# SubCategory model
class SubCategory(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='subcategories/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    created_at = models.DateTimeField(auto_now=True)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def product_count(self):
        """Count the number of products associated with this subcategory."""
        return self.products.count()

class CategoryBulkDiscount(models.Model):
    category = models.ForeignKey(Category, related_name='bulk_discounts', on_delete=models.CASCADE)
    min_quantity = models.PositiveIntegerField()
    discount_percentage = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.category.title} - {self.min_quantity} units - {self.discount_percentage}% discount"


class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., '250g'
    display_name = models.CharField(max_length=100)  # e.g., '250 gram'

    def __str__(self):
        return self.display_name

# class ProductItems(models.Model):
#     IN_STOCK = 'in-stock'
#     OUT_OF_STOCK = 'out-of-stock'
#     PRE_ORDER = 'pre-order'
#     DISCONTINUED = 'discontinued'
    
#     STOCK_STATUS_CHOICES = [
#         (IN_STOCK, 'In Stock'),
#         (OUT_OF_STOCK, 'Out of Stock'),
#         (PRE_ORDER, 'Pre Order'),
#         (DISCONTINUED, 'Discontinued'),
#     ]

#     UNIT_CHOICES = [
#         ('250g', '250 gram'),
#         ('500g', '500 gram'),
#         ('1kg', '1 kilogram'),
#         ('1.25kg', '1.25 kilogram'),
#         ('1.50kg', '1.50 kilogram'),
#         ('1.75kg', '1.75 kilogram'),
#         ('2kg', '2 kilogram'),
#         ('2.25kg', '2.25 kilogram'),
#         ('2.50kg', '2.50 kilogram'),
#         ('5kg', '5 kilogram'),
#         # Add more choices as needed
#     ]

#     image = models.ImageField(upload_to='products')
#     hover_img = models.ImageField(upload_to='products', null=True)
#     title = models.CharField(max_length=100)
#     category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
#     description = RichTextField(null=True)  # Use RichTextField for rich text descriptions
#     status = models.CharField(max_length=50, null=True)
#     stock_status = models.CharField(
#         max_length=50,
#         choices=STOCK_STATUS_CHOICES,
#         null=True,
#         blank=True
#     )
#     rating = models.CharField(max_length=10, null=True)
#     rating_value = models.BigIntegerField(null=True)
#     price = models.DecimalField(decimal_places=2, null=True, max_digits=10)
#     vendor = models.CharField(max_length=100, null=True)
#     created = models.DateTimeField(null=True)
#     updated = models.DateTimeField(auto_now_add=True, null=True)
#     units = models.CharField(max_length=50, choices=UNIT_CHOICES, null=True, blank=True)
#     quantity = models.IntegerField(default=0)  # Add this field to track product quantity

from itertools import chain
from django.utils.text import slugify
import uuid

class ProductItems(models.Model):
    IN_STOCK = 'in-stock'
    OUT_OF_STOCK = 'out-of-stock'
    PRE_ORDER = 'pre-order'
    DISCONTINUED = 'discontinued'
    
    STOCK_STATUS_CHOICES = [
        (IN_STOCK, 'In Stock'),
        (OUT_OF_STOCK, 'Out of Stock'),
        (PRE_ORDER, 'Pre Order'),
        (DISCONTINUED, 'Discontinued'),
    ]

    image = models.ImageField(upload_to='products')
    hover_img = models.ImageField(upload_to='products', null=True)
    title = models.CharField(max_length=100)
    brand_items = models.ManyToManyField(BrandItem, related_name='products') 
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="products", null=True, blank=True)
    
    description = RichTextField(null=True)
    status = models.CharField(max_length=50, null=True)
    stock_status = models.CharField(max_length=50, choices=STOCK_STATUS_CHOICES, null=True, blank=True)
    rating = models.CharField(max_length=10, null=True,default="4.5")
    rating_value = models.BigIntegerField(null=True,default=95)
    price = models.DecimalField(decimal_places=2, null=True, max_digits=10)
    vendor = models.CharField(max_length=100, null=True,default="Beauty Centre")
    created = models.DateTimeField(null=True)
    updated = models.DateTimeField(auto_now_add=True, null=True)
    units = models.ManyToManyField(Unit, blank=True)
    quantity = models.IntegerField(default=0)

    # Additional fields
    type = models.CharField(max_length=100, null=True)
    mfg_date = models.DateField(null=True,blank=True)
    life_span = models.CharField(max_length=100, null=True,blank=True)
    sku = models.CharField(max_length=50, null=True, unique=True)
    tags = models.CharField(max_length=255, null=True)
    is_hidden = models.BooleanField(default=False)

    def get_all_images(self):
        return [self.image] + list(self.additional_images.all().values_list('image', flat=True))

    @property
    def updated_price(self):
        """Calculate the updated price for the product based on `CategoryPriceUpdate`."""
        latest_price_update = self.category.price_updates.order_by('-effective_date').first()
        if latest_price_update:
            return latest_price_update.calculate_updated_price(self.price)
        return self.price

    @property
    def discount(self):
        """Calculate bulk discount based on quantity and `CategoryBulkDiscount`."""
        discounted_price = self.updated_price
        for discount in self.category.bulk_discounts.order_by('-min_quantity'):
            if self.quantity >= discount.min_quantity:
                discount_amount = (discounted_price * discount.discount_percentage) / 100
                discounted_price -= discount_amount
                break
        return discounted_price

    @property
    def discount_percentage(self):
        """Calculate the discount percentage based on original and discounted prices."""
        if self.price and self.discount < self.price:
            return 100 * (self.price - self.discount) / self.price
        return 0

    @property
    def get_brand_items_display(self):
        """Return brand names as a comma-separated string."""
        return ", ".join([brand.title for brand in self.brand_items.all()])

    @property
    def selected_divisions(self):
        """Return distinct division names for the associated brand items."""
        divisions = set(chain.from_iterable(brand.divisions.all() for brand in self.brand_items.all()))
        return ", ".join([division.name for division in divisions])

    @property
    def selected_subdivisions(self):
        """Return distinct subdivision names for the associated brand items."""
        subdivisions = set(chain.from_iterable(brand.subdivisions.all() for brand in self.brand_items.all()))
        return ", ".join([subdivision.name for subdivision in subdivisions])


    def __str__(self):
        """Return a string representation of the product."""
        return f"{self.title} - {self.get_brand_items_display} - {self.category} - {self.price} - {self.vendor}"
  
    def save(self, *args, **kwargs):
        """Override the save method to generate a unique SKU."""
        if not self.sku:
            base_sku = slugify(self.title)
            unique_id = uuid.uuid4().hex[:8]  # Generate a unique 8-character ID
            self.sku = f"{base_sku}-{unique_id}".upper()  # Combine and ensure uppercase
        super().save(*args, **kwargs)    




class ProductBulkUploadSheet(models.Model):
    file = models.FileField(upload_to='bulk_uploads/', null=False, blank=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bulk Upload Sheet - {self.file.name}"
    # Optional: Model-level file validation
    def clean(self):
        if not self.file.name.endswith(('.xls', '.xlsx')):
            raise ValidationError("Please upload a valid Excel file with .xls or .xlsx extension")
        super().clean()




    

class ProductImage(models.Model):
    product = models.ForeignKey(ProductItems, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products')
    
    def __str__(self):
        return f"Image for {self.product.title}"

class CategoryPriceUpdate(models.Model):
    INCREASE = 'increase'
    DECREASE = 'decrease'

    ADJUSTMENT_TYPE_CHOICES = [
        (INCREASE, 'Increase'),
        (DECREASE, 'Decrease'),
    ]

    category = models.ForeignKey(Category, related_name='price_updates', on_delete=models.CASCADE)
    adjustment_type = models.CharField(max_length=10, choices=ADJUSTMENT_TYPE_CHOICES, null=True)
    adjustment_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=Decimal('0.00'))  # Ensure default value
    effective_date = models.DateTimeField(default=timezone.now, null=True)

    def calculate_updated_price(self, base_price):
        if base_price is None:
            base_price = Decimal('0.00')
        
        if self.adjustment_value is None:
            self.adjustment_value = Decimal('0.00')

        if self.adjustment_type == self.INCREASE:
            return base_price + (self.adjustment_value )
        elif self.adjustment_type == self.DECREASE:
            return base_price - ( self.adjustment_value )
        
        return base_price
    

    def __str__(self):
        return f"{self.adjustment_type}-{self.category}-{self.adjustment_value}"

class Billing_Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100,null=True)
    country=models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.EmailField()
    company_name=models.CharField(max_length=100,null=True)
    additional_info=models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.address}-{self.user}-{self.created}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


#========== Start Payment Model's with Prodcut wise ===============#
class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductItems, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product.title} - {self.quantity} - {self.added_at}"

class checkout(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cart_item = models.ForeignKey(CartItem, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}-{self.cart_item.product.title}-{self.added_at}- {'Items Quantity-',self.cart_item.quantity}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class PaymentStatus(models.TextChoices):
    PENDING = 'Pending', _('Pending')
    SUCCESS = 'Success', _('Success')
    FAILURE = 'Failure', _('Failure')

class DeliveryStatus(models.TextChoices):
    PENDING = 'Pending', _('Pending')
    PICKED_BY_COURIER = 'Picked by courier', _('Picked by courier')
    ON_THE_WAY = 'On the way', _('On the way')
    READY_FOR_PICKUP = 'Ready for pickup', _('Ready for pickup')
    DELIVERED = 'Delivered', _('Delivered')
    CANCELLED = 'Cancelled', _('Cancelled')

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment_status = models.CharField(
        max_length=50, 
        choices=PaymentStatus.choices, 
        default=PaymentStatus.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('ProductItems', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    ordered_address = models.ForeignKey('Billing_Address', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    urt_no = models.CharField(_("UTR No"), max_length=36, null=True, blank=True)
    payment_id = models.CharField(_("Payment ID"), max_length=36, null=True, blank=True)
    signature_id = models.CharField(_("Signature ID"), max_length=128, null=True, blank=True)
    invoice_number = models.CharField(_("Invoice Number"), max_length=11, unique=True, null=True, blank=True)
    tracking_id = models.CharField(_("Tracking ID"), max_length=14, unique=True, null=True, blank=True)
    provider_order_id = models.CharField(_("Order ID"), max_length=20, unique=True, null=True, blank=True)
    delivery_status = models.CharField(
        max_length=50,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING
    )
    successful_deliveries = models.IntegerField(default=0, editable=False)
    total_sales_per_day = models.FloatField(default=0.0, editable=False)
    
    @property
    def calculate_successful_deliveries(self):
        return OrderItem.objects.filter(delivery_status=DeliveryStatus.DELIVERED).count()

    @property
    def calculate_total_sales_per_day(self):
        sales = OrderItem.objects.filter(delivery_status=DeliveryStatus.DELIVERED).values('created_at__date').annotate(
            total_sales=Sum(F('quantity') * F('price'))
        ).order_by('created_at__date')
        return sum([sale['total_sales'] for sale in sales])
    
    def generate_unique_invoice_number(self):
        today = timezone.now().strftime('%Y%m%d')
        base_invoice_number = f"INV{today}"
        counter = 1
        invoice_number = base_invoice_number
        while OrderItem.objects.filter(invoice_number=invoice_number).exists():
            suffix = f"{counter:02d}"
            invoice_number = f"{base_invoice_number[:11-len(suffix)]}{suffix}"
            counter += 1
        return invoice_number

    def generate_unique_tracking_id(self):
        base_tracking_id = f"BD{str(uuid.uuid4().int)[:12]}"
        while OrderItem.objects.filter(tracking_id=base_tracking_id).exists():
            base_tracking_id = f"BD{str(uuid.uuid4().int)[:12]}"
        return base_tracking_id

    def generate_unique_provider_order_id(self):
        base_provider_order_id = uuid.uuid4().hex[:12]
        while OrderItem.objects.filter(provider_order_id=base_provider_order_id).exists():
            base_provider_order_id = uuid.uuid4().hex[:12]
        return base_provider_order_id

    def __str__(self):
        return f"OrderItem {self.id} - {self.product.title} - {self.quantity} - {self.price}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not self.invoice_number:
            self.invoice_number = self.generate_unique_invoice_number()
        if not self.tracking_id:
            self.tracking_id = self.generate_unique_tracking_id()
        if not self.provider_order_id:
            self.provider_order_id = self.generate_unique_provider_order_id()

        self.successful_deliveries = self.calculate_successful_deliveries
        self.total_sales_per_day = self.calculate_total_sales_per_day

        super().save(*args, **kwargs)

        if is_new:
            self.product.quantity -= self.quantity
            self.product.save()

        # if is_new:
        #     self.notify_admin()

    # def notify_admin(self):
    #     superuser = CustomUser.objects.filter(is_superuser=True).first()
    #     superuser_phone = None
    #     if superuser:
    #         user_phone = UserPhone.objects.filter(user=superuser).first()
    #         if user_phone:
    #             superuser_phone = user_phone.phone_no

    #     if not superuser_phone:
    #         superuser_phone = settings.ADMIN_WHATSAPP_NUMBER
        
    #     if superuser_phone:
    #         message_body = (
    #             f"Payment Received!\n"
    #             f"Order ID: {self.provider_order_id}\n"
    #             f"Product: {self.product.title}\n"
    #             f"Quantity: {self.quantity}\n"
    #             f"Price (Per Product): {self.price}\n"
    #             f'Total Price: {int(self.price) * int(self.quantity)}\n'
    #             f"Invoice Number: {self.invoice_number}\n"
    #             f"Tracking ID: {self.tracking_id}"
    #         )
    #         send_whatsapp_message(superuser_phone, message_body)

# Signal to handle adding back quantity when an order item is deleted
def order_item_delete(sender, instance, **kwargs):
    product = instance.product
    product.quantity += instance.quantity
    product.save()

post_delete.connect(order_item_delete, sender=OrderItem)


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductItems, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.title} - {self.added_at}"





#blog model
class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextField()  # Using CKEditor for rich text content
    published_date = models.DateTimeField(auto_now_add=True)
    read_time = models.PositiveIntegerField(help_text="Estimated time in minutes to read the blog")
    views = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)

    def __str__(self):
        return self.title




class DumpFileUpload(models.Model):
    file = models.FileField(upload_to='uploads/%Y/%m/%d/', null=True, blank=True)  # Adjust path as needed
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File: {self.file.name} (Uploaded at {self.uploaded_at})"

