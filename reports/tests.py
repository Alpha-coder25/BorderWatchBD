from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from reports.models import Report, ReportCategory
from camps.utils import calculate_haversine_distance

class BorderWatchMathAndLogicTestCase(TestCase):
    def setUp(self):
        # Setup category
        self.category = ReportCategory.objects.create(
            name="Smuggling",
            slug="smuggling",
            description="Illegal trading of contraband."
        )
        
        # Setup users
        self.standard_user = User.objects.create_user(
            username="reporter1",
            password="testpassword123",
            email="reporter@test.com"
        )
        
        # Setup verified user
        self.verified_user = User.objects.create_user(
            username="verified_rep",
            password="testpassword123",
            email="verified@test.com"
        )
        self.verified_user.profile.is_verified = True
        self.verified_user.profile.save()

    def test_haversine_distance_calculation(self):
        """
        Verify the Haversine distance formula against known coordinates.
        Point A (Dhaka): 23.8103, 90.4125
        Point B (Chittagong): 22.3569, 91.7832
        Expected distance is approximately 242 km.
        """
        dhaka = (23.8103, 90.4125)
        chittagong = (22.3569, 91.7832)
        dist = calculate_haversine_distance(dhaka[0], dhaka[1], chittagong[0], chittagong[1])
        
        self.assertAlmostEqual(dist, 242.8, delta=5.0)

    def test_priority_score_calculation(self):
        """
        Verify priority score logic: Priority = Severity Weight * Urgency * Credibility.
        - Critical weight = 5
        - Urgency = 5
        - Verified user credibility = 5
        Expected priority score = 125, is_priority = True
        """
        report = Report.objects.create(
            user=self.verified_user,
            incident_type=self.category,
            title="Critical smuggling attempt",
            description="Large group crossing fence.",
            latitude=25.8300,
            longitude=89.6500,
            severity="Critical",
            urgency=5
        )
        # Verify credibility set to 5 for verified user
        self.assertEqual(report.credibility, 5)
        # Priority score = 5 * 5 * 5 = 125
        self.assertEqual(report.priority_score, 125)
        self.assertTrue(report.is_priority)

    def test_priority_score_low_severity(self):
        """
        - Low weight = 1
        - Urgency = 2
        - Anonymous credibility = 2
        Expected priority score = 4, is_priority = False
        """
        report = Report.objects.create(
            user=None,  # Anonymous
            incident_type=self.category,
            title="Small crossing suspicion",
            description="Someone walking near the boundary.",
            latitude=25.8300,
            longitude=89.6500,
            severity="Low",
            urgency=2
        )
        # Anonymous credibility default = 2
        self.assertEqual(report.credibility, 2)
        # Priority score = 1 * 2 * 2 = 4
        self.assertEqual(report.priority_score, 4)
        self.assertFalse(report.is_priority)

    def test_duplicate_detection_logic(self):
        """
        Test that a report submitted in close range (<200m) of another in the last 24h
        is identified as a potential duplicate.
        """
        # First report
        report1 = Report.objects.create(
            user=self.standard_user,
            incident_type=self.category,
            title="Smuggling event",
            description="Contraband movement seen.",
            latitude=25.8300,
            longitude=89.6500,
            severity="Medium",
            urgency=3
        )
        
        # Second report submitted within 50 meters, same category
        # 25.8301, 89.6501 is extremely close to 25.8300, 89.6500
        # Let's mock a duplicate check inside a submission simulation
        lat2, lon2 = 25.8301, 89.6501
        
        # Check duplicate
        time_threshold = timezone.now() - timezone.timedelta(hours=24)
        potential_duplicates = Report.objects.filter(
            incident_type=self.category,
            created_at__gte=time_threshold
        )
        
        is_dup = False
        for r in potential_duplicates:
            dist = calculate_haversine_distance(lat2, lon2, r.latitude, r.longitude)
            if dist < 0.2:  # 200m
                is_dup = True
                break
                
        self.assertTrue(is_dup)
