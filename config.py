"""
DAH 2026 - 공방전 시뮬레이션 설정
================================
모든 실행 파라미터를 이 파일 한 곳에서 관리한다.
main.py 는 이 값들을 읽어 전체 시뮬레이션을 구동한다.
"""

# --- CybORG 설치 경로 ---
# CybORG 를 이 venv 에 pip 설치하지 않았다면, 여기에 CybORG 폴더 경로를 적는다.
# (다운로드/압축해제한 폴더. 그 안에 setup.py 와 CybORG 패키지 폴더가 있는 위치)
# 비워두면("") 이미 설치된 CybORG 를 사용한다.
CYBORG_PATH = r"C:\Users\SAMSUNG\Desktop\DAH해커톤\CybORG-main\CybORG-main"

# --- 시나리오(무대) 설정 ---
NUM_DRONES = 18       # 드론 스웜 규모 (CC3 기본값 = 18)
MAX_STEPS = 150       # 한 에피소드당 시뮬레이션 스텝 수
SEED = 42             # 재현성을 위한 난수 시드
NUM_EPISODES = 3      # 반복 실행 횟수 (평균 점수 산출용)

# --- 대회 채점 가중치 ---
# 대회 공식: total_score = (attack + defense) * availability
POINTS_PER_DRONE = 10.0   # 드론 1대당 공격/방어 점수
SLA_THRESHOLD = 80.0      # 가용성 SLA 임계치(%) - 이 아래로 떨어지면 임무 위험

# --- 에이전트 선택 ---
# False = 순수 raw CybORG 내장 에이전트로 실행 (공격=RedDroneWorm, 방어=RandomAgent)
# True  = 우리가 만든 규칙 기반 에이전트로 실행 (attack_agent.py / defense_agent.py)
USE_CUSTOM_AGENTS = False

# --- 출력 설정 ---
VERBOSE = True            # 스텝별 로그 출력 여부
LOG_EVERY = 25            # 몇 스텝마다 로그를 찍을지
