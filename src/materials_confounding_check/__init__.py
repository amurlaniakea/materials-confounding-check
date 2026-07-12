"""materials-confounding-check: bibliographic-confounding falsification test for materials ML."""

__version__ = "0.1.0"

from .models import Dataset, Metadata, ConfoundingVerdict

__all__ = ["Dataset", "Metadata", "ConfoundingVerdict", "__version__"]
