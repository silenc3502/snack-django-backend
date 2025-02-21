from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
options.add_argument('window-size=1380,900')
driver = webdriver.Chrome(options=options)

URL = 'https://map.naver.com/p/search/%EA%B0%95%EB%82%A8%EA%B5%AC%20%EB%A7%9B%EC%A7%91?c=13.00,0,0,0,dh'
driver.get(url=URL)

# 페이지 로드 대기
sleep(3)

while True:
    # 현재 페이지의 가게 리스트 가져오기
    store_elements = driver.find_elements(By.XPATH, "/html/body/div[3]/div/div[2]/div[1]/ul/li[1]/div[1]/a[1]/div/div/span[1]")

# <span class="TYaxT">자연산 해담일식 대게마을</span>
# #_pcmap_list_scroll_container > ul > li:nth-child(1) > div.CHC5F > a.tzwk0 > div > div > span.TYaxT
# /html/body/div[3]/div/div[2]/div[1]/ul/li[1]/div[1]/a[1]/div/div/span[1]

    print(f"총 {len(store_elements)}개의 가게를 찾았습니다.")

    for index, e in enumerate(store_elements, start=1):
        try:
            store_name = e.find_element(By.CSS_SELECTOR, ".place_bluelink").text
            print(f"{index}. {store_name}")
        except:
            print(f"{index}. 가게 이름을 가져올 수 없음")

    print("-" * 50)

    # 다음 페이지 버튼 확인
    try:
        next_page_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#app-root .pagination-next"))
        )
        next_page_disabled = next_page_button.get_attribute("aria-disabled")
        
        if next_page_disabled == "true":
            print("더 이상 다음 페이지가 없습니다.")
            break
        
        next_page_button.click()
        sleep(2)
    except:
        print("다음 페이지 버튼을 찾을 수 없습니다.")
        break
