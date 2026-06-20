from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import ReportForm
from .models import Report, ReportEvidence, ReportCategory
from accounts.models import AnonymousToken
from camps.utils import calculate_haversine_distance

def submit_report_view(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            
            # Anonymous token verification if guest
            anon_token = None
            if not request.user.is_authenticated:
                token_str = form.cleaned_data.get('token_str')
                if not token_str:
                    form.add_error('token_str', "You must provide a valid anonymous token to submit reports as a guest.")
                    return render(request, 'reports/submit_report.html', {'form': form})
                
                try:
                    anon_token = AnonymousToken.objects.get(token=token_str, is_used=False)
                    if anon_token.is_expired:
                        form.add_error('token_str', "This token has expired. Please request a new one.")
                        return render(request, 'reports/submit_report.html', {'form': form})
                except (AnonymousToken.DoesNotExist, ValueError):
                    form.add_error('token_str', "Invalid or already used anonymous token.")
                    return render(request, 'reports/submit_report.html', {'form': form})
                
                # Link anonymous token
                report.anonymous_token = anon_token
                # Submitter is anonymous
                report.user = None
            else:
                report.user = request.user

            # Duplicate Detection Logic
            # Same category, within last 24 hours, distance < 200m (0.2 km)
            time_threshold = timezone.now() - timezone.timedelta(hours=24)
            potential_duplicates = Report.objects.filter(
                incident_type=report.incident_type,
                created_at__gte=time_threshold
            )
            
            is_dup = False
            for r in potential_duplicates:
                dist = calculate_haversine_distance(
                    report.latitude, report.longitude,
                    r.latitude, r.longitude
                )
                if dist < 0.2:  # 0.2 km = 200 meters
                    is_dup = True
                    break
            
            report.is_possible_duplicate = is_dup
            report.save()

            # Mark token as used if anonymous
            if anon_token:
                anon_token.is_used = True
                anon_token.save()
                # Store token in session so the guest can track/view their report
                guest_reports = request.session.get('guest_reports', [])
                guest_reports.append(str(report.id))
                request.session['guest_reports'] = guest_reports

            # Process evidence files
            for file_field in ['evidence_1', 'evidence_2']:
                uploaded_file = form.cleaned_data.get(file_field)
                if uploaded_file:
                    ext = uploaded_file.name.split('.')[-1].lower()
                    file_type = 'video' if ext == 'mp4' else 'image'
                    ReportEvidence.objects.create(
                        report=report,
                        file=uploaded_file,
                        file_type=file_type
                    )

            if is_dup:
                messages.warning(
                    request,
                    "Your report has been submitted. Note: A similar report in this exact area was recently filed, and our system has marked this as a possible duplicate for review."
                )
            else:
                messages.success(request, "Incident report submitted successfully for moderation!")
                
            return redirect('reports:report_detail', pk=report.id)
    else:
        # Prepopulate coordinates if passed in GET params (from map clicking)
        initial_data = {}
        if 'lat' in request.GET and 'lon' in request.GET:
            initial_data['latitude'] = request.GET.get('lat')
            initial_data['longitude'] = request.GET.get('lon')
        form = ReportForm(initial=initial_data)

    return render(request, 'reports/submit_report.html', {'form': form})

def report_list_view(request):
    """
    Public listing of verified reports.
    """
    reports = Report.objects.filter(status='Verified', is_displayed=True).select_related('incident_type', 'user')
    categories = ReportCategory.objects.all()

    # Filters
    category_slug = request.GET.get('category')
    severity = request.GET.get('severity')
    date_filter = request.GET.get('date_range')

    if category_slug:
        reports = reports.filter(incident_type__slug=category_slug)
    if severity:
        reports = reports.filter(severity=severity)
        
    if date_filter:
        now = timezone.now()
        if date_filter == 'today':
            reports = reports.filter(created_at__date=now.date())
        elif date_filter == 'week':
            reports = reports.filter(created_at__gte=now - timezone.timedelta(days=7))
        elif date_filter == 'month':
            reports = reports.filter(created_at__gte=now - timezone.timedelta(days=30))

    context = {
        'reports': reports,
        'categories': categories,
        'selected_category': category_slug,
        'selected_severity': severity,
        'selected_date': date_filter,
    }
    return render(request, 'reports/report_list.html', context)

def report_detail_view(request, pk):
    """
    Display details of a report. Unverified reports are restricted to their author, 
    guest session holder, or staff.
    """
    report = get_object_or_404(Report, pk=pk)
    
    # Check permissions if not verified
    if report.status != 'Verified':
        has_permission = False
        if request.user.is_staff or request.user.is_superuser:
            has_permission = True
        elif report.user == request.user:
            has_permission = True
        elif str(report.id) in request.session.get('guest_reports', []):
            has_permission = True
            
        if not has_permission:
            # Mask the report existence or show permission error
            return render(request, '403.html', status=403)

    context = {
        'report': report,
        'evidence': report.evidence.all(),
    }
    return render(request, 'reports/report_detail.html', context)
