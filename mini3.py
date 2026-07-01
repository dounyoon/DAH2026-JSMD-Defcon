import sys, os
sys.path.insert(0, "/tmp/cc3/CybORG")
import warnings; warnings.filterwarnings("ignore")
from src.runner import run_episode
def main():
    print("STDOUT inside main() via guard")
if __name__ == "__main__":
    main()
