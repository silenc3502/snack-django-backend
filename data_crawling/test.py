import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime

# ✅ 반드시 네 API키로 변경해야 함
KAKAO_API_KEY = "너의_카카오_API_키"

service = Service("/opt/homebrew/bin/chromedriver")
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

seoul_gu_list = [
    "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구",
    "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구",
    "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"
]

def clean_address(address):
    address = re.sub(r"\sM층", " 1층", address)
    address = re.sub(r"\s*\d+[-,~]?\s*\d*\s*층", " 1층", address)
    address = re.sub(r"\s\d+[-,~]?\d*\s?호", " 101호", address)
    address = re.sub(r"\s\(.+?\)", "", address)
    address = re.sub(r"\s[가-힣A-Za-z0-9]+빌딩", "", address)
    address = re.sub(r"\s[가-힣A-Za-z0-9]+센터", "", address)
    address = re.sub(r"\s[가-힣A-Za-z0-9]+호텔", "", address)
    return address.strip()

def get_coordinates(address):
    cleaned_address = clean_address(address)
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": cleaned_address}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if response.status_code == 200 and data["documents"]:
        lat = data["documents"][0]["y"]
        lon = data["documents"][0]["x"]
        return lat, lon

    params = {"query": address}  # 원래 주소로 재시도
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if response.status_code == 200 and data["documents"]:
        lat = data["documents"][0]["y"]
        lon = data["documents"][0]["x"]
        return lat, lon

    print(f"❌ 주소 변환 실패: {address}")
    return None, None

def init_driver():
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://map.kakao.com/')
    time.sleep(2)
    return driver

def search_keyword(driver, keyword):
    search_area = driver.find_element(By.ID, 'search.keyword.query')
    search_area.clear()
    search_area.send_keys(keyword)
    search_area.send_keys(Keys.ENTER)
    time.sleep(3)

    try:
        driver.find_element(By.XPATH, '//*[@id="info.main.options"]/li[2]/a').click()
        time.sleep(2)
    except:
        pass

    try:
        driver.find_element(By.ID, 'info.search.place.more').click()
        time.sleep(2)
    except:
        pass

def expand_menu_tab_and_collect(driver):
    menu_items = []
    try:
        menu_tab = driver.find_element(By.CSS_SELECTOR, 'a[href="#menuInfo"]')
        menu_tab.click()
        time.sleep(2)

        while True:
            try:
                more_button = driver.find_element(By.CSS_SELECTOR, '.wrap_more a.link_more')
                if more_button.is_displayed():
                    more_button.click()
                    time.sleep(2)
                else:
                    break
            except:
                break

        menu_elements = driver.find_elements(By.CSS_SELECTOR, '.list_goods > li')
        for element in menu_elements:
            name = element.find_element(By.CSS_SELECTOR, '.tit_item').text.strip()
            try:
                price = element.find_element(By.CSS_SELECTOR, '.desc_item').text.strip()
            except:
                price = '가격정보 없음'
            menu_items.append(f'{name} ({price})')
    except:
        return ['메뉴 없음']
    return menu_items if menu_items else ['메뉴 없음']

def get_store_details(driver, detail_url):
    original_window = driver.current_window_handle
    driver.execute_script("window.open(arguments[0]);", detail_url)
    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)

    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)

    menu_list = expand_menu_tab_and_collect(driver)
    menu_text = ', '.join(menu_list)

    driver.close()
    driver.switch_to.window(original_window)
    return menu_text

def crawl_all_pages(driver):
    all_data = []

    def process_current_page():
        nonlocal all_data
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        stores = soup.select('.placelist > .PlaceItem')

        for store in stores:
            try:
                name = store.select_one('.head_item .tit_name .link_name').text.strip()
                degree = store.select_one('.rating .score .num').text.strip()
                review_count = store.select_one('.review em[data-id="numberofreview"]').text.strip() or '0'
                address = store.select_one('.info_item .addr').text.strip()
                tel = store.select_one('.info_item .phone').text.strip() if store.select_one('.info_item .phone') else '전화번호 없음'
                detail_url = store.select_one('.contact .moreview')['href']

                menu_text = get_store_details(driver, detail_url)

                lat, lon = get_coordinates(address)

                print(f"📍 {name} | 평점: {degree} | 리뷰 {review_count}개 | 위도: {lat} | 경도: {lon}")
                all_data.append([name, degree, review_count, address, tel, menu_text, lat, lon])

            except Exception as e:
                print(f"❌ 매장 크롤링 실패: {e}")

    while True:
        process_current_page()
        try:
            next_button = driver.find_element(By.ID, 'info.search.page.next')
            if "disabled" in next_button.get_attribute("class"):
                break
            next_button.click()
            time.sleep(2)
        except:
            break

    return all_data

def save_to_csv(gu_name, data):
    today = datetime.now().strftime("%Y%m%d")
    filename = f'{today}_{gu_name}_맛집_크롤링.csv'
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['이름', '평점', '리뷰수', '주소', '전화번호', '메뉴', '위도', '경도'])
        writer.writerows(data)
    print(f"✅ {gu_name} 저장 완료 ({filename})")

def crawl_seoul_gu():
    for gu in seoul_gu_list:
        print(f"🔹 {gu} 크롤링 시작!")
        driver = init_driver()
        search_keyword(driver, f'{gu} 맛집')

        all_data = crawl_all_pages(driver)
        save_to_csv(gu, all_data)

        driver.quit()
        print(f"✅ {gu} 크롤링 및 저장 완료\n")

if __name__ == '__main__':
    crawl_seoul_gu()
