import random
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import numpy as np

# Terminal çıktısını UTF-8 olarak ayarla
sys.stdout.reconfigure(encoding='utf-8')

def generate_random_coordinates():
    # Avrupa Koordinatları (Boylam 10 ile 45 arasında, Enlem 35 ile 70 arasında)
    random_x = random.uniform(35, 70)   # Enlem
    random_y = random.uniform(10, 45)   # Boylam
    return random_x, random_y

def calculate_average_color(image_path):
    # Resmi aç ve renk ortalamasını hesapla
    img = Image.open(image_path)
    img = img.convert("RGB")  # Renk formatını RGB'ye çevir
    np_img = np.array(img)
    
    # Renk ortalamasını hesapla
    avg_color = np.mean(np_img, axis=(0, 1))  # Her pikselin RGB değerlerinin ortalamasını al
    return avg_color

def crop_image(image_path):
    img = Image.open(image_path)
    
    # Görüntü boyutlarını al
    width, height = img.size
    
    # Eğer görüntü yüksekliği 360px'den küçükse kırpma yapma
    if height < 360:
        print("Görüntü çok küçük, kırpma işlemi atlandı.")
        return

    # Yeni kırpılmış alanı belirle (yukarıdan 180px, aşağıdan 180px kes)
    cropped_img = img.crop((0, 180, width, height - 180))
    
    # Aynı dosyanın üzerine yaz
    cropped_img.save(image_path)
    print(f"Kırpma işlemi tamamlandı: {image_path}")

def capture_screenshot(url, filename="earth_screenshot.png"):
    # Chrome seçenekleri
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")  # Tarayıcıyı arka planda çalıştırmak için (isteğe bağlı)

    # WebDriver başlat
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)

        # Sayfanın tamamen yüklenmesini bekle (iframe yüklenene kadar)
        WebDriverWait(driver, 250000).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        time.sleep(10)  # Sayfa tam yüklenene kadar bekle

        # Sayfanın ekran görüntüsünü al ve kaydet
        driver.save_screenshot(filename)
        print(f"Ekran görüntüsü kaydedildi: {filename}")

        # Renk ortalamasını hesapla
        avg_color = calculate_average_color(filename)
        print(f"Renk ortalaması: {avg_color}")

        # Eğer renk ortalaması mavi veya siyah ise yeni koordinatları üret
        if (avg_color[2] > avg_color[0] and avg_color[2] > avg_color[1]) or np.all(avg_color < [50, 50, 50]):
            print("Renk mavi veya siyaha yakın, yeni koordinatlar üretilecek...")
            return True  # Yeni koordinatlar üretilecek
        else:
            print("Renk ortalaması okyanus dışı, işlem sonlandırılıyor...")

            # Ekran görüntüsünü kırp
            crop_image(filename)

            return False  # İşlem sonlanacak

    except Exception as e:
        print(f"Hata oluştu: {e}")
        return False

    finally:
        driver.quit()

# Rastgele koordinatları üret
def process_coordinates():
    while True:
        random_x, random_y = generate_random_coordinates()
        print(f"Koordinatlar: {random_x}, {random_y}")
        
        # URL oluştur
        test_url = f"https://earth.google.com/web/@{random_x},{random_y},1000a,4000d,35y,0h,0t,0r"
        
        # Ekran görüntüsünü al ve renk ortalamasına bak
        if not capture_screenshot(test_url):
            break  # Eğer renk okyanus dışıysa, döngü sonlanır

# Başlat
process_coordinates()

