"""
방어 에이전트 (Blue / 아군 드론)
================================
방산 도메인의 '탐지 -> 격리 -> 복구 -> 가용성 유지' 방어 파이프라인을
규칙 기반으로 구현한다. 드론 1대당 방어 에이전트 1개가 분산 배치된다.

핵심 원칙 (가용성 보존):
  - 위협이 없으면 Sleep 으로 자원을 아낀다. (전체망 차단 금지 원칙)
  - 침입 세션이 탐지되면 RemoveOtherSessions 로 '그 세션만' 격리한다.
  - 드론을 뺏겼으면 RetakeControl 로 복구한다.

정수 액션 매핑:
  CybORG PettingZoo 래퍼는 정수 액션을 쓴다. runner 가 넘겨주는
  action_map(정수 -> Action 객체)에서 원하는 행동 유형의 인덱스를 찾아 반환한다.
"""

from CybORG.Agents import BaseAgent
from CybORG.Shared import Results


class ReactiveDefenseAgent(BaseAgent):
    """반응형 규칙 기반 방어 에이전트."""

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

    def _detect_lost(self, observation):
        """내 드론에 내 blue root 세션이 없으면 장악당한 것 -> 복구 대상 IP 반환."""
        host = observation.get(self._own_drone_key(), {})
        sessions = host.get("Sessions", [])
        has_blue = any("blue" in str(s.get("Agent", "")) for s in sessions)
        if not has_blue and sessions is not None:
            for iface in host.get("Interface", []):
                if "IP Address" in iface:
                    return iface["IP Address"]
        return None

    # --- 정수 액션 인덱스 탐색 ---
    def _find_index(self, action_name, ip=None):
        for idx, act in self.action_map.items():
            if type(act).__name__ != action_name:
                continue
            if ip is None or getattr(act, "ip_address", None) == ip:
                return idx
        return None

    def get_action(self, observation, action_space):
        # runner 는 action_space 자리에 정수->Action 매핑을 넘겨준다.
        if isinstance(action_space, dict):
            self.action_map = action_space

        # 1) 복구 최우선: 뺏긴 드론이면 RetakeControl
        lost_ip = self._detect_lost(observation)
        if lost_ip is not None:
            idx = self._find_index("RetakeControl", lost_ip)
            if idx is None:
                idx = self._find_index("RetakeControl")
            if idx is not None:
                return idx

        # 2) 격리: 침입 세션 탐지되면 RemoveOtherSessions
        if self._detect_intrusion(observation):
            idx = self._find_index("RemoveOtherSessions")
            if idx is not None:
                return idx

        # 3) 위협 없음: Sleep 으로 자원 절약 (가용성 보존)
        idx = self._find_index("Sleep")
        return idx if idx is not None else 0

    # --- BaseAgent 필수 인터페이스 ---
    def train(self, results: Results):
        pass

    def end_episode(self):
        self.__init__(self.name, self.np_random)

    def set_initial_values(self, action_space, observation):
        pass
