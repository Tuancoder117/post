import time
import pandas as pd
import pyautogui
import pyperclip

# Đọc file CSV
data = pd.read_csv(
    "data.csv",
    sep="\t",
    header=None,
    names=["link", "ten", "baohanh", "danhmuc", "hang"]
)

print("Bạn có 5 giây để mở cửa sổ form...")
time.sleep(5)

def safe_click(x, y, delay=1):
    pyautogui.click(x, y)
    time.sleep(delay)

for index, row in data.iterrows():
    print(f"Đang nhập sản phẩm: {row['ten']}")
    
    # Link sản phẩm
    safe_click(360, 137)
    pyautogui.typewrite(row['link'])
    time.sleep(1)
    pyautogui.press("tab")
    
    # Danh mục
    safe_click(922, 568)
    pyautogui.typewrite(row['danhmuc'])
    time.sleep(1)
    pyautogui.press("tab")
    
    # Hãng
    safe_click(925, 610)  # sửa thiếu dấu phẩy
    pyautogui.typewrite(row['hang'])
    time.sleep(1)
    pyautogui.press("tab")
    
    # Bảo hành
    safe_click(1408, 574)
    pyautogui.typewrite(row['baohanh'])
    time.sleep(1)
    pyautogui.press("tab")
    
    # Gửi form
    safe_click(1366, 614)
    safe_click(1155, 603)
    

    safe_click(511, 697, delay=7) #bấm nút quét 

    #Vô trang thông tin
    print("đã xong")
    safe_click(464,377)
    safe_click(986,555)
    safe_click(981,610)
    safe_click(528,434)

    pyautogui.click(x=500, y=300)

safe_click(256,822)
# Chọn tất cả văn bản
pyautogui.hotkey('ctrl', 'a')

# Lặp liên tục kiểm tra dấu tích
while True:
    tick_location = pyautogui.locateOnScreen('tick_check.png', confidence=0.2)
    if tick_location:
        pyautogui.press('enter')
        time.sleep(0.5)