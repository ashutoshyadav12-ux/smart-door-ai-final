import numpy as np

MIN_SHARPNESS = 40.0
MIN_BRIGHT, MAX_BRIGHT = 40.0, 220.0
MIN_FACE_SIZE = 80


def assess(img_bgr, bbox) -> dict:
    import cv2
    x1, y1, x2, y2 = [int(max(0, v)) for v in bbox]
    crop = img_bgr[y1:y2, x1:x2]
    if crop.size == 0:
        return {"ok": False, "score": 0.0, "reason": "empty_crop"}
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    sharp = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    bright = float(gray.mean())
    size = min(x2 - x1, y2 - y1)

    reason = None
    if size < MIN_FACE_SIZE:
        reason = "face_too_small"
    elif bright < MIN_BRIGHT:
        reason = "too_dark"
    elif bright > MAX_BRIGHT:
        reason = "too_bright"
    elif sharp < MIN_SHARPNESS:
        reason = "too_blurry"

    score = (min(sharp / 150.0, 1.0) * 0.5
             + (1 - abs(bright - 128) / 128) * 0.25
             + min(size / 200.0, 1.0) * 0.25)
    return {"ok": reason is None, "score": round(float(np.clip(score, 0, 1)), 3),
            "reason": reason, "sharpness": sharp, "brightness": bright, "size": size}
