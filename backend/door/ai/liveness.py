"""PROTOTYPE liveness: blink (EAR over frames) or natural face motion.
Not spoof-proof (a video replay can pass). Use IR/depth hardware for real security."""
import numpy as np

EAR_CLOSED, EAR_OPEN = 0.21, 0.25


def _ear(eye):
    eye = np.asarray(eye, dtype=np.float32)
    a = np.linalg.norm(eye[1] - eye[5])
    b = np.linalg.norm(eye[2] - eye[4])
    c = np.linalg.norm(eye[0] - eye[3])
    return float((a + b) / (2.0 * c + 1e-6))


def eye_aspect_ratio(landmarks68):
    """landmarks68: (68, 2+) array, iBUG ordering."""
    pts = np.asarray(landmarks68)[:, :2]
    return (_ear(pts[36:42]) + _ear(pts[42:48])) / 2.0


def blink_detected(ears) -> bool:
    return len(ears) >= 2 and min(ears) < EAR_CLOSED and max(ears) > EAR_OPEN


def motion_score(crops) -> float:
    """Mean abs pixel difference between consecutive 64x64 grayscale face crops."""
    import cv2
    small = [cv2.resize(cv2.cvtColor(c, cv2.COLOR_BGR2GRAY), (64, 64)).astype(np.float32) for c in crops]
    if len(small) < 2:
        return 0.0
    return float(np.mean([np.abs(small[i + 1] - small[i]).mean() for i in range(len(small) - 1)]))


def check(results) -> tuple:
    """results: list of FaceResult (>=2 frames). Returns (is_live, reason)."""
    if len(results) < 2:
        return False, "need_multiple_frames"
    ears = [r.ear for r in results if r.ear is not None]
    if blink_detected(ears):
        return True, "blink"
    crops = [r.crop for r in results if r.crop is not None]
    if len(crops) >= 2 and motion_score(crops) > 1.0:
        return True, "motion"
    return False, "no_blink_or_motion"
