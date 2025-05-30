from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .serializers import PropertySerializer
from .models import Property
from .filter_property import apply_property_filters

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_property(request):
    """
    Endpoint to add a new property listing.
    Only landlords and agents can add properties.
    """
    user = request.user
    if user.user_type not in ['landlord', 'agent']:
        return Response({"message": "Invalid User Type"}, status=403)
    
    data = request.data
    serializer = PropertySerializer(data=data)
    if serializer.is_valid():
        property = serializer.save(uploader=user, uploader_user_type=user.user_type)
        return Response({"success": True, "message": "Property Successfully Added", "property_id": property.id}, status=201)
    else:
        return Response({"success": False, "message": "Property Not Added", "errors": serializer.errors}, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_properties(request):
    """
    Endpoint to list properties for all users.
    Query Parameters:
    - search: Search by title, description, city, or state.
    - min_price: Minimum price filter.
    - max_price: Maximum price filter.
    - property_type: Filter by property type.
    - bedrooms: Filter by number of bedrooms.
    - bathrooms: Filter by number of bathrooms.
    - ordering: Order by a specific field.
    """
    qs = Property.objects.all()
    qs = apply_property_filters(qs, request)
    if qs.count() == 0:
        return Response({"message": "No search matches your parameter, please try again with new filters"}, status=404)
    else:
        serializer = PropertySerializer(qs, many=True)
        return Response({"properties": serializer.data}, status=200)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_property(request, property_id):
    """
    Endpoint to update a property listing.
    Only landlords and agents can update properties.
    """
    user = request.user
    if user.user_type not in ['landlord', 'agent']:
        return Response({"message": "Invalid User Type"}, status=403)
    
    try:
        property = Property.objects.get(id=property_id, uploader=user)
    except Property.DoesNotExist:
        return Response({"message": "Property Not Found"}, status=404)
    
    serializer = PropertySerializer(property, data=request.data, partial=True)
    if serializer.is_valid():
        property = serializer.save()
        return Response({"success": True, 
                         "message": "Property Successfully Updated", 
                         "property_id": property.id}, 
                         status=200)
    else:
        return Response({"success": False, 
                         "message": "Property Not Updated", 
                         "errors": serializer.errors}, 
                         status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_property(request, property_id):
    """
    Endpoint to get a specific property listing.
    """
    user = request.user
    try:
        property = Property.objects.get(id=property_id, uploader=user)
    except Property.DoesNotExist:
        return Response({"message": "Property Not Found"}, status=404)
    
    serializer = PropertySerializer(property)
    return Response({"property": serializer.data}, status=200)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_property(request, property_id):
    """
    Endpoint to delete a property listing.
    Only landlords and agents can delete properties.
    """
    user = request.user
    if user.user_type not in ['landlord', 'agent']:
        return Response({"message": "Invalid User Type"}, status=403)
    
    try:
        property = Property.objects.get(id=property_id, uploader=user)
    except Property.DoesNotExist:
        return Response({"message": "Property Not Found"}, status=404)
    property.delete()
    return Response(status=204)
