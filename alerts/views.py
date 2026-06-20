from django.shortcuts import render
from .models import Alert

def alert_list_view(request):
    """
    Public listing of active emergency notices, high-risk warnings, and missing person alerts.
    """
    alerts = Alert.objects.filter(is_active=True).order_by('-created_at')
    
    # Optional filters
    alert_type = request.GET.get('type')
    priority = request.GET.get('priority')
    
    if alert_type:
        alerts = alerts.filter(type=alert_type)
    if priority:
        alerts = alerts.filter(priority=priority)
        
    context = {
        'alerts': alerts,
        'selected_type': alert_type,
        'selected_priority': priority,
    }
    return render(request, 'alerts/alert_list.html', context)
