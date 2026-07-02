"""
공격 에이전트 (Red / 적 드론) — 가용성 공격 집중 버전
======================================================
개선 근거 논문: Y.-M. Kwon et al., "Empirical Analysis of MAVLink Protocol
Vulnerability for UAVs," IEEE Access, 2018. (DOI 10.1109/ACCESS.2018.2863237)

논문에서 가져온 것:
  - ICMP 플러딩 공격(가용성 붕괴): 대상에 요청을 퍼부어 과부하 → 제어·센서·임무
    메시지가 제때 전달되지 못하게 만든다. => FloodBandwidth 로 모사, 비중을 높였다.
  - 관찰 → 분석 → 타격 → 피드백의 적응형 공격 파이프라인.
  - 상태 식별 후 '서비스 중인 표적'을 공격: 이미 장악한 드론은 통신이 이미 죽었으므로
    때려봐야 낭비. 아직 장악 안 된 드론에만 플러딩을 집중한다.
  - 패킷 주입(임무 무력화): MISSION_COUNT 는 CybORG에 없어 Exploit → Seize 로 대응(보조).

전략 한 줄: 정상 사용자(green)의 통신을 최대한 많이 붕괴시켜 상대 가용성을 깎는다.
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
    """가용성 공격 집중형 적응 공격 에이전트."""

    # 가용성 공격(FloodBandwidth) 비중. 1.0에 가까울수록 가용성 붕괴에 집중.
    FLOOD_PROBABILITY = 0.7

    def __init__(self, name, np_random=None):
        super().__init__(name, np_random)
        self.own_ip = None
        self.target_ip = None       # 현재 침투 시도 중인 표적
        self.seized = set()         # 이미 장악한 드론 IP
        self.flood_count = {}       # 피드백: 타겟별 플러딩 횟수 (분산 타격용)

    def _own_drone_key(self):
        """자신이 올라탄 드론의 관측 키 (예: red_agent_3 -> drone_3)."""
        return "drone_" + self.name.split("_")[-1]

    def _neighbors(self, observation):
        """관찰: 주변 드론 IP 목록(자기 자신 제외) = 공격 대상 후보."""
        ips = []
        for key, val in observation.items():
            if key == "success" or not isinstance(val, dict):
                continue
            iface = val.get("Interface")
            if iface and "IP Address" in iface[0]:
                ips.append(iface[0]["IP Address"])
        return [ip for ip in ips if ip != self.own_ip]

    def get_action(self, observation, action_space):
        # 1) 관찰: 자기 IP 파악
        if self.own_ip is None:
            try:
                self.own_ip = observation[self._own_drone_key()]["Interface"][0]["IP Address"]
            except Exception:
                self.own_ip = None

        success = str(observation.get("success", ""))

        # 4) 피드백: 직전 침투가 성공했다면 곧바로 장악(서비스에서 제거 → 가용성 저하)
        if self.target_ip is not None and "TRUE" in success:
            ip = self.target_ip
            self.target_ip = None
            self.seized.add(ip)
            return SeizeControl(ip_address=ip, agent=self.name, session=0)

        # 2) 분석: 공격 대상 후보 목록
        targets = self._neighbors(observation)
        if not targets:
            return Sleep()

        # 3) 타격(주력): 가용성 공격 = FloodBandwidth
        #    [논문 반영] "상태 식별 후 서비스 중인 표적을 공격"(Kwon et al.).
        #    이미 장악한 드론은 정상 통신이 이미 죽었으므로 때려봐야 낭비다.
        #    아직 장악 안 된(=green 을 서비스 중인) 드론에만 플러딩을 집중해,
        #    같은 힘으로 더 많은 정상 통신을 붕괴시킨다. 그 안에서 덜 때린 드론을 고른다.
        if self.np_random.random() < self.FLOOD_PROBABILITY:
            serving = [ip for ip in targets if ip not in self.seized] or targets
            target = min(serving, key=lambda ip: self.flood_count.get(ip, 0))
            self.flood_count[target] = self.flood_count.get(target, 0) + 1
            return FloodBandwidth(ip_address=target, agent=self.name, session=0)

        # 3-2) 보조: 미장악 드론 침투 → 다음 스텝에 장악(영구적으로 서비스 제거)
        candidates = [ip for ip in targets if ip not in self.seized] or targets
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
