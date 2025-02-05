from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_product/', views.add_product, name='add_product'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('sub/category/<int:subcategory_id>/', views.subcategory_detail, name='subcategory_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('carts/', views.addCart, name='addCart'),
    path('<int:product_id>/add-cart/', views.add_to_cart, name='add_to_cart'),
    path('<int:cart_item_id>/remove_from_cart', views.remove_from_cart, name='remove_from_cart'),
    path('increase_quantity/<int:cart_item_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease_quantity/<int:cart_item_id>/', views.decrease_quantity, name='decrease_quantity'),

    path('removes/from/cart/', views.remove_all_from_cart, name='all_remove_from_cart'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('get_cart_and_wishlist_counts/', views.get_cart_and_wishlist_counts_view, name='get_cart_and_wishlist_counts'),
    path('<int:product_id>/add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('check-wishlist-status/', views.check_wishlist_status, name='check_wishlist_status'),
    path('<int:product_id>/remove-from-wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('<int:p_id>/product/detail/', views.product_detail, name='itemDetail'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('confirm-bank-transfer/', views.confirm_bank_transfer, name='confirm_bank_transfer'),
    path('get_invoice_details/<str:provider_order_id>/', views.get_invoice_details, name='get_invoice_details'),
    path('Order/track/', views.OrderTrack, name='orderTrack'),
    path('user/profile/edit/', views.update_user_profile, name='useredit'),
    path('user/password/change/', views.change_password, name='passchange'),
    path("success/", views.callback, name="callback"),
    path('account/', views.account, name='account'),
    path('admin/get_subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
    path('get-subcategories/', views.get_subcategories, name='get_subcategories'),
    path('division/<int:division_id>/', views.division_detail, name='division_detail'),

    



    path('products/market/', views.products_market, name='market'),
    path('<int:category_id>/products/market/', views.products_market, name='specific_market'),
    path('brand/<int:brand_id>/products/market/', views.products_market, name='brand_specific_market'),
    path('categories', views.items_categories, name='categories'),
    path('brands/', views.brand_filtered, name='brands'),
    path('brands/<str:name>/', views.brand_filtered_professional, name='brand_filtered_professional'),
    path('<int:pk>/brand/', views.brand_filtered, name='brandItem'),
    path('search/', views.search_items, name='search_items'),

    #------------ Auth URLs ------------
    path('account/login/', views.signin, name='signin'),
    path('account/register/', views.signup, name='signup'),
    path('account/signout/', views.signout, name='signout'),
    #------------ End Auth URLs ------------

    #Blog urls
    path('blogs/', views.blog_list, name='blog_list'),
    path('blogs/<int:id>/', views.blog_detail, name='blog_detail'),
    path('compare/<str:product_ids>/', views.compare_products, name='compare_products'),
    path('search-order/', views.search_order_by_id, name='search_order_by_id'),
    path("add-category/", views.add_category, name="add_category"),
    path("add-product/", views.add_product, name="add_Product"),
    path("add-subcategory/", views.add_subcategory, name="add_subCate"),
    path("add-brand/", views.add_brand, name="add_brand"),
    path('load-categories/', views.load_categories, name='load_categories'),
    path('load-categories/browser/', views.load_categories_browser, name='load_categories'),
    
    path('category/<int:p_id>/pdo/', views.category_pdo, name='category_pdo'),
    path('category/pdo/', views.category_pdo, name='category_pdo'),
]
