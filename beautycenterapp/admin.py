from django.contrib import admin
from .models import *
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.urls import path

admin.site.register(CustomUser)

class BrandItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'categories_count','is_hidden']
    filter_horizontal = ('divisions', 'subdivisions', 'categories','subcategories')
    actions = ['hide_selected', 'show_selected'] 

    def categories_count(self, obj):
        return obj.categories_count

    categories_count.short_description = 'Number of Categories'
    # Action to hide selected BrandItem(s)
    def hide_selected(self, request, queryset):
        queryset.update(is_hidden=True)
        self.message_user(request, "Selected BrandItems have been hidden.")
    hide_selected.short_description = 'Hide selected BrandItems'

    # Action to show selected BrandItem(s)
    def show_selected(self, request, queryset):
        queryset.update(is_hidden=False)
        self.message_user(request, "Selected BrandItems are now visible.")
    show_selected.short_description = 'Show selected BrandItems'

class BrandItemInline(admin.TabularInline):
    model = BrandItem.divisions.through
    extra = 1

class DivisionAdmin(admin.ModelAdmin):
    inlines = [BrandItemInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('all_brands/', self.admin_site.admin_view(self.all_brands_view), name='all_brands'),
        ]
        return custom_urls + urls

    # Custom view to show all brands
    def all_brands_view(self, request):
        # Redirect to the BrandItem list page
        return HttpResponseRedirect(reverse('admin:beautycenterapp_branditem_changelist'))

    # Display a link to view all brands in the Division admin panel
    def all_brands_link(self, obj=None):
        # Show the "All Brands" link at the top
        return format_html('<a href="{}"><strong>All Brands</strong></a>', reverse('admin:all_brands'))

    all_brands_link.short_description = "All Brands"

    # Modify the list display to show "All Brands" at the top
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        # Adding a custom row for "All Brands" at the top
        extra_context['show_all_brands_link'] = True

        return super().changelist_view(request, extra_context=extra_context)

    # Add 'name' and 'all_brands_link' in list display
    list_display = ('name', 'all_brands_link')

    # Sorting name field
    def name(self, obj):
        return obj.name

    name.admin_order_field = 'name'


# Registering models in the admin
admin.site.register(BrandItem, BrandItemAdmin)
admin.site.register(Division, DivisionAdmin)
   

from django.contrib import admin
from .models import Category, SubCategory

# Admin action to hide selected categories
def hide_categories(modeladmin, request, queryset):
    queryset.update(is_hidden=True)
hide_categories.short_description = "Hide selected Categories"

# Admin action to unhide selected categories
def unhide_categories(modeladmin, request, queryset):
    queryset.update(is_hidden=False)
unhide_categories.short_description = "Unhide selected Categories"

# Admin action to hide selected subcategories
def hide_subcategories(modeladmin, request, queryset):
    queryset.update(is_hidden=True)
hide_subcategories.short_description = "Hide selected SubCategories"

# Admin action to unhide selected subcategories
def unhide_subcategories(modeladmin, request, queryset):
    queryset.update(is_hidden=False)
unhide_subcategories.short_description = "Unhide selected SubCategories"


# SubCategory Inline for CategoryAdmin
class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1  # How many extra blank forms to show for adding subcategories
    fk_name = 'category'


# CategoryAdmin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_hidden', 'product_count']
    search_fields = ['title']
    list_filter = ('is_hidden',) 
    actions = [hide_categories, unhide_categories] 
    inlines = [SubCategoryInline]


# SubCategoryAdmin
@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_hidden', 'created_at')
    search_fields = ('title', 'category__title')
    list_filter = ('is_hidden', 'category',)
    actions = [hide_subcategories, unhide_subcategories]




# admin.site.register(ProductItems)
@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name')
    search_fields = ('name', 'display_name')





# from .forms import*
# class ProductItemsForm(forms.ModelForm):
#     class Meta:
#         model = ProductItems
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Initially filter subcategories if category is preselected
#         if 'category' in self.data:
#             try:
#                 category_id = int(self.data.get('category'))
#                 self.fields['subcategory'].queryset = SubCategory.objects.filter(category_id=category_id)
#             except (ValueError, TypeError):
#                 pass  # Ignore invalid input and use default queryset
#         elif self.instance.pk and self.instance.category:
#             self.fields['subcategory'].queryset = SubCategory.objects.filter(category=self.instance.category)
#         else:
#             self.fields['subcategory'].queryset = SubCategory.objects.none()  # Empty queryset if no category selected

# class ProductItemsAdmin(admin.ModelAdmin):
#     form = ProductItemsForm
#     list_display = ('title', 'price', 'stock_status', 'category', 'subcategory')
#     search_fields = ('title', 'category', 'subcategory')
#     list_filter = ('stock_status', 'category')

#     class Media:
#         js = ('js/category_subcategory_filter.js',)  # Custom JavaScript for filtering subcategories based on category selection

# admin.site.register(ProductItems, ProductItemsAdmin)



from django import forms
from django.contrib import admin


admin.site.register(CartItem)
admin.site.register(Wishlist)
admin.site.register(ProductImage)
admin.site.register(checkout)
admin.site.register(Billing_Address)
admin.site.register(Order)
admin.site.register(CategoryBulkDiscount)
admin.site.register(CategoryPriceUpdate)
admin.site.register(Ads)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price', 'delivery_status', 'created_at')
    readonly_fields = ['successful_deliveries', 'total_sales_per_day']

    def successful_deliveries(self, obj):
        return obj.successful_deliveries
    successful_deliveries.short_description = 'Successful Deliveries'

    def total_sales_per_day(self, obj):
        return obj.total_sales_per_day
    total_sales_per_day.short_description = 'Total Sales Per Day'





@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'views')
    search_fields = ('title',)




class SubDivisionInline(admin.TabularInline):
    model = SubDivision
    extra = 1  # Number of extra forms in the admin

# class DivisionAdmin(admin.ModelAdmin):
#     list_display = ['name']
#     inlines = [SubDivisionInline]  # Inline for adding subdivisions directly in the division form

class SubDivisionAdmin(admin.ModelAdmin):
    list_display = ['name', 'division']
    list_filter = ['division']  # Filter by division

# admin.site.register(Division, DivisionAdmin)
admin.site.register(SubDivision, SubDivisionAdmin)


from .forms import ProductItemsAdminForm
from django.utils.safestring import mark_safe

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of empty forms to display for new related objects

@admin.register(ProductItems)
class ProductItemsAdmin(admin.ModelAdmin):
    form = ProductItemsAdminForm
    list_display = ["title", "category", "subcategory", "price", "stock_status", "is_hidden"]
    search_fields = ('title', 'category', 'subcategory')
    list_filter = ('stock_status', 'category')
    inlines = [ProductImageInline]
    
    readonly_fields = ('image_preview', 'hover_image_preview')

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img id="image-preview" src="{obj.image.url}" style="width: 150px; height: auto;" />')
        return mark_safe('<img id="image-preview" src="" style="display:none; width: 150px; height: auto;" />')

    def hover_image_preview(self, obj):
        if obj.hover_img:
            return mark_safe(f'<img id="hover-image-preview" src="{obj.hover_img.url}" style="width: 150px; height: auto;" />')
        return mark_safe('<img id="hover-image-preview" src="" style="display:none; width: 150px; height: auto;" />')
    # vendor, rating, rating_value,
    fieldsets = (
        (None, {
            
            'fields': ('image', 'image_preview', 'hover_img', 'hover_image_preview', 'title', 'brand_items', 'category', 'subcategory', 'price', 'stock_status','status', 'description','units','quantity','mfg_date','life_span', 'is_hidden')
        }),
    )

    class Media:
        js = ('admin/js/image_preview.js',)  # Include your custom JS file
        
#importing requires library 
import os
import shutil
import openpyxl
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import redirect
from .models import ProductItems, BrandItem, Category, SubCategory, Unit
    
class ProductBulkUploadSheetAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at')

    def save_model(self, request, obj, form, change):
        """Override save to trigger processing after file upload."""
        super().save_model(request, obj, form, change)

        # Process the Excel file after saving
        if obj.file:
            self.import_excel(request, obj.file)

    def handle_image_path(self, local_image_path):
        """Ensure image is copied to MEDIA_ROOT and return the relative path."""
        if not local_image_path:
            return None

        # Extract the file name from the provided local path
        image_name = os.path.basename(local_image_path)
        
        # Define the target directory inside MEDIA_ROOT
        target_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)  # Create the 'products' directory if it doesn't exist

        # Define the full target path for the image
        image_path = os.path.join(target_dir, image_name)

        # Check if the image exists at the provided local path
        if os.path.exists(local_image_path):
            # If the image exists locally, copy it to the 'products' directory within MEDIA_ROOT
            shutil.copy(local_image_path, image_path)
        else:
            raise ValidationError(f"Image '{local_image_path}' not found on the local machine.")

        # Return the relative path to store in the database (for use in ImageField)
        return os.path.join('products', image_name)  # This returns 'products/beautycenter.jpeg'

    def import_excel(self, request, excel_file):
        """Process the Excel file and create products in bulk."""
        try:
            # Load the workbook and active sheet using openpyxl
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active

            # Process the rows (skip header)
            #vendor, rating, rating_value,
            for row in sheet.iter_rows(min_row=2, values_only=True):
                title, sku, price, quantity, description, stock_status, image, hover_image,  mfg_date, life_span, tags, is_hidden, units, brand_name, category_name, sub_category_name = row

                # Handle image paths (use local paths provided in the sheet)
                image_path = self.handle_image_path(image) if image else None
                hover_image_path = self.handle_image_path(hover_image) if hover_image else None

                # Fetch or create the brand
                brand, _ = BrandItem.objects.get_or_create(title=brand_name)

                # Fetch or create the category
                category, _ = Category.objects.get_or_create(title=category_name)

                # Fetch or create the subcategory
                if category:
                    sub_category, _ = SubCategory.objects.get_or_create(title=sub_category_name, category=category)
                else:
                    raise ValidationError("Category not found for subcategory.")

                # Create or update the product item
                product, created = ProductItems.objects.update_or_create(
                    sku=sku,
                    defaults={
                        'title': title,
                        'price': price,
                        'quantity': quantity,
                        'description': description,
                        'stock_status': stock_status,
                        'image': image_path,
                        'hover_img': hover_image_path,
                        # 'vendor': vendor,
                        # 'rating': rating,
                        # 'rating_value': rating_value,
                        'mfg_date': mfg_date,
                        'life_span': life_span,
                        'tags': tags,
                        'is_hidden': is_hidden,
                        'category': category,
                        'subcategory': sub_category
                    }
                )

                # Add brand items to the product
                product.brand_items.add(brand)

                # Assign units (if any)
                if units:
                    units_list = units.split(", ")
                    for unit_name in units_list:
                        unit, _ = Unit.objects.get_or_create(name=unit_name)
                        product.units.add(unit)

            messages.success(request, "Products successfully imported!")
        except Exception as e:
            messages.error(request, f"Error processing the file: {str(e)}")

        return redirect("..")
        
# Register the admin classes
admin.site.register(ProductBulkUploadSheet, ProductBulkUploadSheetAdmin)

admin.site.register(DumpFileUpload)
        
