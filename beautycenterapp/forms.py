from django import forms
from .models import *
    
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude=['created_at']

class subCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        exclude=['created_at']


class BrandItemForm(forms.ModelForm):
    class Meta:
        model = BrandItem
        fields = [
             'title', 'image', 'divisions', 'subdivisions', 'categories', 'subcategories',
        ]


# forms.py
from django import forms
from .models import ProductItems, SubCategory

# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = ProductItems
#         fields = ['category', 'subcategory', 'title', 'description', 'price', 'image']

#     def __init__(self, *args, **kwargs):
#         super(ProductForm, self).__init__(*args, **kwargs)
        
#         # Initially, set subcategory queryset to empty if no category is selected
#         if 'category' in self.data:
#             try:
#                 category_id = int(self.data.get('category'))
#                 self.fields['subcategory'].queryset = SubCategory.objects.filter(category_id=category_id)
#             except (ValueError, TypeError):
#                 self.fields['subcategory'].queryset = SubCategory.objects.none()
#         elif self.instance.pk:
#             # When editing an existing ProductItem, populate subcategory based on the saved category
#             self.fields['subcategory'].queryset = SubCategory.objects.filter(category=self.instance.category)
#         else:
#             # Initially empty if no category is selected yet
#             self.fields['subcategory'].queryset = SubCategory.objects.none()

from django import forms
from .models import ProductItems, Category, SubCategory

class ProductItemsForm(forms.ModelForm):
    class Meta:
        model = ProductItems
        fields = ['title', 'price', 'stock_status', 'category', 'subcategory']

    subcategory = forms.ModelChoiceField(queryset=SubCategory.objects.none(), required=False)

    # Override __init__ to filter subcategories based on selected category
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        category = self.initial.get('category') or self.instance.category
        if category:
            self.fields['subcategory'].queryset = SubCategory.objects.filter(category=category)




class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductItems
        fields = [
            'image', 'hover_img', 'title', 'brand_items', 'category', 'subcategory',
            'description', 'status', 'stock_status', 'rating', 'rating_value', 'price',
            'vendor', 'units', 'quantity', 'mfg_date', 'is_hidden'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
            'mfg_date': forms.DateInput(attrs={'type': 'date'}),
            'created': forms.DateInput(attrs={'type': 'datetime-local'}),
            'updated': forms.DateInput(attrs={'type': 'datetime-local'}),
            'brand_items': forms.SelectMultiple(),
            'units': forms.SelectMultiple(),
            'is_hidden':forms.CheckboxInput(attrs={'class':'form-checkbox-input'})
        }

    def clean_price(self):
        """
        Custom validation for the price field.
        Ensure that the price is a non-negative value.
        """
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("The price cannot be negative.")
        return price

    def clean_quantity(self):
        """
        Custom validation for the quantity field.
        Ensure that the quantity is a non-negative integer.
        """
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 0:
            raise forms.ValidationError("The quantity cannot be negative.")
        return quantity
    
from django_select2.forms import Select2Widget, ModelSelect2Widget

class CategorySelectWidget(ModelSelect2Widget):
    model = Category
    search_fields = ["title__icontains"]

class SubCategorySelectWidget(ModelSelect2Widget):
    model = SubCategory
    search_fields = ["title__icontains"]

    # Filter SubCategory queryset based on selected Category
    def filter_queryset(self, request, term, queryset, **dependent_fields):
        category_id = dependent_fields.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset
        

class ProductItemsAdminForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=ModelSelect2Widget(
            model=Category,
            search_fields=['title__icontains'],  # Search is still enabled but not required
            attrs={
                'data-minimum-input-length': 0  # Show all options by default
            }
        )
    )
    subcategory = forms.ModelChoiceField(
        queryset=SubCategory.objects.all(),
        widget=ModelSelect2Widget(
            model=SubCategory,
            search_fields=['title__icontains'],
            dependent_fields={'category': 'category'},  # Filters based on the selected category
            attrs={
                'data-minimum-input-length': 0  # Show all options by default
            }
        )
    )

    class Meta:
        model = ProductItems
        fields = "__all__"

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
        
    #     # Populate subcategory queryset based on the instance or data
    #     if "category" in self.data:
    #         try:
    #             category_id = int(self.data.get("category"))
    #             self.fields["subcategory"].queryset = SubCategory.objects.filter(category__id=category_id)
    #         except (ValueError, TypeError):
    #             self.fields["subcategory"].queryset = SubCategory.objects.none()
    #     elif self.instance.pk and self.instance.category:
    #         self.fields["subcategory"].queryset = SubCategory.objects.filter(category=self.instance.category)
    #     else:
    #         self.fields["subcategory"].queryset = SubCategory.objects.none()