"""
공격 에이전트 (Baseline) — 개선 전 1차 버전
==========================================
탐색·장악 위주의 규칙 기반 공격. (가용성 공격 집중 개선 '전' 상태)
current(attack_agent.py)와 비교하기 위한 기준선으로 남겨둔다.

차이점:
  - FLOOD_PROBABILITY 가 낮다(0.3) → 장악 시도 위주, 가용성 압박이 약함.
  - 타겟을 무작위로 고른다(분산 타격 로직 없음).
"""

from CybORG.Agents import BaseAgent
from CybORG.Shared import Results
from CybORG.Simulator.Actions import (
    ExploitDroneVulnerability,
    FloodBandwidth,
    SeizeControl,
    Sleep,
)


class BaselineAttackAgent(BaseAgent):
    """개선 전 기준선 공격 에이전트 (탐색·장악 위주)."""

    FLOOD_PROBABILITY = 0.3   # 가용성 공격 비중이 낮음

    def __init__(self, name, np_random=None):
        super().__init__(name, np_random)
        self.own_ip = None
        self.target_ip = None
        self.seized = set()

    def _own_drone_key(self):
        return "drone_" + self.name.split("_")[-1]

    def _neighbors(self, observation):
        ips = []
        for key, val in observation.items():
            if key == "success" or not isinstance(val, dict):
                continue
            iface = val.get("Interface")
            if iface and "IP Address" in iface[0]:
                ips.append(iface[0]["IP Address"])
        return [ip for ip in ips if ip != self.own_ip]

    def get_action(self, observation, action_space):
        if self.own_ip is None:
            try:
                self.own_ip = observation[self._own_drone_key()]["Interface"][0]["IP Address"]
            except Exception:
                self.own_ip = None

        success = str(observation.get("success", ""))

        # 피드백: 직전 침투 성공 시 장악
        if self.target_ip is not None and "TRUE" in success:
            ip = self.target_ip
            self.target_ip = None
            self.seized.add(ip)
            return SeizeControl(ip_address=ip, agent=self.name, session=0)

        targets = self._neighbors(observation)
        if not targets:
            return Sleep()

        # 가용성 공격은 낮은 확률로만
        if self.np_random.random() < self.FLOOD_PROBABILITY:
            target = self.np_random.choice(targets)   # 무작위 타겟 (분산 로직 없음)
            return FloodBandwidth(ip_address=target, agent=self.name, session=0)

        # 주력: 미장악 드론 침투 → 다음 스텝 장악
        candidates = [ip for ip in targets if ip not in self.seized] or targets
        target = self.np_random.choice(candidates)
        self.target_ip = target
        return ExploitDroneVulnerability(ip_address=target, agent=self.name, session=0)

    def train(self, results: Results):
        pass

    def end_episode(self):
        self.__init__(self.name, self.np_random)

    def set_initial_values(self, action_space, observation):
        pass
