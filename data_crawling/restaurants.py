import re
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 서울의 25개 구 리스트
seoul_gu_list = [
    "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구",
    "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구",
    "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"
]


def get_place_ids(gu):
    search_url = f"https://map.naver.com/v5/search/{gu} 맛집"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 브라우저 화면 없이 실행
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(search_url)

    # 페이지가 완전히 로드될 때까지 기다리기
    time.sleep(10)  # 페이지 로딩을 충분히 기다린 후 진행

    # 전체 HTML 확인
    print("📄 전체 HTML 구조 확인:\n", driver.page_source[:500])

    # /html/body/div[1]/div/div[2]/div[1]/div/div[2]/div[1]/div/div[2]/iframe
    try:
        # /html/body/div[1] -> div[1] 이후 계속 찾기
        div_1 = driver.find_element(By.XPATH, "/html/body/div[1]")
        print("✅ /html/body/div[1] 찾기 성공")

        # Step 2: div[1] -> div[2]로 진행
        div_2 = div_1.find_element(By.XPATH, "./div/div[2]")
        print("✅ div[1]/div[2] 찾기 성공")

        # Step 3: div[2] -> div[1]로 진행
        div_3 = div_2.find_element(By.XPATH, "./div[1]/div/div[2]/div[1]")
        print("✅ div[2]/div[1] 찾기 성공")

        # Step 4: div[1] -> div[2]로 진행
        div_4 = div_3.find_element(By.XPATH, "./div/div[2]")
        print("✅ div[3]/div[2] 찾기 성공")

        # Step 5: iframe 찾기
        iframe = WebDriverWait(div_4, 20).until(EC.presence_of_element_located((By.ID, "searchIframe")))
        print("✅ searchIframe 찾기 성공")
        driver.switch_to.frame(iframe)  # iframe 내부로 전환
        print(f"✅ iframe 전환 완료")
        time.sleep(3)

    except Exception as e:
        print(f"⚠️ iframe 찾기 실패 - 에러: {str(e)}")

    # Step 2: 검색 결과 컨테이너 찾기 (iframe 없이)
    try:
        place_list = driver.find_element(By.CLASS_NAME, "Ryr1F")
        print(f"✅ 검색 결과 컨테이너 발견")
        results = place_list.find_elements(By.TAG_NAME, "a")
        print(f"✅ 검색 결과 {len(results)}개 발견")
    except Exception as e:
        print(f"🚨 검색 결과 컨테이너 찾기 실패 - 에러: {str(e)}")
        driver.quit()
        return []

    # Step 3: place_id 추출
    place_ids = []
    for result in results:
        href = result.get_attribute("href")
        match = re.search(r"place/(\d+)", href)
        if match:
            place_ids.append(match.group(1))

    driver.quit()
    print(f"🔎 찾은 place_ids: {place_ids}")  # 확인용
    return list(set(place_ids))  # 중복 제거


def get_place_info(place_id):
    url = f"https://pcmap.place.naver.com/restaurant/{place_id}/home"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 브라우저 화면 없이 실행
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(5)  # 페이지 로딩 대기

    try:
        name = driver.find_element(By.CSS_SELECTOR, "span.Fc1rA").text
        review_count = int(driver.find_element(By.CSS_SELECTOR, "span.PXMot").text.replace(",", ""))  # 리뷰 개수
        rating = driver.find_element(By.CSS_SELECTOR, "span.Z1W8N").text  # 평점
    except:
        print(f"⚠️ place_id {place_id}: 리뷰 정보 가져오기 실패")
        name, review_count, rating = "정보 없음", 0, "정보 없음"

    driver.quit()

    return {
        "식당 이름": name,
        "리뷰 개수": review_count,
        "평점": rating
    }


# 서울 각 구별로 식당 데이터 수집
all_restaurants = []
for gu in seoul_gu_list:
    print(f"🔍 {gu}에서 네이버 지도 검색 중...")

    place_ids = get_place_ids(gu)

    gu_restaurants = []
    for place_id in place_ids:
        info = get_place_info(place_id)
        if info and info["리뷰 개수"] >= 100:
            info["구"] = gu  # 구 정보 추가
            gu_restaurants.append(info)
            time.sleep(1)  # API 요청 간격 조절

    all_restaurants.extend(gu_restaurants)
    print(f"✅ {gu}에서 리뷰 100개 이상인 식당 {len(gu_restaurants)}개 수집 완료!")

# 데이터 저장 및 출력
df = pd.DataFrame(all_restaurants)
df.to_csv("seoul_restaurants_by_gu.csv", index=False, encoding="utf-8-sig")

print("🎉 데이터 저장 완료! 'seoul_restaurants_by_gu.csv' 파일을 확인하세요.")
