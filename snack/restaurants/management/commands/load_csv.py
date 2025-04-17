import pandas as pd
from django.core.management.base import BaseCommand
from restaurants.entity.restaurants import Restaurant

class Command(BaseCommand):
    help = "CSV 파일을 DB에 저장"

    def handle(self, *args, **kwargs):
        file_path = "data/preprocessed_송파구_맛집.csv"  # 실제 경로로 맞춰줘야 함
        df = pd.read_csv(file_path)

        for _, row in df.iterrows():
            name = row['이름']
            latitude = row.get('위도')
            longitude = row.get('경도')
            address = row.get('주소', '')
            rating = row.get('평점', None)
            review_count = row.get('리뷰수', None)
            category = row.get('서브카테고리', '')
            closed = False  # 폐업 여부 없음

            obj, created = Restaurant.objects.get_or_create(
                name=name,
                defaults={
                    'latitude': latitude,
                    'longitude': longitude,
                    'address': address,
                    'rating': rating,
                    'reviewCount': review_count,
                    'category': category,
                    'closed': closed,
                }
            )

            msg = "✅ 저장 완료" if created else "⚠️ 이미 존재"
            self.stdout.write(self.style.SUCCESS(f"{msg}: {name}"))

        self.stdout.write(self.style.SUCCESS("🎉 CSV 데이터 입력 완료!"))
