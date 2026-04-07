import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from dashboard.models import (
    Activity,
    DashboardLayout,
    DEFAULT_LAYOUTS,
    Metric,
    MetricHistory,
    Notification,
    UserProfile,
)


class Command(BaseCommand):
    help = "Seed the database with sample data for AdminPulse Pro dashboard"

    def handle(self, *args, **options):
        self.stdout.write("Seeding AdminPulse Pro database...")

        # Clear old data
        MetricHistory.objects.all().delete()
        Notification.objects.all().delete()
        DashboardLayout.objects.all().delete()
        Activity.objects.all().delete()
        Metric.objects.all().delete()

        # Create superuser
        if not User.objects.filter(username="admin").exists():
            admin_user = User.objects.create_superuser(
                username="admin",
                email="admin@adminpulse.dev",
                password="admin",
                first_name="Admin",
                last_name="User",
            )
            UserProfile.objects.update_or_create(
                user=admin_user,
                defaults={
                    "role": "admin",
                    "avatar": "https://ui-avatars.com/api/?name=Admin+User&background=6366f1&color=fff",
                },
            )
            self.stdout.write(self.style.SUCCESS("Created superuser: admin / admin"))
        else:
            admin_user = User.objects.get(username="admin")
            UserProfile.objects.get_or_create(
                user=admin_user,
                defaults={"role": "admin"},
            )
            self.stdout.write("Superuser 'admin' already exists.")

        # Create sample users with different roles
        sample_users = [
            ("jdoe", "John", "Doe", "manager"),
            ("asmith", "Alice", "Smith", "analyst"),
            ("bwilson", "Bob", "Wilson", "viewer"),
            ("cjones", "Carol", "Jones", "analyst"),
            ("dlee", "David", "Lee", "manager"),
        ]

        colors = ["6366f1", "0ea5e9", "10b981", "f59e0b", "ef4444", "8b5cf6"]
        users = [admin_user]
        for username, first, last, role in sample_users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "email": f"{username}@adminpulse.dev",
                },
            )
            if created:
                user.set_password("password123")
                user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "role": role,
                    "avatar": f"https://ui-avatars.com/api/?name={first}+{last}&background={random.choice(colors)}&color=fff",
                },
            )
            users.append(user)

        self.stdout.write(self.style.SUCCESS(f"Created {len(sample_users)} sample users"))

        # Create metrics
        metrics_data = [
            {
                "name": "Total Users",
                "value": Decimal("2847"),
                "previous_value": Decimal("2651"),
                "unit": "count",
                "icon": "users",
            },
            {
                "name": "Revenue",
                "value": Decimal("48295.50"),
                "previous_value": Decimal("42180.00"),
                "unit": "currency",
                "icon": "dollar-sign",
            },
            {
                "name": "Orders",
                "value": Decimal("1432"),
                "previous_value": Decimal("1389"),
                "unit": "count",
                "icon": "shopping-cart",
            },
            {
                "name": "Growth",
                "value": Decimal("14.5"),
                "previous_value": Decimal("11.2"),
                "unit": "percent",
                "icon": "trending-up",
            },
        ]

        metrics = []
        for data in metrics_data:
            metric, _ = Metric.objects.update_or_create(name=data["name"], defaults=data)
            metrics.append(metric)

        self.stdout.write(self.style.SUCCESS(f"Created {len(metrics_data)} metrics"))

        # Create 90 days of MetricHistory for each metric
        now = timezone.now()
        history_count = 0
        for metric in metrics:
            base_value = float(metric.value)
            for day in range(90, 0, -1):
                recorded = now - timedelta(days=day)
                # Create a realistic trend with some randomness
                factor = 1.0 - (day / 90) * 0.3  # gradual increase over time
                noise = random.uniform(0.85, 1.15)
                value = round(base_value * factor * noise, 2)
                MetricHistory.objects.create(
                    metric=metric,
                    value=Decimal(str(value)),
                    recorded_at=recorded,
                )
                history_count += 1

        self.stdout.write(self.style.SUCCESS(f"Created {history_count} metric history entries"))

        # Create activities
        actions = [
            ("Created new account", "User Registration"),
            ("Updated profile settings", "User Profile"),
            ("Placed an order", "Order #{}"),
            ("Generated report", "Monthly Analytics"),
            ("Updated product listing", "Product #{}"),
            ("Processed refund", "Order #{}"),
            ("Added team member", "Team Management"),
            ("Changed password", "Security Settings"),
            ("Exported data", "CSV Export"),
            ("Modified permissions", "Role Management"),
            ("Uploaded document", "File Storage"),
            ("Sent notification", "Email Campaign"),
            ("Resolved support ticket", "Ticket #{}"),
            ("Approved request", "Request #{}"),
            ("Deployed update", "Version 2.1.{}"),
        ]

        for i in range(50):
            action_template, target_template = random.choice(actions)
            target = target_template.format(random.randint(1000, 9999))
            Activity.objects.create(
                user=random.choice(users),
                action=action_template,
                target=target,
                timestamp=now - timedelta(
                    hours=random.randint(0, 168),
                    minutes=random.randint(0, 59),
                ),
            )

        self.stdout.write(self.style.SUCCESS("Created 50 activity entries"))

        # Create notifications for each user
        notification_templates = [
            ("info", "New feature: Dashboard customization is now available"),
            ("success", "Your export completed successfully"),
            ("warning", "Storage usage is approaching 80% of your limit"),
            ("error", "Failed to sync data with external API"),
            ("info", "Team member {} joined the workspace"),
            ("success", "Monthly report generated for March 2026"),
            ("warning", "API rate limit will be reached in 2 hours"),
            ("info", "System maintenance scheduled for this weekend"),
            ("success", "Backup completed successfully"),
            ("error", "Payment processing error on Order #{}"),
        ]

        notif_count = 0
        for user in users:
            num_notifications = random.randint(5, 10)
            for i in range(num_notifications):
                ntype, msg_template = random.choice(notification_templates)
                message = msg_template.format(random.choice(["Alice", "Bob", "Carol", str(random.randint(1000, 9999))]))
                Notification.objects.create(
                    user=user,
                    message=message,
                    notification_type=ntype,
                    is_read=random.choice([True, False, False]),  # 2/3 unread
                    created_at=now - timedelta(
                        hours=random.randint(0, 72),
                        minutes=random.randint(0, 59),
                    ),
                )
                notif_count += 1

        self.stdout.write(self.style.SUCCESS(f"Created {notif_count} notifications"))

        # Create default dashboard layouts for each user
        layout_count = 0
        for user in users:
            try:
                role = user.profile.role
            except UserProfile.DoesNotExist:
                role = "viewer"
            default = DEFAULT_LAYOUTS.get(role, DEFAULT_LAYOUTS["viewer"])
            DashboardLayout.objects.update_or_create(
                user=user,
                defaults={"layout": default},
            )
            layout_count += 1

        self.stdout.write(self.style.SUCCESS(f"Created {layout_count} dashboard layouts"))

        self.stdout.write(self.style.SUCCESS("\nAdminPulse Pro seeding complete!"))
        self.stdout.write("Login credentials:")
        self.stdout.write("  admin / admin (Administrator)")
        self.stdout.write("  jdoe / password123 (Manager)")
        self.stdout.write("  asmith / password123 (Analyst)")
        self.stdout.write("  bwilson / password123 (Viewer)")
