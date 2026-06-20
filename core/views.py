from django.shortcuts import render
from django.db.models import Count
from reports.models import Report, ReportCategory
from alerts.models import Alert
from camps.models import BGBCamp

def home_view(request):
    """
    Renders the platform homepage featuring:
    1. Incident visualizer map (Leaflet.js)
    2. Active notices and emergency alerts
    3. Quick emergency nearest camp calculator interface
    4. General statistics (categories, severity)
    """
    # Active notices
    active_alerts = Alert.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    # Verified reports to render on Leaflet Map
    verified_reports = Report.objects.filter(status='Verified').select_related('incident_type')
    
    # Gather statistics
    total_incidents = verified_reports.count()
    categories = ReportCategory.objects.all()
    camps_count = BGBCamp.objects.filter(operational_status='Active').count()

    context = {
        'alerts': active_alerts,
        'reports': verified_reports,
        'categories': categories,
        'total_incidents': total_incidents,
        'camps_count': camps_count,
    }
    return render(request, 'core/home.html', context)

def about_view(request):
    return render(request, 'core/about.html')

def safety_guidelines_view(request):
    return render(request, 'core/guidelines.html')

def contact_view(request):
    return render(request, 'core/contact.html')

def faq_view(request):
    return render(request, 'core/faq.html')
