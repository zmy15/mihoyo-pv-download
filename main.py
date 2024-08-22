import os
import re
import time
import requests
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
from get_urls import get_urls


def configure_driver():
    edge_options = Options()
    edge_options.add_argument('--disable-gpu')
    edge_options.add_argument('--no-sandbox')
    edge_options.add_argument('--disable-dev-shm-usage')
    edge_driver_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedgedriver.exe"
    service = Service(edge_driver_path)
    driver = webdriver.Edge(service=service, options=edge_options)
    return driver


def read_urls(file_path):
    with open(file_path, 'r') as file:
        urls = file.readlines()
    return [url.strip() for url in urls]


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def download_video(driver, url, save_dir):
    # 打开网页
    driver.get(url)

    # 等待页面加载并确保视频标签出现
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, 'video'))
        )
    except Exception as e:
        print(f'加载页面时出错或未找到视频标签: {url}')
        return

    # 获取页面标题
    time.sleep(5)
    page_title = driver.title.strip().replace(' ', '_')
    invalid_chars = r'[\/:*?"<>|]'

    # 使用正则表达式替换掉非法字符
    filename = re.sub(invalid_chars, '', page_title)

    # 查找所有<video>标签的src属性
    video_tags = driver.find_elements(By.TAG_NAME, 'video')
    video_tag = video_tags[0]
    video_url = video_tag.get_attribute('src')

    # 如果没有找到任何视频URL，输出错误信息并跳过这个URL
    if not video_url:
        print(f'未找到视频链接: {url}')
        return

    video_filename = os.path.join(save_dir, f'{filename}.mp4')

    # 如果文件已存在，跳过下载
    if os.path.exists(video_filename):
        print(f'文件已存在，跳过下载: {video_filename}')
        return

    # 下载视频
    video_response = requests.get(video_url, stream=True)
    total_size = int(video_response.headers.get('content-length', 0))

    # 使用tqdm显示下载进度条
    with open(video_filename, 'wb') as video_file, tqdm(
            desc=video_filename,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as bar:
        for chunk in video_response.iter_content(chunk_size=1024):
            if chunk:
                video_file.write(chunk)
                bar.update(len(chunk))

    print(f'视频下载完成，保存为 {video_filename}')


def download_videos(url_file, save_dir):
    urls = read_urls(url_file)
    create_directory(save_dir)
    driver = configure_driver()

    for url in urls:
        download_video(driver, url, save_dir)

    driver.quit()


if __name__ == "__main__":

    game = input("输入要爬取的游戏\n原神输入:ys\n星铁输入:sr\n绝区零输入:zzz\n")
    state = input("是否获取最新数据(是:Y/否:N)\n")

    if state in ['Y', 'y', 'yes', 'Yes', '是', '1']:
        print('正在获取最新角色数据，会消耗较长时间')
        get_urls(game)

    if game == 'sr':
        url_file = 'sr_角色PV_links.txt'
        save_dir_pv = './videos/sr/'
        download_videos(url_file, save_dir_pv)

    elif game == 'ys':
        save_dir_pv = './videos/ys/pv/'
        save_dir_show = './videos/ys/show/'

        download_videos('ys_角色PV_links.txt', save_dir_pv)
        download_videos('ys_角色演示_links.txt', save_dir_show)

    elif game == 'zzz':
        save_dir_pv = './videos/zzz/pv/'
        save_dir_show = './videos/zzz/show/'

        download_videos('zzz_角色PV_links.txt', save_dir_pv)
        download_videos('zzz_角色展示_links.txt', save_dir_show)
