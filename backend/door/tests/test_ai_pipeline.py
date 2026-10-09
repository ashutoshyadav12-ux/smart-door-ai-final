import numpy as np
from django.test import SimpleTestCase, override_settings

from door.ai.pipeline import pipeline
from door.ai.similarity import cosine


@override_settings(AI_BACKEND="mock")
class PipelineTests(SimpleTestCase):
    def test_same_input_same_embedding(self):
        a, b = pipeline.analyze(b"face-a"), pipeline.analyze(b"face-a")
        self.assertAlmostEqual(cosine(a.embedding, b.embedding), 1.0, places=4)

    def test_different_inputs_dissimilar(self):
        a, b = pipeline.analyze(b"face-a"), pipeline.analyze(b"face-b")
        self.assertLess(cosine(a.embedding, b.embedding), 0.3)

    def test_embedding_shape(self):
        self.assertEqual(pipeline.analyze(b"x").embedding.shape, (512,))
