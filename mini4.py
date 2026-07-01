import warnings; warnings.filterwarnings("ignore")
import os, sys, config
base="/tmp/cc3/CybORG"
for root,d,files in os.walk(base):
    if os.path.basename(root)=="CybORG" and "__init__.py" in files:
        sys.path.insert(0, os.path.dirname(root)); break
from src.runner import run_episode
def main():
    print("STDOUT via config+ensure+guard")
if __name__=="__main__":
    main()
