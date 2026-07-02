"""
방어 에이전트 (Blue / 아군 드론)
================================
방산 도메인의 '탐지 -> 격리 -> 복구 -> 가용성 유지' 방어 파이프라인을
규칙 기반으로 구현한다. 드론 1대당 방어 에이전트 1개가 분산 배치된다.

핵심 원칙 (가용성 보존):
  - 내 드론에 침입 세션이 탐지되면 RemoveOtherSessions 로 '그 세션만' 격리한다.
  - 뺏긴 '다른' 드론을 RetakeControl 로 되찾는다 (아래 [중요] 참고).
  - 할 일이 없으면 Sleep 으로 자원을 아낀다 (전체망 차단 금지 원칙).

[중요] 복구는 '다른' 드론을 대상으로 한다:
  드론이 장악되면 그 드론의 방어 에이전트도 함께 제거된다(죽는다). 따라서
  "내 드론이 뺏기면 내가 복구"는 영원히 실행될 수 없다(죽은 에이전트는 행동 불가).
  그래서 '살아있는' 에이전트가 뺏긴 다른 드론을 RetakeControl 로 되찾도록 한다.
  뺏긴 드론을 되찾으면 그 드론에 박힌 red root 가 제거되어 정상 통신이 되살아나
  가용성이 회복된다.

정수 액션 매핑:
  CybORG PettingZoo 래퍼는 정수 액션을 쓴다. runner 가 넘겨주는
  action_map(정수 -> Action 객체)에서 원하는 행동 유형의 인덱스를 찾아 반환한다.
"""

from CybORG.Agents import BaseAgent
from CybORG.Shared import Results


class ReactiveDefenseAgent(BaseAgent):
    """반응형 규칙 기반 방어 에이전트 (복구형)."""

    # 로컬 위협이 없을 때, 뺏긴 다른 드론 복구(RetakeControl)를 시도할 확률.
    RETAKE_PROBABILITY = 0.5

    def __init__(self, name, np_random=None):
        super().__init__(name, np_random)
        self.action_map = {}   # {정수: Action 객체} - runner 가 매 스텝 갱신

    def _own_drone_key(self):
        """자신이 지키는 드론의 관측 키 (예: blue_agent_5 -> drone_5)."""
        return "drone_" + self.name.split("_")[-1]

    # --- 탐지 로직 ---
    def _detect_intrusion(self, observation):
        """내 드론에 blue 가 아닌 세션이 붙었거나 외부 연결 흔적이 있으면 침입."""
        host = observation.get(self._own_drone_key(), {})
        for sess in host.get("Sessions", []):
            if "blue" not in str(sess.get("Agent", "")):
                return True
        for iface in host.get("Interface", []):
            if iface.get("NetworkConnections"):
                return True
        return False

    # --- 정수 액션 인덱스 탐색 ---
    def _find_index(self, action_name):
        for idx, act in self.action_map.items():
            if type(act).__name__ == action_name:
                return idx
        return None

    def _retake_indices(self):
        """복구(RetakeControl) 가능한 모든 정수 액션 인덱스 목록."""
        return [idx for idx, act in self.action_map.items()
                if type(act).__name__ == "RetakeControl"]

    def get_action(self, observation, action_space):
        # runner 는 action_space 자리에 정수->Action 매핑을 넘겨준다.
        if isinstance(action_space, dict):
            self.action_map = action_space

        # 1) 격리 최우선: 내 드론에 침입 세션이 보이면 그것만 제거
        if self._detect_intrusion(observation):
            idx = self._find_index("RemoveOtherSessions")
            if idx is not None:
                return idx

        # 2) 복구: 뺏긴 '다른' 드론을 RetakeControl 로 되찾는다
        #    (내 드론이 뺏기면 나는 이미 죽어 못 하므로, 살아있는 내가 이웃을 복구)
        if self.np_random.random() < self.RETAKE_PROBABILITY:
            retakes = self._retake_indices()
            if retakes:
                return self.np_random.choice(retakes)

        # 3) 할 일 없음: Sleep 으로 자원 절약 (가용성 보존)
        idx = self._find_index("Sleep")
        return idx if idx is not None else 0

    # --- BaseAgent 필수 인터페이스 ---
    def train(self, results: Results):
        pass

    def end_episode(self):
        self.__init__(self.name, self.np_random)

    def set_initial_values(self, action_space, observation):
        pass
