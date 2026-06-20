from django.shortcuts import render
from django.http import JsonResponse
from .models import BGBCamp
from .utils import calculate_haversine_distance

def nearest_camp_view(request):
    """
    Finds and displays BGB camps sorted by proximity to the user's location.
    Supports AJAX requests returning raw JSON.
    """
    user_lat = request.GET.get('lat')
    user_lon = request.GET.get('lon')
    
    camps = BGBCamp.objects.filter(operational_status='Active')
    camp_list = []
    
    has_coords = False
    if user_lat and user_lon:
        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
            has_coords = True
        except (ValueError, TypeError):
            pass

    for camp in camps:
        distance = None
        directions_url = f"https://www.google.com/maps/dir/?api=1&destination={camp.latitude},{camp.longitude}"
        
        if has_coords:
            distance = calculate_haversine_distance(user_lat, user_lon, camp.latitude, camp.longitude)
        
        camp_list.append({
            'id': camp.id,
            'name': camp.name,
            'district': camp.district,
            'phone': camp.phone,
            'latitude': float(camp.latitude),
            'longitude': float(camp.longitude),
            'distance': distance,
            'directions_url': directions_url
        })
        
    if has_coords:
        # Sort by distance (ascending)
        camp_list.sort(key=lambda x: x['distance'] if x['distance'] is not None else float('inf'))
    else:
        # Sort by name if no coordinates
        camp_list.sort(key=lambda x: x['name'])
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'success': True,
            'camps': camp_list[:10]  # Return top 10 nearest
        })
        
    context = {
        'camps': camp_list,
        'has_coords': has_coords,
        'user_lat': user_lat,
        'user_lon': user_lon,
    }
    return render(request, 'camps/nearest_camps.html', context)
