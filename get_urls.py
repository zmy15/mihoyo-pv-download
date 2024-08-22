from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os


def configure_driver():
    edge_options = Options()
    edge_options.add_argument('--disable-gpu')
    edge_options.add_argument('--no-sandbox')
    edge_options.add_argument('--disable-dev-shm-usage')
    edge_driver_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedgedriver.exe"
    service = Service(edge_driver_path)
    driver = webdriver.Edge(service=service, options=edge_options)
    return driver


def wait_for_element(driver, by, value, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except Exception as e:
        print(f'加载页面时出错: {e}')
        driver.quit()
        exit()


def click_load_more(driver, button_selector):
    time.sleep(2)
    while True:
        try:
            load_more_button = driver.find_element(By.CSS_SELECTOR, button_selector)
            load_more_button.click()
            time.sleep(2)
        except Exception as e:
            print('没有更多内容')
            break


def get_news_items(driver, game):
    if game == 'sr':
        return driver.find_elements(By.CSS_SELECTOR, 'div.list-wrap > a')
    elif game == 'ys':
        return driver.find_elements(By.CLASS_NAME, 'news__item')
    elif game == 'zzz':
        return driver.find_elements(By.CLASS_NAME, 'news-list__item')


def filter_links(news_items, game, keywords):
    links = {key: [] for key in keywords}
    for item in news_items:
        if game == 'sr':
            title_element = item.find_element(By.CSS_SELECTOR, 'div.news-item .title')
        elif game == 'ys':
            title_element = item.find_element(By.CLASS_NAME, 'news__info')
        elif game == 'zzz':
            title_element = item.find_element(By.CLASS_NAME, 'news-list__item-title')

        title_text = title_element.text.strip()

        if game in ['ys', 'zzz']:
            link_element = item.find_element(By.TAG_NAME, 'a')
            link_url = link_element.get_attribute('href')
        elif game == 'sr':
            link_url = item.get_attribute('href')

        if game == 'ys' and link_url.startswith('/'):
            link_url = f'https://ys.mihoyo.com{link_url}'
        elif game == 'zzz' and link_url.startswith('/'):
            link_url = f'https://zzz.mihoyo.com{link_url}'

        for key in keywords:
            if key in title_text:
                links[key].append(link_url)
                print(f'找到包含“{key}”的链接: {link_url}')
                break
    return links


def save_links(links, game):
    for key, link_list in links.items():
        output_file = f'{game}_{key}_links.txt'
        if game == 'zzz':
            with open(output_file, 'a') as file:
                for link in link_list:
                    file.write(link + '\n')
        else:
            with open(output_file, 'w') as file:
                for link in link_list:
                    file.write(link + '\n')


def get_urls(game):
    base_urls = {
        'sr': 'https://sr.mihoyo.com/news',
        'ys': 'https://ys.mihoyo.com/main/news/719',
        'zzz': 'https://zzz.mihoyo.com/news?category=278'
    }

    button_selectors = {
        'sr': '.btn-more-wrap',
        'ys': '.news__more',
        'zzz': 'a.mihoyo-pager-rich__next'
    }

    if game == 'ys':
        keywords = ['角色PV', '角色演示']
        class_name = 'news__item'
    elif game == 'zzz':
        keywords = ['角色PV', '角色展示']
        class_name = 'news-list__item'
    else:
        keywords = ['角色PV']
        class_name = 'list-wrap'

    driver = configure_driver()
    driver.get(base_urls[game])

    wait_for_element(driver, By.CLASS_NAME, class_name)
    if game in ['ys', 'sr']:
        click_load_more(driver, button_selectors[game])
        news_items = get_news_items(driver, game)
        links = filter_links(news_items, game, keywords)
        save_links(links, game)
    elif game == 'zzz':
        button_numbers = []
        if os.path.exists('zzz_角色PV_links.txt'):
            os.remove('zzz_角色PV_links.txt')
        if os.path.exists('zzz_角色展示_links.txt'):
            os.remove('zzz_角色展示_links.txt')
        time.sleep(3)
        button_item = driver.find_element(By.CSS_SELECTOR, 'div.mihoyo-pager-rich.news-pager')
        title_elements = button_item.find_elements(By.CLASS_NAME, 'mihoyo-pager-rich__button')
        for title_element in title_elements:
            button_numbers.append(int(title_element.text.strip()))
        button_number = max(button_numbers)
        for i in range(1, button_number + 1):
            news_items = get_news_items(driver, game)
            links = filter_links(news_items, game, keywords)
            save_links(links, game)
            time.sleep(3)
            try:
                load_more_button = driver.find_element(By.CSS_SELECTOR, button_selectors[game])
                load_more_button.click()
                time.sleep(2)
            except Exception as e:
                print('没有更多内容')

    driver.quit()
