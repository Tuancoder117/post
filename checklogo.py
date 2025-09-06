import cv2
import numpy as np
import os

def preprocess_logo(logo_path):
    logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
    if logo is None:
        return None, None
    if logo.shape[2] == 4:  # có alpha (png trong suốt)
        bgr = logo[:, :, :3]
        alpha = logo[:, :, 3]
        mask = cv2.threshold(alpha, 1, 255, cv2.THRESH_BINARY)[1]
        return bgr, mask
    return logo, None


def match_template_multiscale(img, tpl, mask=None, threshold=0.6, scales=np.linspace(0.5, 1.5, 11)):
    best_val = -1
    best_proj = None

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tpl_gray = cv2.cvtColor(tpl, cv2.COLOR_BGR2GRAY)

    for scale in scales:
        new_w = int(tpl_gray.shape[1] * scale)
        new_h = int(tpl_gray.shape[0] * scale)

        if new_w < 10 or new_h < 10:
            continue

        # bỏ qua nếu template lớn hơn ảnh
        if new_w > img_gray.shape[1] or new_h > img_gray.shape[0]:
            continue

        resized_tpl = cv2.resize(tpl_gray, (new_w, new_h))
        resized_mask = cv2.resize(mask, (new_w, new_h)) if mask is not None else None

        if resized_mask is not None:
            res = cv2.matchTemplate(img_gray, resized_tpl, cv2.TM_CCOEFF_NORMED, mask=resized_mask)
        else:
            res = cv2.matchTemplate(img_gray, resized_tpl, cv2.TM_CCOEFF_NORMED)

        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        if max_val > best_val:
            best_val = max_val
            top_left = max_loc
            bottom_right = (top_left[0] + new_w, top_left[1] + new_h)
            best_proj = np.array([[[top_left[0], top_left[1]]],
                                  [[bottom_right[0], top_left[1]]],
                                  [[bottom_right[0], bottom_right[1]]],
                                  [[top_left[0], bottom_right[1]]]], dtype=np.float32)

    return best_val >= threshold, best_proj, best_val


def check_logo(image_path, logo_path, show=True, threshold=0.6):
    img = cv2.imread(image_path)
    tpl, mask = preprocess_logo(logo_path)

    if img is None or tpl is None:
        print(f"⚠️ Không đọc được ảnh hoặc logo: {logo_path}")
        return False

    ok, proj, score = match_template_multiscale(img, tpl, mask=mask, threshold=threshold)

    if not ok:
        print(f"❌ Không tìm thấy logo [{os.path.basename(logo_path)}] (max score={score:.2f})")
        return False

    out = img.copy()
    cv2.polylines(out, [np.int32(proj)], True, (0, 255, 0), 3)

    if show:
        cv2.imshow(f"Kết quả - {os.path.basename(logo_path)}", out)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    print(f"✅ Tìm thấy logo [{os.path.basename(logo_path)}] (score={score:.2f})")
    return True


if __name__ == "__main__":
    image_path = "image/test3.jpg"
    logos_dir = "image/logos"

    for logo_file in os.listdir(logos_dir):
        logo_path = os.path.join(logos_dir, logo_file)
        check_logo(image_path, logo_path, show=False, threshold=0.6)
