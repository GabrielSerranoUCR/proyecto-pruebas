import scipy
import sklearn
import pytest
def main() -> None:
    print("SciPy:", scipy.__version__)
    print("Scikit-learn:", sklearn.__version__)
    print("Pytest:", pytest.__version__)


if __name__ == "__main__":
    main()
