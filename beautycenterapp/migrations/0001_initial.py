# Generated by Django 5.0.6 on 2024-09-21 04:13

import ckeditor.fields
import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('image', models.ImageField(upload_to='ads/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company_brand', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', ckeditor.fields.RichTextField()),
                ('published_date', models.DateTimeField(auto_now_add=True)),
                ('read_time', models.PositiveIntegerField(help_text='Estimated time in minutes to read the blog')),
                ('views', models.PositiveIntegerField(default=0)),
                ('image', models.ImageField(blank=True, null=True, upload_to='blog_images/')),
            ],
        ),
        migrations.CreateModel(
            name='brandItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('display_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone_number', models.CharField(max_length=15, unique=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Billing_Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=100)),
                ('address2', models.CharField(max_length=100, null=True)),
                ('country', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('pincode', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('company_name', models.CharField(max_length=100, null=True)),
                ('additional_info', models.TextField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='categories/')),
                ('created_at', models.DateTimeField(auto_now=True, null=True)),
                ('brand', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='brandName', to='beautycenterapp.branditem')),
            ],
        ),
        migrations.CreateModel(
            name='CategoryBulkDiscount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_quantity', models.PositiveIntegerField()),
                ('discount_percentage', models.PositiveIntegerField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bulk_discounts', to='beautycenterapp.category')),
            ],
        ),
        migrations.CreateModel(
            name='CategoryPriceUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adjustment_type', models.CharField(choices=[('increase', 'Increase'), ('decrease', 'Decrease')], max_length=10, null=True)),
                ('adjustment_value', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, null=True)),
                ('effective_date', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_updates', to='beautycenterapp.category')),
            ],
        ),
        migrations.CreateModel(
            name='checkout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('cart_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beautycenterapp.cartitem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_status', models.CharField(choices=[('Pending', 'Pending'), ('Success', 'Success'), ('Failure', 'Failure')], default='Pending', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProductItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products')),
                ('hover_img', models.ImageField(null=True, upload_to='products')),
                ('title', models.CharField(max_length=100)),
                ('description', ckeditor.fields.RichTextField(null=True)),
                ('status', models.CharField(max_length=50, null=True)),
                ('stock_status', models.CharField(blank=True, choices=[('in-stock', 'In Stock'), ('out-of-stock', 'Out of Stock'), ('pre-order', 'Pre Order'), ('discontinued', 'Discontinued')], max_length=50, null=True)),
                ('rating', models.CharField(max_length=10, null=True)),
                ('rating_value', models.BigIntegerField(null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('vendor', models.CharField(max_length=100, null=True)),
                ('created', models.DateTimeField(null=True)),
                ('updated', models.DateTimeField(auto_now_add=True, null=True)),
                ('quantity', models.IntegerField(default=0)),
                ('type', models.CharField(max_length=100, null=True)),
                ('mfg_date', models.DateField(null=True)),
                ('life_span', models.CharField(max_length=100, null=True)),
                ('sku', models.CharField(max_length=50, null=True)),
                ('tags', models.CharField(max_length=255, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='beautycenterapp.category')),
                ('units', models.ManyToManyField(blank=True, to='beautycenterapp.unit')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='additional_images', to='beautycenterapp.productitems')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('price', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('urt_no', models.CharField(blank=True, max_length=36, null=True, verbose_name='UTR No')),
                ('payment_id', models.CharField(blank=True, max_length=36, null=True, verbose_name='Payment ID')),
                ('signature_id', models.CharField(blank=True, max_length=128, null=True, verbose_name='Signature ID')),
                ('invoice_number', models.CharField(blank=True, max_length=11, null=True, unique=True, verbose_name='Invoice Number')),
                ('tracking_id', models.CharField(blank=True, max_length=14, null=True, unique=True, verbose_name='Tracking ID')),
                ('provider_order_id', models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name='Order ID')),
                ('delivery_status', models.CharField(choices=[('Pending', 'Pending'), ('Picked by courier', 'Picked by courier'), ('On the way', 'On the way'), ('Ready for pickup', 'Ready for pickup'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')], default='Pending', max_length=50)),
                ('successful_deliveries', models.IntegerField(default=0, editable=False)),
                ('total_sales_per_day', models.FloatField(default=0.0, editable=False)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='beautycenterapp.order')),
                ('ordered_address', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beautycenterapp.billing_address')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beautycenterapp.productitems')),
            ],
        ),
        migrations.AddField(
            model_name='cartitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beautycenterapp.productitems'),
        ),
        migrations.CreateModel(
            name='UserPhone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_no', models.CharField(blank=True, help_text='Enter your primary phone number', max_length=15, null=True, unique=True)),
                ('alternate_phone', models.CharField(blank=True, help_text='Enter an alternate phone number if any', max_length=15, null=True)),
                ('gst_no', models.CharField(blank=True, help_text='Enter an GST NO. if any', max_length=15, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beautycenterapp.productitems')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
