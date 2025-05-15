from django.urls import path
from .views import(
    add_property,
    list_properties,
    update_property,
    delete_property,
)

urlpatterns = [
    path('properties/', add_property, name='add-property'),
    path('properties/list/', list_properties, name='list-properties'),
    path('properties/update/<int:property_id>/', update_property, name='update-property'),
    path('properties/delete/<int:property_id>/', delete_property, name='delete-property'),
]