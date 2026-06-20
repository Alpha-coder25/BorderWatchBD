from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from reports.models import Report, ReportCategory
from accounts.models import Profile
from .forms import AdminUserEditForm
from .models import VerificationLog

@login_required
def user_dashboard_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    reports = request.user.reports.all().order_by('-created_at')

    context = {
        'profile': profile,
        'reports': reports,
    }
    return render(request, 'dashboard/user_dashboard.html', context)


@staff_member_required
def admin_dashboard_view(request):
    """
    Main admin dashboard showing statistics, pending moderation items,
    general user management, and report publication controls.
    """
    total_reports = Report.objects.count()
    pending_reports = Report.objects.filter(status='Pending').order_by('is_possible_duplicate', '-priority_score')
    verified_reports_count = Report.objects.filter(status='Verified').count()
    escalated_reports_count = Report.objects.filter(status='Escalated').count()
    rejected_reports_count = Report.objects.filter(status='Rejected').count()

    general_users = Profile.objects.select_related('user').filter(user__is_staff=False)
    general_users_count = general_users.count()
    public_reports = Report.objects.filter(status='Verified', is_displayed=True).order_by('-created_at')
    verified_reports = Report.objects.filter(status='Verified').order_by('-created_at')
    
    # Priority reports queue
    high_priority_count = Report.objects.filter(is_priority=True, status='Pending').count()
    possible_duplicates_count = Report.objects.filter(is_possible_duplicate=True, status='Pending').count()

    # Category distribution stats
    category_stats = Report.objects.values('incident_type__name').annotate(
        total=Count('id'),
        verified=Count('id', filter=Q(status='Verified')),
        pending=Count('id', filter=Q(status='Pending'))
    ).order_by('-total')

    # Severity distribution
    severity_stats = Report.objects.values('severity').annotate(total=Count('id')).order_by('-total')

    # Calculate District Risk Scores for last 30 days
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    recent_reports = Report.objects.filter(status='Verified', created_at__gte=thirty_days_ago)
    
    # We group by district (or coordinate clusters)
    # Since reports have district in profiles, or we can use latitude/longitude and group by district name
    # Let's group by report title/location if it contains district or group by report's user profile district
    # Let's count risk scores grouped by district from user profiles, or based on coordinates (mocking districts)
    # A cleaner way: Django Report model doesn't have a direct "district" field, but we can compute it using some coordinates mapping
    # OR we can extract the district field if it is written in descriptions or titles, OR we can check user.profile.district
    # Let's write a simple query grouping by user's profile district and calculating risk score:
    # Risk Score = Sum(Verified Reports * Weight) / 30
    
    severity_weights = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 5}
    district_reports = recent_reports.values('user__profile__district').annotate(
        report_count=Count('id'),
    )
    
    # Since user profile district might be null (or anonymous report), let's fallback to report coordinates-based districts
    # Or let's group by the reporter's profile district.
    risk_scores = []
    for dist_entry in district_reports:
        dist_name = dist_entry['user__profile__district'] or "Unknown / Border Region"
        
        # Calculate sum of weights for this district manually
        reports_in_dist = recent_reports.filter(
            Q(user__profile__district=dist_entry['user__profile__district']) if dist_entry['user__profile__district'] 
            else Q(user__profile__district__isnull=True)
        )
        
        weighted_sum = 0
        for r in reports_in_dist:
            weighted_sum += severity_weights.get(r.severity, 2)
            
        risk_score = round(weighted_sum / 30.0, 3)  # Per day over 30 days
        risk_scores.append({
            'district': dist_name,
            'count': reports_in_dist.count(),
            'score': risk_score
        })
        
    risk_scores.sort(key=lambda x: x['score'], reverse=True)

    context = {
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'verified_reports_count': verified_reports_count,
        'escalated_reports_count': escalated_reports_count,
        'rejected_reports_count': rejected_reports_count,
        'high_priority_count': high_priority_count,
        'possible_duplicates_count': possible_duplicates_count,
        'category_stats': category_stats,
        'severity_stats': severity_stats,
        'risk_scores': risk_scores,
        'general_users': general_users,
        'general_users_count': general_users_count,
        'public_reports': public_reports,
        'verified_reports': verified_reports,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@staff_member_required
def moderate_report_view(request, pk):
    """
    Handle changes to report status, updating scores, and writing to verification log.
    """
    report = get_object_or_404(Report, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status in dict(Report.STATUS_CHOICES).keys():
            old_status = report.status
            report.status = new_status
            
            # If admin updates urgency or severity in moderation
            mod_severity = request.POST.get('severity')
            if mod_severity in dict(Report.SEVERITY_CHOICES).keys():
                report.severity = mod_severity
                
            report.is_displayed = True if new_status == 'Verified' else False
            report.save()  # Triggers priority recalculation
            
            # Log moderation action
            VerificationLog.objects.create(
                report=report,
                admin_user=request.user,
                previous_status=old_status,
                new_status=new_status,
                notes=notes
            )
            
            messages.success(request, f"Report #{report.id} successfully updated to '{new_status}'.")
        else:
            messages.error(request, "Invalid status change requested.")
            
        return redirect('dashboard:admin_dashboard')

    return render(request, 'dashboard/moderate_report.html', {'report': report})

@staff_member_required
def toggle_report_display_view(request, pk):
    report = get_object_or_404(Report, pk=pk)
    
    if request.method == 'POST':
        if report.status != 'Verified':
            report.is_displayed = False
            report.save()
            messages.warning(request, "Only verified reports can be displayed publicly. This report has been hidden.")
        else:
            report.is_displayed = not report.is_displayed
            report.save()
            if report.is_displayed:
                messages.success(request, f"Report #{report.id} is now visible on the public website.")
            else:
                messages.success(request, f"Report #{report.id} has been hidden from public view.")
    return redirect('dashboard:admin_dashboard')


@staff_member_required
def edit_user_view(request, pk):
    user_obj = get_object_or_404(User, pk=pk, is_staff=False)
    profile_obj, _ = Profile.objects.get_or_create(user=user_obj)

    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user_obj, profile_instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"User {user_obj.username} updated successfully.")
            return redirect('dashboard:admin_dashboard')
    else:
        form = AdminUserEditForm(instance=user_obj, profile_instance=profile_obj)

    return render(request, 'dashboard/edit_user.html', {'form': form, 'user_obj': user_obj})


def heatmap_data_api(request):
    """
    JSON API returning coordinates of reports for rendering Leaflet Heatmaps.
    Only returns verified and displayed reports.
    """
    # Severity weights for heatmap rendering intensity
    severity_weights = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 5}
    
    reports = Report.objects.filter(status='Verified', is_displayed=True)
    
    features = []
    for r in reports:
        features.append({
            'lat': float(r.latitude),
            'lng': float(r.longitude),
            'count': severity_weights.get(r.severity, 2)
        })
        
    return JsonResponse({
        'success': True,
        'data': features
    })
