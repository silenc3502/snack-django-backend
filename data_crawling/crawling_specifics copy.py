from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv

service = Service("/opt/homebrew/bin/chromedriver")
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=service, options=options)
driver.get('https://map.kakao.com/')
time.sleep(2)

search_area = driver.find_element(By.ID, 'search.keyword.query')
search_area.send_keys('강남구 맛집')
search_area.send_keys(Keys.ENTER)
time.sleep(3)

def remove_dimmed_layer():
    try:
        dimmed_layer = driver.find_element(By.ID, 'dimmedLayer')
        driver.execute_script("arguments[0].style.display='none';", dimmed_layer)
    except:
        pass

def click_place_tab():
    remove_dimmed_layer()
    driver.find_element(By.XPATH, '//*[@id="info.main.options"]/li[2]/a').click()
    time.sleep(2)

click_place_tab()

def click_place_more():
    try:
        driver.find_element(By.ID, 'info.search.place.more').click()
        time.sleep(2)
    except:
        pass

click_place_more()

def expand_menu_tab_and_collect():
    menu_items = []
    try:
        # 메뉴 탭 클릭
        menu_tab = driver.find_element(By.CSS_SELECTOR, 'a[href="#menuInfo"]')
        menu_tab.click()
        time.sleep(2)

        # 메뉴 더보기 버튼 계속 클릭해서 전체 메뉴 노출
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

        # 메뉴 목록 수집
        menu_elements = driver.find_elements(By.CSS_SELECTOR, '.list_goods > li')
        for element in menu_elements:
            name = element.find_element(By.CSS_SELECTOR, '.tit_item').text.strip()
            try:
                price = element.find_element(By.CSS_SELECTOR, '.desc_item').text.strip()
            except:
                price = '가격정보 없음'
            menu_items.append(f'{name} ({price})')

    except Exception as e:
        print(f"❌ 메뉴 수집 실패: {e}")
        return ['메뉴 없음']

    return menu_items if menu_items else ['메뉴 없음']

def scroll_to_reviews():
    try:
        review_section = driver.find_element(By.CSS_SELECTOR, '.section_review')
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", review_section)
        time.sleep(2)
    except Exception as e:
        print(f"❌ 리뷰 섹션 이동 실패: {e}")

def get_all_reviews():
    reviews = []
    seen_reviews = set()
    last_seen_review = None  # 무한루프 방지

    def collect_reviews():
        nonlocal last_seen_review
        found_new = False
        review_elements = driver.find_elements(By.CSS_SELECTOR, '.list_review .inner_review')

        for element in review_elements:
            try:
                expand_btns = element.find_elements(By.CSS_SELECTOR, 'button.btn_fold')
                for btn in expand_btns:
                    if btn.is_displayed():
                        btn.click()
                        time.sleep(0.5)

                review_text = element.find_element(By.CSS_SELECTOR, '.desc_review').text.strip()
                if review_text and review_text not in seen_reviews:
                    seen_reviews.add(review_text)
                    reviews.append(review_text)
                    found_new = True

            except Exception as e:
                print(f"❌ 리뷰 수집 에러: {e}")

        if reviews:
            last_seen_review = reviews[-1]
        return found_new

    scroll_to_reviews()
    collect_reviews()

    while True:
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(0.5)

        found_new = collect_reviews()

        try:
            more_button = driver.find_element(By.CSS_SELECTOR, '.section_review .wrap_more a.link_more')
            if more_button.is_displayed():
                more_button.click()
                time.sleep(2)

                new_review_elements = driver.find_elements(By.CSS_SELECTOR, '.list_review .inner_review')
                if new_review_elements:
                    last_review_text = new_review_elements[-1].find_element(By.CSS_SELECTOR, '.desc_review').text.strip()
                    if last_seen_review and last_review_text == last_seen_review:
                        print("⚠️ 더보기 눌러도 새 리뷰 없음 - 무한루프 방지 종료")
                        break
                continue
        except:
            pass

        if not found_new:
            print("✅ 새로운 리뷰 없음, 수집 종료")
            break

    return "\n".join(reviews) if reviews else "후기 없음"

def get_store_details(detail_url):
    original_window = driver.current_window_handle

    driver.execute_script("window.open(arguments[0]);", detail_url)
    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)

    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)

    # 메뉴 탭 열고 모든 메뉴 수집
    menu_list = expand_menu_tab_and_collect()
    menu_text = ', '.join(menu_list) if menu_list else '메뉴 없음'

    # 리뷰 수집
    review_text = get_all_reviews()

    driver.close()
    driver.switch_to.window(original_window)

    return menu_text, review_text

def crawl_all_pages():
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

                menu_text, review_text = get_store_details(detail_url)

                print(f"📍 {name} | 평점: {degree} | 리뷰 {review_count}개 수집 완료")
                all_data.append([name, degree, review_count, address, tel, menu_text, review_text])

            except Exception as e:
                print(f"❌ 매장 크롤링 실패: {e}")

    while True:
        process_current_page()

        try:
            next_button = driver.find_element(By.ID, 'info.search.page.next')
            if "disabled" in next_button.get_attribute("class"):
                print("✅ 마지막 페이지 도달, 크롤링 종료")
                break
            next_button.click()
            time.sleep(2)
        except:
            print("❌ 다음 버튼 클릭 실패, 크롤링 종료")
            break

    with open('강남구_맛집_전체크롤링.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['이름', '평점', '리뷰수', '주소', '전화번호', '메뉴', '리뷰'])
        writer.writerows(all_data)

    print("✅ 전체 크롤링 완료 및 저장 완료")

print("🔹 크롤링 시작!")
crawl_all_pages()
driver.quit()
