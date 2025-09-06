import time
import os
import pandas as pd
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import numpy as np
import cv2
from PIL import Image
import io
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# === KHỞI TẠO ===
driver = webdriver.Chrome()
driver.get("https://odoo.trungtinpc.vn/odoo/action-180")

# === Đăng nhập ===
username = driver.find_element(By.NAME, "login")
username = WebDriverWait(driver, 30).until(
    EC.visibility_of_element_located((By.NAME, "login"))
)
username.send_keys("cfoprubik@gmail.com")

password = driver.find_element(By.NAME, "password")
password.send_keys("123456")
password.send_keys(Keys.ENTER)
time.sleep(3)

# === Đọc file CSV ===
data = pd.read_csv(
    "data.csv",
    sep="\t",
    header=None,
    names=["link", "ten", "baohanh", "danhmuc", "hang"]
)

# === Thư mục chứa logo ===
logos_dir = "image/logos"

# === Hàm check logo trong element với nhiều file logo ===
def check_multiple_logos_in_element(element, logos_dir, min_inliers=10, ratio=0.8):
    """
    Kiểm tra element có chứa bất kỳ logo nào trong thư mục logos_dir không
    """
    try:
        # Chụp ảnh element
        png = element.screenshot_as_png
        img_array = np.array(Image.open(io.BytesIO(png)))
        img_color = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        if img_color is None:
            return False

        img = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)

        # ORB cho ảnh sản phẩm (tính 1 lần)
        orb = cv2.ORB_create(nfeatures=1500)
        kp2, des2 = orb.detectAndCompute(img, None)
        if des2 is None:
            return False

        bf = cv2.BFMatcher(cv2.NORM_HAMMING)

        # Duyệt tất cả logo trong thư mục
        for logo_file in os.listdir(logos_dir):
            logo_path = os.path.join(logos_dir, logo_file)
            tpl_color = cv2.imread(logo_path)
            if tpl_color is None:
                continue

            tpl = cv2.cvtColor(tpl_color, cv2.COLOR_BGR2GRAY)
            kp1, des1 = orb.detectAndCompute(tpl, None)
            if des1 is None:
                continue

            matches = bf.knnMatch(des1, des2, k=2)
            good = [m for m, n in matches if m.distance < ratio * n.distance]

            if len(good) >= min_inliers and len(kp1) > 20 and len(kp2) > 20:
                print(f"✅ Phát hiện logo: {logo_file}")
                return True

        return False
    except Exception as e:
        print("⚠️ Lỗi khi check logo:", e)
        return False


# === Vòng lặp nhập sản phẩm ===
for index, row in data.iterrows():
    driver.get("https://odoo.trungtinpc.vn/odoo/action-570")
    time.sleep(2)

    print(f"Đang nhập sản phẩm: {row['ten']}")

    # Link sản phẩm
    LINK = driver.find_element(By.CSS_SELECTOR, "#url_0")
    LINK.send_keys(row['link'])
    pyautogui.press("enter")
    time.sleep(0.2)

    # Danh mục
    CATE = driver.find_element(By.CSS_SELECTOR, "#cate_id_0")
    CATE.send_keys(row['danhmuc'])
    pyautogui.press("enter")
    time.sleep(0.2)

    # Hãng
    BRAND = driver.find_element(By.CSS_SELECTOR, "#brand_id_0")
    BRAND.send_keys(row['hang'])
    pyautogui.press("enter")
    time.sleep(0.2)

    # Bảo hành
    WARRANTY = driver.find_element(By.CSS_SELECTOR, "#warranty_id_0")
    WARRANTY.send_keys(row['baohanh'])
    pyautogui.press("enter")
    time.sleep(0.2)

    # Ấn nút theo dõi hàng tồn kho
    CHECK_RADIO = driver.find_element(By.CSS_SELECTOR, ".form-check-input")
    CHECK_RADIO.click()

    # Gửi form
    button_crawl = driver.find_element(By.CSS_SELECTOR, ".btn.btn-primary")
    button_crawl.click()
    time.sleep(10)

    # Bật nút show on website
    button_show = driver.find_element(By.CSS_SELECTOR, "#website_published_0")
    button_show.click()

    # Tắt 2 nút thuế
    button_thue = driver.find_elements(By.CSS_SELECTOR, ".oi.oi-close.align-text-top")
    button_thue[0].click()
    button_thue[1].click()
    time.sleep(0.2)

    # === Kiểm tra avatar có logo ===
    avt = driver.find_element(By.NAME, "image_1920")
    if check_multiple_logos_in_element(avt, logos_dir):
        try:
            btn_delete_avt = driver.find_element(By.CSS_SELECTOR, ".fa.fa-trash-o.fa-fw")
            btn_delete_avt.click()
            print("Phát hiện logo ở Avatar sản phẩm, đã xóa logo")
        except:
            print("Có logo nhưng không tìm thấy nút xóa")

    # === Vô tab website ===
    Tab_website = driver.find_element(By.NAME, "website")
    Tab_website.click()
    time.sleep(0.2)

    # === Chèn xuống dòng sau icon ===
    text_area = driver.find_element(By.CSS_SELECTOR, "div.note-editable.odoo-editor-editable")
    driver.execute_script("""
        let container = arguments[0];
                          
        let icons = container.querySelectorAll('.fa'); // lấy tất cả icon .fa
        icons.forEach(icon => {
            let br = document.createElement('br');
            icon.parentNode.insertBefore(br, icon);
        });
        container.focus();
    """, text_area)

    # === Xử lý ảnh chứa logo ===
    images = driver.find_elements(By.TAG_NAME, "img")
    time.sleep(10)

    for idx, img in enumerate(images, start=1):
        try:
            if not img.get_attribute("src"):
                print(f"⚠️ Ảnh {idx} không có src, bỏ qua")
                continue

            size = img.size
            if size['width'] == 0 or size['height'] == 0:
                print(f"⚠️ Ảnh {idx} có kích thước 0, bỏ qua")
                continue

            if check_multiple_logos_in_element(img, logos_dir):
                print(f"✅ Logo phát hiện trong ảnh số {idx}")
                # TODO: Thêm code xóa ảnh ở đây
            else:
                print(f"❌ Ảnh số {idx} không có logo")

        except Exception as e:
            print(f"⚠️ Lỗi khi xử lý ảnh số {idx}: {e}")

    # === Xoá text chứa An Phát / Liên Hệ ===
    driver.execute_script("""
        let spans = document.querySelectorAll("span");
        spans.forEach(span => {
            let text = span.innerText.trim();
            if (text.includes("An Phát") || text.includes("Liên Hệ")) {
                span.remove(); // xoá thẻ span
                console.log("Xoá span có chữ:", text);
            }
        });
    """)

    time.sleep(10)

    # === Upload sản phẩm ===
    UP = driver.find_element(By.CSS_SELECTOR, ".fa.fa-cloud-upload.fa-fw")
    UP.click()
    time.sleep(3)

    print(f"✅ Đã xong sản phẩm: {row['ten']}")
