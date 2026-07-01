"""
공격 에이전트 (Red / 적 드론)
=============================
방산 도메인의 '관찰 -> 분석 -> 타격 -> 피드백' 적응형 공격 파이프라인을
규칙 기반으로 구현한다. CybORG 의 BaseAgent 인터페이스를 따르며,
시나리오에 default_red_agent 로 주입되어 적 드론들을 조종한다.

전략 (도메인 매핑):
  1) 관찰: 주변 드론들의 IP 를 수집한다.
  2) 분석: 아직 장악하지 못한 드론을 표적으로 고른다.
  3) 타격: ExploitDroneVulnerability(취약점 공격) 로 침투를 시도한다.
  4) 피드백: 침투가 성공하면 다음 스텝에 SeizeControl(제어권 탈취)로 장악한다.
  * 일정 확률로 FloodBandwidth(대역폭 소모=재밍/DoS 모사)를 섞어 가용성을 압박한다.
"""

from CybORG.Agents import BaseAgent
from CybORG.Shared import Results
from CybORG.Simulator.Actions import (
    ExploitDroneVulnerability,
    FloodBandwidth,
    SeizeControl,
    Sleep,
)


class AdaptiveAttackAgent(BaseAgent):
    """적응형 규칙 기반 공격 에이전트."""

    # 대역폭 소모(가용성 공격)를 시도할 확률
    FLOOD_PROBABILITY = 0.3

    def __init__(self, name, np_random=None):
        super().__init__(name, np_random)
        self.own_ip = None
        self.target_ip = None      # 현재 침투 시도 중인 표적
        self.seized = set()        # 이미 장악한 드론 IP

    def _own_drone_key(self):
        """자신이 올라탄 드론의 관측 키 (예: red_agent_3 -> drone_3)."""
        return "drone_" + self.name.split("_")[-1]

    def get_action(self, observation, action_space):
        # --- 자기 IP 파악 ---
        if self.own_ip is None:
            try:
                self.own_ip = observation[self._own_drone_key()]["Interface"][0]["IP Address"]
            except Exception:
                self.own_ip = None

        success = str(observation.get("success", ""))

        # --- 4) 피드백: 직전 침투가 성공했다면 곧바로 제어권 탈취 ---
        if self.target_ip is not None and "TRUE" in success:
            ip = self.target_ip
            self.target_ip = None
            self.seized.add(ip)
            return SeizeControl(ip_address=ip, agent=self.name, session=0)

        # --- 1) 관찰: 주변 드론 IP 목록 수집 ---
        ip_list = []
        for key, val in observation.items():
            if key == "success" or not isinstance(val, dict):
                continue
            iface = val.get("Interface")
            if iface and "IP Address" in iface[0]:
                ip_list.append(iface[0]["IP Address"])
        ip_list = [ip for ip in ip_list if ip != self.own_ip]

        if not ip_list:
            return Sleep()

        # --- 가용성 공격(FloodBandwidth = 재밍/DoS 모사) ---
        if self.np_random.random() < self.FLOOD_PROBABILITY:
            target = self.np_random.choice(ip_list)
            return FloodBandwidth(ip_address=target, agent=self.name, session=0)

        # --- 2)+3) 분석 후 타격: 미장악 드론을 골라 취약점 공격 ---
        candidates = [ip for ip in ip_list if ip not in self.seized] or ip_list
        target = self.np_random.choice(candidates)
        self.target_ip = target
        return ExploitDroneVulnerability(ip_address=target, agent=self.name, session=0)

    # --- BaseAgent 필수 인터페이스 ---
    def train(self, results: Results):
        pass

    def end_episode(self):
        self.__init__(self.name, self.np_random)

    def set_initial_values(self, action_space, observation):
        pass
