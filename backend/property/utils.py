from django.db.models import Q

def apply_property_filters(qs, request):
    """
    Helper function to apply filters to the property queryset.
    Filters include search, price range, property type, bedrooms, bathrooms,
    and sorting.

    Args:
        qs (QuerySet): The initial queryset of properties.
        request (HttpRequest): The request object containing query parameters.
    Returns:
        QuerySet: The filtered queryset of properties.
    """

    search = request.query_params.get('search')
    if search:
        qs = qs.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) | 
            Q(city__icontains=search) | 
            Q(state__icontains=search) |
            Q(address__icontains=search) |
            Q(property_type__iexact=search)
        )

    # Filter by price range
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    if min_price:
        qs = qs.filter(rent_price__gte=min_price)
    if max_price:
        qs = qs.filter(rent_price__lte=max_price)
    
    # Filter by property type
    property_type = request.query_params.get('property_type')
    if property_type:
        qs = qs.filter(property_type__iexact=property_type)

    # Filter by bedrooms
    bedrooms = request.query_params.get('bedrooms')
    if bedrooms:
        qs = qs.filter(bedrooms__iexact=bedrooms)
    
    # Filter by bathrooms
    bathrooms = request.query_params.get('bathrooms')
    if bathrooms:
        qs = qs.filter(bathrooms__iexact=bathrooms)
    
    # Sorting
    ordering = request.query_params.get('ordering', '-date_added')
    if ordering:
        qs = qs.order_by(ordering)
    return qs