import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borderwatch.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile
from reports.models import ReportCategory
from camps.models import BGBCamp
from alerts.models import Alert

def seed_data():
    print("Seeding database...")

    # 1. Create Superuser
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser('admin', 'admin@borderwatchbd.org', 'adminpassword123')
        # Create profile for admin
        Profile.objects.create(
            user=admin_user,
            role='witness',
            phone='+8801700000000',
            nid='19990000000000000',
            district='Dhaka',
            is_verified=True
        )
        print("Superuser created! Username: admin, Password: adminpassword123")
    else:
        print("Superuser 'admin' already exists.")

    # 2. Create Categories
    categories = [
        ("Illegal Push-in Attempts", "illegal-push-in", "Reports of unauthorized groups attempting to cross the border fence or zero-line."),
        ("Human Trafficking", "human-trafficking", "Suspicious gatherings or movements suggesting illegal transport of people across the border."),
        ("Smuggling", "smuggling", "Illegal trade of goods, contraband, weapons, drugs, or cattle across border boundaries."),
        ("Border Violence", "border-violence", "Active conflict, firing, border guard clashes, or civilian injury reports near the border."),
        ("Missing Persons", "missing-persons", "Civilians who went missing or were last seen near the border fence or zero-line."),
        ("Illegal Crossings", "illegal-crossings", "Unauthorized individual crossings without proper legal transit documents."),
        ("Suspicious Movements", "suspicious-movements", "Strange activities, night signals, or unidentified vehicles near the border lines."),
    ]

    for name, slug, desc in categories:
        cat, created = ReportCategory.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'description': desc}
        )
        if created:
            print(f"Created category: {name}")

    # 3. Create BGB Camps
    # Real coordinate positions along the Bangladesh border regions
    camps = [
        ("Phulbari BGB Camp", "Kurigram", "+8801769600100", 25.8300, 89.6500),
        ("Benapole BGB Camp", "Jessore", "+8801769600101", 23.0400, 88.8900),
        ("Hili BGB Camp", "Dinajpur", "+8801769600102", 25.2811, 89.0233),
        ("Teknaf BGB Camp", "Cox's Bazar", "+8801769600103", 20.8600, 92.3000),
        ("Tamabil BGB Camp", "Sylhet", "+8801769600104", 25.1764, 92.0833),
        ("Akhaura BGB Camp", "Brahmanbaria", "+8801769600105", 23.8833, 91.2500),
        ("Rohanpur BGB Camp", "Chapainawabganj", "+8801769600106", 24.8167, 88.3333),
    ]

    for name, district, phone, lat, lon in camps:
        camp, created = BGBCamp.objects.get_or_create(
            name=name,
            defaults={
                'district': district,
                'phone': phone,
                'latitude': lat,
                'longitude': lon,
                'operational_status': 'Active'
            }
        )
        if created:
            print(f"Created camp: {name} ({district})")

    # 4. Create Active Alerts
    alerts = [
        ("High Smuggling Warning - Kurigram Border", 
         "Increased night smuggling activities reported near Phulbari border. Local residents and transport workers are advised to restrict movement near the fence after 10 PM.", 
         "danger_warning", "High"),
        ("Missing Person - Sylhet Border Area", 
         "A 24-year old farmer, last seen tending to crops near Tamabil zero-line, went missing yesterday. If you have information or witnessed any BSF movement, report it immediately.", 
         "missing_person", "Critical"),
        ("Night Fencing Check Warning", 
         "Routine fence checks and patrols will be intensified by BGB along Jessore borders. Carry your NIDs at all times.", 
         "general_alert", "Medium")
    ]

    for title, desc, alert_type, priority in alerts:
        alert, created = Alert.objects.get_or_create(
            title=title,
            defaults={
                'description': desc,
                'type': alert_type,
                'priority': priority,
                'is_active': True
            }
        )
        if created:
            print(f"Created alert: {title}")

    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_data()
