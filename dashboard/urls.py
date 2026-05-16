from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static 

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('inventory/', views.inventory_dashboard, name='inventory_dashboard'),
    
    path('analysis/', views.analysis, name='analysis'),
    path('news/', views.news, name='news'),
    path("report/export/", views.export_report_excel, name="export_report_excel"),
    path("report/", views.report_page, name="report"),

    # delete item
    path('delete-item/<int:item_id>/', views.delete_item, name='delete_item'),

    # banners
    path('edit-banner/<int:banner_id>/', views.edit_banner, name='edit_banner'),
    path('delete-banner/<int:banner_id>/', views.delete_banner, name='delete_banner'),

    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # ✅ outside the list