from django.urls import path
from . import views

urlpatterns = [
    # Inventory list / home page
    path('', views.home, name='inventory_list'),
    path('account-create/', views.account_create, name='account_create'),   # list page
    

    # Add item (admin only)
    path('add-item/', views.add_item, name='add_item'),

    # Item detail page
    path('details/<int:item_id>/', views.details, name='inventory_details'),

    # Collections page
    path('collection/<int:item_id>/', views.collection, name='collection'),
    path('collection/', views.collections, name='inventory_collection'), 
    # User authentication
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    #banner add
   path('banners/', views.banner_list, name='banner_list'),
   path('banners/add/', views.banner_add, name='banner_add'),
   path('banners/edit/<int:pk>/', views.banner_edit, name='banner_edit'),
   path('banners/delete/<int:pk>/', views.banner_delete, name='banner_delete'),
   path('checkout/<int:item_id>/', views.create_checkout, name='checkout'),
   path('payment/success/', views.payment_success, name='payment_success'),

    # ⚠️ Remove these until you actually define the views
    # path('update-item/<int:item_id>/', views.update_item, name='update_item'),
    # path('delete-item/<int:item_id>/', views.delete_item, name='delete_item'),
]
