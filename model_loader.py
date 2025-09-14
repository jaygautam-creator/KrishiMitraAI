# model_loader.py
import pickle
import numpy as np
from sklearn.tree import _tree

def load_compatible_model(model_path):
    """Load model with compatibility for different scikit-learn versions"""
    try:
        # First try normal loading
        return joblib.load(model_path)
    except Exception as e:
        if "incompatible dtype" in str(e):
            # Use custom unpickling for compatibility
            with open(model_path, 'rb') as f:
                return pickle.load(f)
        else:
            raise e

# Alternative approach for specific version mismatch
def custom_unpickler(file):
    import sys
    if sys.version_info >= (3, 0):
        return pickle.load(file, encoding='latin1')
    else:
        return pickle.load(file)