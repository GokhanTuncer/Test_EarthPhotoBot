import sys
import time
import random
import numpy as np
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Terminal çıktısını UTF-8 olarak ayarla
sys.stdout.reconfigure(encoding='utf-8')

def generate_random_coordinates():
    # X ve Y koordinatları için sınırlar belirleyelim
    random_x = random.uniform(-180, 180)  # X koordinatı -180 ile 180 arasında
    random_y = random.uniform(-90, 90)    # Y koordinatı -90 ile 90 arasında
    return random_x, random_y

def average_color(image_path):
    """Bir resmin ortalama rengini hesapla."""
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        pixels = np.array(img)
        r = np.mean(pixels[:,:,0])  # Red kanalının ortalaması
        g = np.mean(pixels[:,:,1])  # Green kanalının ortalaması
        b = np.mean(pixels[:,:,2])  # Blue kanalının ortalaması
        return r, g, b

def is_ocean_color(r, g, b):
    """Mavi veya siyah tonlarına yakın mı kontrol et."""
    # Renk analizine göre okyanus mu değil mi kontrol et
    if b > r and b > g:
        return True
    return False

def capture_screenshot(url, filename="earth_screenshot.png"):
    # Chrome seçenekleri
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")  # Tarayıcıyı arka planda çalıştırmak için (isteğe bağlı)

    # WebDriver başlat
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        while True:
            # Rastgele koordinatları oluştur
            random_x, random_y = generate_random_coordinates()

            # URL'yi güncelle
            test_url = f"https://earth.google.com/web/@{random_y},{random_x},100a,100d,35y,0h,0t,0r"

            driver.get(test_url)

            # Sayfanın tamamen yüklenmesini bekle
            WebDriverWait(driver, 250000).until(
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
            time.sleep(5)  # Sayfanın tam yüklenmesi için bir süre bekle

            # Ekran görüntüsünü al
            driver.save_screenshot(filename)

            # Renk ortalamasını kontrol et
            r, g, b = average_color(filename)
            print(f"Renk Ortalaması: R={r}, G={g}, B={b}")

            if is_ocean_color(r, g, b):
                print("Okyanus renginde, yeni koordinatlar üretilecek...")
                continue  # Okyanus renginde ise tekrar yeni koordinatla dene
            else:
                print("Kara alanı bulundu, ekran görüntüsü kaydedildi.")
                break  # Kara alanı bulundu, işlemi sonlandır

    except Exception as e:
        print(f"Hata oluştu: {e}")

    finally:
        driver.quit()

# Test için ekran görüntüsü al
capture_screenshot("earth_screenshot.png")