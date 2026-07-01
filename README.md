# DAH 2026 · 드론 스웜 AI 공방전 시뮬레이션

CybORG(CAGE Challenge 3) 드론 스웜 환경 위에서 **AI 공격 에이전트 vs 방어 에이전트**의
공방전을 돌리고, 대회 공식 `총점 = (공격 + 방어) × 가용성` 으로 점수를 산출한다.
`main.py` **하나만 실행하면** 환경 생성 → 공방전 → 채점까지 자동으로 이어진다.

---

## 1. 폴더 구조

```
DAH 2026/
├── main.py              # ★ 단일 진입점 (이것만 실행)
├── config.py            # 모든 설정 (드론 수·스텝·에이전트 선택 등)
├── requirements.txt     # 고정 버전 의존성
├── README.md            # 이 문서
├── src/
│   ├── environment.py   # CybORG 드론 환경 생성 + 래핑
│   ├── attack_agent.py  # (옵션) 규칙 기반 공격 에이전트
│   ├── defense_agent.py # (옵션) 규칙 기반 방어 에이전트
│   ├── scoring.py       # 대회 점수 계산
│   └── runner.py        # 에피소드 실행 루프
└── docs/
    └── architecture.md  # 구조·설계 설명
```

## 2. 사전 준비 — 왜 버전을 고정하나

CybORG 드론 스웜 시나리오는 **구형 `gym==0.23.1`** 에 묶여 있다. 이 라이브러리는
개발이 중단되어 **numpy 2.x 와 Python 3.12+(distutils 제거)** 에서 깨진다.
따라서 **Python 3.11(또는 3.10) + numpy 1.23.5 + gym 0.23.1** 조합으로 고정한다.

## 3. 설치 (Windows PowerShell 기준)

```powershell
# (1) 프로젝트 폴더로 이동
cd "C:\Users\SAMSUNG\Desktop\DAH해커톤\DAH 2026"

# (2) Python 3.11 가상환경 생성 & 활성화
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# (3) 고정 버전 의존성 설치
python -m pip install --upgrade pip
pip install -r requirements.txt

# (4) CybORG 본체 연결 (이미 설치한 폴더를 지정)
pip install -e "C:\Users\SAMSUNG\Desktop\CybORG-main\CybORG-main"
```

> **CybORG 설치가 editable(-e)로 안 되면** 아래처럼 경로만 잡아줘도 된다:
> ```powershell
> $env:PYTHONPATH = "C:\Users\SAMSUNG\Desktop\CybORG-main\CybORG-main"
> ```
> 이미 `test_run.py` 를 돌렸던 기존 venv 가 있다면, 그 venv 를 활성화해서
> `pip install -r requirements.txt` 만 해도 된다.

## 4. 실행

```powershell
python main.py
```

끝이다. 개별 스크립트를 따로 돌릴 필요가 없다.

## 5. 설정 바꾸기 (`config.py`)

| 항목 | 의미 | 기본값 |
|------|------|--------|
| `NUM_DRONES` | 드론 스웜 규모 | 18 |
| `MAX_STEPS` | 에피소드당 스텝 수 | 150 |
| `NUM_EPISODES` | 반복 실행 횟수 | 3 |
| `USE_CUSTOM_AGENTS` | False=순수 CybORG 내장 / True=우리 규칙 기반 | False |
| `SLA_THRESHOLD` | 가용성 SLA 임계치(%) | 80 |

## 6. 출력 예시

```
 적(Red) = CybORG 내장 웜 / 아군(Blue) = CybORG 내장 RandomAgent (raw)
[에피소드 1/3]
    step   0 | 생존 블루 18/18 | 누적 통신실패 5
    ...
  공격 점수 (attack)   : 20.0  (장악 드론 2대)
  방어 점수 (defense)  : 40.0  (방어 드론 4대)
  가용성 (availability): 7.5%  [미달 (SLA 80%)]
  총점 = (공격+방어) x 가용성 = 4.5
```

> 기본 방어(RandomAgent)는 무작위라 가용성이 낮게 나오는 것이 정상이다.
> 이것이 **개선 전 베이스라인**이며, 여기서 방어 에이전트를 똑똑하게 만드는 것이
> 대회의 핵심 과제다. (`USE_CUSTOM_AGENTS=True` 로 규칙 기반 버전을 켤 수 있다.)
