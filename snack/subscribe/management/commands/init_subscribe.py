from django.core.management.base import BaseCommand
from subscribe.entity.subscribe import Subscribe

class Command(BaseCommand):
    help = '초기 구독 상품 헝글패스 데이터 생성'

    def handle(self, *args, **kwargs):
        plans = [
            {
                'name': 'Hungll Pass Basic',
                'price': 9900,
                'duration_days': 30,
                'plan_type': 'BASIC'
            },
            {
                'name': 'Hungll Pass Premium',
                'price': 15900,
                'duration_days': 30,
                'plan_type': 'PREMIUM'
            },
        ]

        for plan in plans:
            obj, created = Subscribe.objects.get_or_create(
                plan_type=plan['plan_type'],
                defaults={**plan, 'is_active': True}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"{plan['name']} 생성됨"))
            else:
                self.stdout.write(f"{plan['name']} 이미 존재함")
