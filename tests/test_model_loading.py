import pickle
import tempfile
import unittest
from pathlib import Path

import app


class ModelLoadingTests(unittest.TestCase):
    def test_load_model_rebuilds_invalid_pickle(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            broken_model_path = Path(tmpdir) / "diabetes_model.pkl"
            broken_artifact = {
                "feature_columns": ["Pregnancies", "Glucose"],
                "scaler": None,
                "models": {
                    "Logistic Regression": {
                        "model": object(),
                        "accuracy": 85.0,
                    }
                },
            }
            with open(broken_model_path, "wb") as handle:
                pickle.dump(broken_artifact, handle)

            app.MODEL_PATH = str(broken_model_path)
            app.model_artifact = None
            app.load_model()

            self.assertIn("Logistic Regression", app.MODEL_OPTIONS)
            self.assertTrue(
                hasattr(
                    app.model_artifact["models"]["Logistic Regression"]["model"],
                    "predict_proba",
                )
            )


if __name__ == "__main__":
    unittest.main()
