from django.core.management.base import BaseCommand

from apps.locations.models import Location


MOCKUP_LOCATIONS = [
    {
        "name": "ساحة بلدية الخليل",
        "latitude": 31.5326,
        "longitude": 35.0998,
        "radius_meters": 15,
        "allowed_days": ["sunday", "monday", "tuesday", "wednesday", "thursday"],
        "start_time": "08:00",
        "end_time": "20:00",
        "max_stalls": 3,
        "notes": "الساحة الرئيسية أمام مبنى البلدية",
    },
    {
        "name": "شارع الشهداء - مدخل السوق",
        "latitude": 31.5245,
        "longitude": 35.1105,
        "radius_meters": 12,
        "allowed_days": ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
        "start_time": "07:00",
        "end_time": "22:00",
        "max_stalls": 5,
        "notes": "مدخل السوق القديم - حركة مشاة عالية",
    },
    {
        "name": "حديقة المنارة",
        "latitude": 31.5290,
        "longitude": 35.0950,
        "radius_meters": 20,
        "allowed_days": ["friday", "saturday"],
        "start_time": "09:00",
        "end_time": "18:00",
        "max_stalls": 4,
        "notes": "حديقة عامة - مناسبة لبسطات نهاية الأسبوع",
    },
    {
        "name": "مفترق عين سارة",
        "latitude": 31.5380,
        "longitude": 35.0880,
        "radius_meters": 15,
        "allowed_days": ["sunday", "monday", "tuesday", "wednesday", "thursday"],
        "start_time": "06:00",
        "end_time": "14:00",
        "max_stalls": 2,
        "notes": "موقع صباحي - مناسب لبسطات الإفطار والمأكولات",
    },
    {
        "name": "شارع النهضة - قرب الجامعة",
        "latitude": 31.5415,
        "longitude": 35.1020,
        "radius_meters": 15,
        "allowed_days": ["sunday", "monday", "tuesday", "wednesday", "thursday"],
        "start_time": "07:00",
        "end_time": "21:00",
        "max_stalls": 6,
        "notes": "بالقرب من جامعة الخليل - حركة طلابية كثيفة",
    },
    {
        "name": "دوار ابن رشد",
        "latitude": 31.5350,
        "longitude": 35.1060,
        "radius_meters": 18,
        "allowed_days": ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
        "start_time": "08:00",
        "end_time": "23:00",
        "max_stalls": 4,
        "notes": "دوار رئيسي - موقع مميز للمساء",
    },
    {
        "name": "سوق الخضار المركزي",
        "latitude": 31.5270,
        "longitude": 35.1035,
        "radius_meters": 10,
        "allowed_days": ["sunday", "monday", "tuesday", "wednesday", "thursday", "saturday"],
        "start_time": "05:00",
        "end_time": "15:00",
        "max_stalls": 8,
        "notes": "سوق الخضار - أماكن محدودة بجانب المحلات القائمة",
    },
    {
        "name": "مجمع الحافلات الشمالي",
        "latitude": 31.5400,
        "longitude": 35.0940,
        "radius_meters": 15,
        "allowed_days": ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
        "start_time": "06:00",
        "end_time": "20:00",
        "max_stalls": 3,
        "notes": "قرب محطة الحافلات - مسافرون ومنتظرون",
    },
    {
        "name": "شارع وادي التفاح",
        "latitude": 31.5305,
        "longitude": 35.0915,
        "radius_meters": 12,
        "allowed_days": ["sunday", "monday", "tuesday", "wednesday", "thursday"],
        "start_time": "10:00",
        "end_time": "22:00",
        "max_stalls": 3,
        "notes": "منطقة سكنية تجارية - مناسبة للمساء",
    },
    {
        "name": "مدخل الحرم الإبراهيمي",
        "latitude": 31.5228,
        "longitude": 35.1108,
        "radius_meters": 20,
        "allowed_days": ["friday", "saturday", "sunday"],
        "start_time": "08:00",
        "end_time": "17:00",
        "max_stalls": 5,
        "notes": "منطقة سياحية - مناسبة للهدايا والحرف اليدوية",
    },
]


class Command(BaseCommand):
    help = "Load mockup municipality-defined locations for vendor reservation"

    def handle(self, *args, **options):
        created = 0
        for data in MOCKUP_LOCATIONS:
            _, was_created = Location.objects.get_or_create(
                name=data["name"],
                defaults={
                    "latitude": data["latitude"],
                    "longitude": data["longitude"],
                    "radius_meters": data["radius_meters"],
                    "allowed_days": data["allowed_days"],
                    "start_time": data["start_time"],
                    "end_time": data["end_time"],
                    "max_stalls": data["max_stalls"],
                    "is_active": True,
                    "notes": data["notes"],
                },
            )
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Done — {created} new locations created ({len(MOCKUP_LOCATIONS)} total in fixture)")
        )
