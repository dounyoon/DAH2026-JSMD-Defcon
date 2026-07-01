import warnings; warnings.filterwarnings("ignore")
import os, sys
sys.stdout = sys.stderr          # 모든 print를 stderr로 (pygame이 안 건드림)
base="/tmp/cc3/CybORG"
for root,d,files in os.walk(base):
    if os.path.basename(root)=="CybORG" and "__init__.py" in files:
        sys.path.insert(0, os.path.dirname(root)); break
from src.runner import run_episode
from src.scoring import format_report
def main():
    print("배너: 시뮬레이션 시작")
    s = run_episode(6, 30, 42, 10.0, 80.0, True, 15, use_custom_agents=False)
    print(format_report(s, 80.0))
if __name__=="__main__":
    main()
