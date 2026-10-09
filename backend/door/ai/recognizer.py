from .similarity import normalize


def embed(face):
    """ArcFace 512-d embedding (already computed by FaceAnalysis), L2-normalised."""
    return normalize(face.embedding)
