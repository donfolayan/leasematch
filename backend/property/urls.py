from django.urls import path
from .views import(
    add_property,
    list_properties,
    get_property,
    update_property,
    delete_property,
)

urlpatterns = [
    path('create/', add_property, name='add-property'),
    path('list/', list_properties, name='list-properties'),
    path('list/<int:property_id>/', get_property, name='get-property'),
    path('update/<int:property_id>/', update_property, name='update-property'),
    path('delete/<int:property_id>/', delete_property, name='delete-property'),
]