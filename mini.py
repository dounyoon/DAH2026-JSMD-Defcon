import sys, os
sys.path.insert(0, "/tmp/cc3/CybORG")
import warnings; warnings.filterwarnings("ignore")
sys.stderr.write(">> imports 시작\n")
from src.runner import run_episode
sys.stderr.write(">> runner import 완료\n")
print("STDOUT: 배너 테스트 라인")      # 이게 보이는지가 핵심
sys.stdout.flush()
sys.stderr.write(">> print 완료\n")
