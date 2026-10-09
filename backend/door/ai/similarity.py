import numpy as np


def normalize(v) -> np.ndarray:
    v = np.asarray(v, dtype=np.float32)
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def cosine(a, b) -> float:
    return float(np.dot(normalize(a), normalize(b)))


def cosine_matrix(matrix: np.ndarray, v) -> np.ndarray:
    """matrix rows must already be L2-normalised."""
    return matrix @ normalize(v)
