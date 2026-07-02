# 논문 분석: Empirical Analysis of MAVLink Protocol Vulnerability for UAVs

Kwon, Yu, Cho, Eun, Park (DGIST), IEEE Access, 2018. DOI 10.1109/ACCESS.2018.2863237

> 목적: 논문을 "읽는 것"이 아니라, 공격 구조를 재현할 수 있을 정도로 분해해 이해한다.
> 우리 대회 연결점: 이 논문의 두 공격(ICMP 플러딩 = 가용성 붕괴, MISSION_COUNT 패킷 주입 = 임무 무력화)은
> 우리 `attack_agent.py`의 FloodBandwidth / ExploitDroneVulnerability·SeizeControl에 개념적으로 대응한다.

---

## [ABSTRACT]

### 1. 직독직해

- English: Recently, unmanned aerial vehicle (UAV) or so called drones are used in various applications.
- Korean: 최근, 무인 항공기(UAV) 또는 이른바 드론이 다양한 응용 분야에서 사용된다.

- English: Especially, UAVs are used for rescue systems, disaster detection, and military purposes, as well as for leisure and commercial purposes.
- Korean: 특히, UAV는 레저 및 상업 목적뿐 아니라 구조 시스템, 재난 탐지, 군사 목적에도 사용된다.

- English: In particular, UAVs that are controlled over networks by ground control stations (GCS) can provide various services with the expanded activity area.
- Korean: 특히, 지상관제소(GCS)에 의해 네트워크를 통해 제어되는 UAV는 확장된 활동 영역으로 다양한 서비스를 제공할 수 있다.

- English: Consequently, it is of critical importance to investigate the vulnerability of the drone system.
- Korean: 따라서, 드론 시스템의 취약점을 조사하는 것이 매우 중요하다.

- English: In this paper, we focus on the UAVs controlled by GCS over networks.
- Korean: 본 논문에서, 우리는 네트워크를 통해 GCS에 의해 제어되는 UAV에 초점을 맞춘다.

- English: We analyze the vulnerability of the micro air vehicle communication (MAVLink) protocol, which is one of the most widely adopted communication protocols for GCS-based control of UAVs.
- Korean: 우리는 UAV의 GCS 기반 제어에 가장 널리 채택된 통신 프로토콜 중 하나인 MAVLink(micro air vehicle communication) 프로토콜의 취약점을 분석한다.

- English: Then, by exploiting the vulnerability of the MAVLink protocol, we propose an attack methodology that can disable an ongoing mission of a UAV.
- Korean: 그런 다음, MAVLink 프로토콜의 취약점을 악용하여, UAV의 진행 중인 임무를 무력화할 수 있는 공격 방법론을 제안한다.

- English: Our empirical study confirms that the proposed attack can stop the attacked UAV and disable the mission.
- Korean: 우리의 실증 연구는 제안된 공격이 공격받은 UAV를 멈추게 하고 임무를 무력화할 수 있음을 확인한다.

- English (INDEX TERMS): UAV, UAS, drones, MAVLink, network attack, DoS, flooding attack, packet injection
- Korean: UAV, UAS, 드론, MAVLink, 네트워크 공격, DoS, 플러딩 공격, 패킷 주입

### 2. 핵심 개념
- 대상: 네트워크로 GCS가 제어하는 UAV.
- 표적 프로토콜: MAVLink (GCS-드론 제어의 사실상 표준).
- 두 공격: (1) DoS/플러딩, (2) 패킷 주입 → "진행 중인 임무 무력화".
- 검증: 실제 테스트베드 실험(empirical).

### 3. 공격/방어 해석
- 공격 목표: UAV를 격추가 아니라 "임무 정지". 가용성/임무지속성을 깬다.
- 깨지는 가정: "GCS와 드론 사이 메시지는 신뢰할 수 있다"는 가정.

### 4. 학습 포인트
- 배경지식: GCS, MAVLink, DoS, 패킷 주입.
- 핵심 한 줄: 암호화·인증 없는 MAVLink를 악용해 드론의 임무를 멈춘다.

---

## [INTRODUCTION]

### 1. 직독직해

- English: RECENTLY, unmanned aerial vehicles (UAV), or so called drones, have been widely used around the world for the last decade.
- Korean: 최근, 무인 항공기(UAV), 이른바 드론은 지난 10년간 전 세계적으로 널리 사용되어 왔다.

- English: Especially, we can think of various services by drones.
- Korean: 특히, 우리는 드론에 의한 다양한 서비스를 생각할 수 있다.

- English: For example, drone network provides services for various drone applications [1], such as rescue systems [2], disaster monitoring [3, 4], commercial use, military mission, and so on.
- Korean: 예를 들어, 드론 네트워크는 구조 시스템[2], 재난 모니터링[3,4], 상업적 이용, 군사 임무 등 다양한 드론 응용[1]을 위한 서비스를 제공한다.

- English: An example of a commercial service using UAVs is Amazon's project Prime-Air, which was released in 2015 [5].
- Korean: UAV를 이용한 상업 서비스의 한 예는 2015년에 공개된 아마존의 프로젝트 Prime-Air[5]이다.

- English: This system aims to design a future delivery service using UAVs.
- Korean: 이 시스템은 UAV를 이용한 미래 배송 서비스를 설계하는 것을 목표로 한다.

- English: Since then, various services utilizing UAVs such as Fleetlight [6] and Matternet [7] have been released, as shown in Fig. 1.
- Korean: 그 이후, 그림 1에 보이듯 Fleetlight[6]와 Matternet[7] 같은 UAV 활용 서비스가 다양하게 출시되었다.

- English: In this way, services using UAVs are mainly performed in environments that are controlled over networks as shown in Fig. 2.
- Korean: 이런 식으로, UAV를 이용한 서비스는 주로 그림 2와 같이 네트워크를 통해 제어되는 환경에서 수행된다.

- English: Controlling the UAV over a network allows the UAV to perform its mission by completing the mission without user control.
- Korean: 네트워크를 통해 UAV를 제어하는 것은 사용자 제어 없이 임무를 완수함으로써 UAV가 임무를 수행하게 한다.

- English: However, as the demands for the services using UAVs are increasing, the negative use cases are also rapidly increasing.
- Korean: 그러나, UAV를 이용한 서비스 수요가 증가함에 따라, 부정적 사용 사례도 급격히 증가하고 있다.

- English: Therefore, we need methodologies that can disable malicious UAVs.
- Korean: 따라서, 우리는 악성 UAV를 무력화할 수 있는 방법론이 필요하다.

- English: In this paper, we focus on the UAVs controlled by GCS over networks.
- Korean: 본 논문에서, 우리는 네트워크를 통해 GCS로 제어되는 UAV에 초점을 맞춘다.

- English: We empirically analyze the vulnerability of the micro air vehicle communication (MAVLink) protocol, which is one of the most popular protocols used for GCS-based control of UAV [8].
- Korean: 우리는 UAV의 GCS 기반 제어에 사용되는 가장 인기 있는 프로토콜 중 하나인 MAVLink 프로토콜[8]의 취약점을 실증적으로 분석한다.

- English: It should be noted that there exist few empirical studies on the vulnerability of the MAVLink protocol.
- Korean: MAVLink 프로토콜 취약점에 대한 실증 연구가 거의 없다는 점을 유의해야 한다.

- English: By exploiting the vulnerability of the MAVLink protocol, we propose an attack methodology that can disable an ongoing mission of the UAV.
- Korean: MAVLink 프로토콜의 취약점을 악용하여, 우리는 UAV의 진행 중인 임무를 무력화할 수 있는 공격 방법론을 제안한다.

- English: We empirically validate the proposed attack methodology with a UAV testbed.
- Korean: 우리는 제안된 공격 방법론을 UAV 테스트베드로 실증적으로 검증한다.

- English: Our experimental results confirms that the attacked UAV is stopped and the mission disabled.
- Korean: 우리의 실험 결과는 공격받은 UAV가 멈추고 임무가 무력화됨을 확인한다.

- English: We identify the vulnerability of the MAVLink protocol, a de facto standard for UAV and GCS communication.
- Korean: 우리는 UAV와 GCS 통신의 사실상 표준인 MAVLink 프로토콜의 취약점을 식별한다.

- English: By exploiting the identified protocol vulnerability, we develop an attack methodology that can disable the mission of UAVs.
- Korean: 식별된 프로토콜 취약점을 악용하여, 우리는 UAV의 임무를 무력화할 수 있는 공격 방법론을 개발한다.

- English: The rest of the paper is organized as follows. (이하 논문 구성 안내 — Section II 배경, III 제안 공격, IV 실험, V 관련연구, VI 결론)
- Korean: 논문의 나머지는 다음과 같이 구성된다. (II장 배경, III장 UAV 무력화 제안 기법, IV장 실험 환경·시나리오, V장 기존 연구, VI장 결론)

### 2. 핵심 개념
- 문제의식: UAV는 네트워크 제어가 표준이 됐고, 악성 UAV를 멈출 방법이 필요.
- 갭: MAVLink 취약점의 "실증" 연구가 드물다 → 이 논문이 실제 드론으로 검증.
- 기여 2가지: 취약점 식별 + 실증 공격 방법론.

### 3. 공격/방어 해석
- 위협 모델의 전제: 공격자가 UAV-GCS 네트워크에 이미 침투했다고 가정(뒤 III장에서 명시).
- 공격 벡터: MAVLink의 비암호화 특성.

### 4. 학습 포인트
- "de facto standard(사실상 표준)" = 공식 표준은 아니나 현장에서 사실상 표준처럼 쓰임 → 공격의 범용성 근거.
- 핵심 한 줄: MAVLink가 워낙 널리 쓰이므로, 그 취약점 하나가 광범위한 드론에 통한다.

---

## [BACKGROUND (Section II)]

### 1. 직독직해

**A. Drone Control Structure**

- English: There are basically two ways to control a UAV; using a controller and using a ground control station (GCS) as shown in Fig. 3.
- Korean: UAV를 제어하는 방법은 기본적으로 두 가지이다; 그림 3과 같이 컨트롤러를 사용하는 것과 지상관제소(GCS)를 사용하는 것.

- English: In controller-based control, the user views the UAV directly or watches through a camera mounted on the UAV and controls it using the controller.
- Korean: 컨트롤러 기반 제어에서, 사용자는 UAV를 직접 보거나 UAV에 장착된 카메라를 통해 보면서 컨트롤러로 제어한다.

- English: The UAV and the controller are connected to a communication module, and the UAV is controlled by transmitting the controller's signal to the UAV in real time.
- Korean: UAV와 컨트롤러는 통신 모듈로 연결되며, 컨트롤러의 신호를 실시간으로 UAV에 전송하여 UAV를 제어한다.

- English: Generally, the communication modules used are telemetry, Wi-Fi, ZigBee, and so on.
- Korean: 일반적으로 사용되는 통신 모듈은 텔레메트리, 와이파이, 지그비 등이다.

- English: On the other hand, GCS-based control uses a computer to connect the managing software and the UAV; GCS then performs mission commands uploaded by the user.
- Korean: 반면, GCS 기반 제어는 컴퓨터를 사용해 관리 소프트웨어와 UAV를 연결한다; 그런 다음 GCS는 사용자가 업로드한 임무 명령을 수행한다.

- English: GCS can monitor the status of the UAV by receiving information of various sensors mounted on the UAV such as current altitude, speed, map position, and current mission status.
- Korean: GCS는 현재 고도, 속도, 지도상 위치, 현재 임무 상태 등 UAV에 장착된 다양한 센서 정보를 수신하여 UAV의 상태를 모니터링할 수 있다.

- English: The controller-based method can manually control the UAV in real time while GCS-based control enables stable flight as well as unassisted flight to complete autonomous missions.
- Korean: 컨트롤러 기반 방식은 UAV를 실시간으로 수동 제어할 수 있는 반면, GCS 기반 제어는 안정적 비행과 더불어 자율 임무 완수를 위한 무인(보조 없는) 비행을 가능하게 한다.

- English: Here, we consider GCS-based control for our study.
- Korean: 여기서, 우리는 연구를 위해 GCS 기반 제어를 고려한다.

**B. MAVLink Protocol**

- English: The MAVLink protocol is a message-based UAV communication protocol developed by Lorenz Meier in 2009 [8].
- Korean: MAVLink 프로토콜은 2009년 Lorenz Meier가 개발한 메시지 기반 UAV 통신 프로토콜이다.

- English: In addition, the MAVLink protocol is a part of the current DroneCode project and is used by thousands of developers.
- Korean: 또한, MAVLink 프로토콜은 현재 DroneCode 프로젝트의 일부이며 수천 명의 개발자가 사용한다.

- English: It is also used in numerous Autopilot-based systems such as ArdupilotMega, pxIMU Autopilot, and SLUGS Autopilot [9].
- Korean: 그것은 ArdupilotMega, pxIMU Autopilot, SLUGS Autopilot[9] 같은 수많은 오토파일럿 기반 시스템에서도 사용된다.

- English: MAVLink packets are bidirectionally transferred between UAV and GCS as header-based messages.
- Korean: MAVLink 패킷은 헤더 기반 메시지로서 UAV와 GCS 사이에서 양방향으로 전송된다.

- English: The GCS sends mission commands to the UAV, and the UAV transmits state information including the sensor value, and current position to the GCS.
- Korean: GCS는 UAV에 임무 명령을 보내고, UAV는 센서 값과 현재 위치를 포함한 상태 정보를 GCS에 전송한다.

- English: Fig. 4 shows the message structure of the MAVLink protocol and Table 1 shows the meaning of the MAVLink frame [8].
- Korean: 그림 4는 MAVLink 프로토콜의 메시지 구조를, 표 1은 MAVLink 프레임의 의미를 보여준다.

**MAVLink 프레임 구조 (Table 1 / Fig 4) 직독:**
- STX (byte 0, 0xFE): Indicates start of a new packet → 새 패킷의 시작을 나타냄. (헤더 인식의 핵심)
- LEN (byte 1, 0-255): payload 길이.
- SEQ (byte 2): 패킷 손실 감지를 위한 전송 순서 정보.
- SYS (byte 3, 1-255): 보내는 시스템 ID; 같은 네트워크의 여러 플랫폼 식별.
- COMP (byte 4): 보내는 컴포넌트 ID.
- MSG (byte 5): 메시지 ID; payload의 의미와 디코딩 방법 정의.
- Payload (6~n+6): 메시지 데이터; MSG ID에 따라 달라짐.
- Checksum CKA/CKB (n+7~n+8): bytes 1~(n+6)의 해시, MAVLINK_CRC_EXTRA 포함.

**C. Network Attack**

- English: Network attacks violate the confidentiality, integrity, and availability of the system.
- Korean: 네트워크 공격은 시스템의 기밀성, 무결성, 가용성을 침해한다.

- English: Confidentiality allows information on the system only to authorized users.
- Korean: 기밀성은 시스템 정보를 인가된 사용자에게만 허용한다.

- English: If confidentiality is violated, it is possible to eavesdrop on information and spoof the system.
- Korean: 기밀성이 침해되면, 정보를 도청하고 시스템을 속이는 것이 가능하다.

- English: Integrity means the original information and signals transmitted, stored, and converted are maintained and not changed afterwards.
- Korean: 무결성은 전송·저장·변환된 원본 정보와 신호가 유지되고 이후 변경되지 않음을 의미한다.

- English: Violation of integrity allows attacks such as message injection, replay attack, and so on.
- Korean: 무결성의 침해는 메시지 주입, 재전송(replay) 공격 등을 가능하게 한다.

- English: Availability allows the system to function for the time required by the user.
- Korean: 가용성은 시스템이 사용자가 요구하는 시간 동안 작동하도록 한다.

- English: In terms of maintenance, service must not be interrupted; performance must be maintained.
- Korean: 유지 관점에서, 서비스는 중단되어서는 안 되며; 성능이 유지되어야 한다.

- English: Also, in terms of access to the system, the service must be accessible whenever the user needs it.
- Korean: 또한, 시스템 접근 관점에서, 서비스는 사용자가 필요할 때 언제든 접근 가능해야 한다.

- English: Denial of service attacks can violate availability.
- Korean: 서비스 거부(DoS) 공격은 가용성을 침해할 수 있다.

- English (MITM): Man-in-the-middle (MITM) is an attack that violates the confidentiality or integrity of the system [10, 11].
- Korean: 중간자(MITM)는 시스템의 기밀성 또는 무결성을 침해하는 공격이다.

- English: As can be seen from the name, the attacker is located in the middle of the hosts and sniffs information [12].
- Korean: 이름에서 알 수 있듯, 공격자는 호스트들 사이에 위치하여 정보를 스니핑(엿봄)한다.

- English: The attacker can cause hosts to communicate information to the attacker.
- Korean: 공격자는 호스트들이 정보를 공격자에게 전달하도록 만들 수 있다.

- English: This is possible because system allows host to set the destination address to the attacker's address for address resolution protocol (ARP) poisoning.
- Korean: 이는 시스템이 ARP 포이즈닝을 위해 호스트가 목적지 주소를 공격자의 주소로 설정하도록 허용하기 때문에 가능하다.

- English: When MITM is applied to the UAV system, it is possible to eavesdrop on all of information transmitted between the UAV and GCS.
- Korean: MITM이 UAV 시스템에 적용되면, UAV와 GCS 사이에 전송되는 모든 정보를 도청하는 것이 가능하다.

- English (Eavesdropping): Eavesdropping is an attack that violates the confidentiality of the system; it means that an attacker steals and listens to information of other users.
- Korean: 도청은 시스템의 기밀성을 침해하는 공격이다; 공격자가 다른 사용자의 정보를 훔쳐 엿듣는 것을 의미한다.

- English: If an MITM attack succeeds, eavesdropping can be enabled [12]. As a method to protect the system from eavesdropping, it is necessary to encrypt the message.
- Korean: MITM 공격이 성공하면 도청이 가능해진다. 도청으로부터 시스템을 보호하는 방법으로, 메시지를 암호화하는 것이 필요하다.

- English (DoS): Denial-of-Service (DoS) attacks violate availability, monopolizing the resources of the system; using both DoS and MITM, it is possible to prevent other users from using system services [13].
- Korean: 서비스 거부(DoS) 공격은 시스템의 자원을 독점하여 가용성을 침해한다; DoS와 MITM을 함께 사용하면 다른 사용자가 시스템 서비스를 사용하지 못하게 막을 수 있다.

- English: In case of a DoS attack on a UAV system, control message, sensor information, and mission information are not correctly transmitted.
- Korean: UAV 시스템에 대한 DoS 공격의 경우, 제어 메시지·센서 정보·임무 정보가 올바르게 전송되지 않는다.

- English: Therefore, not only is the UAV not maintained in the stable state, but also the mission execution can not be performed correctly.
- Korean: 따라서, UAV가 안정 상태로 유지되지 못할 뿐 아니라, 임무 수행도 올바르게 이루어질 수 없다.

- English (Potential threats): In the UAV system, it is possible to have different vulnerabilities for each component of the system. ... Table 2 shows the potential threats that may occur for each component of the UAV system.
- Korean: UAV 시스템에서는 시스템의 각 구성 요소마다 서로 다른 취약점을 가질 수 있다. ... 표 2는 UAV 시스템의 각 구성 요소에 발생할 수 있는 잠재적 위협을 보여준다.

**Table 2 직독 (보안목표 → 시스템대상 → 공격방법):**
- 기밀성: GCS(바이러스·멀웨어·키로거·트로이목마), UAV(하이재킹), 통신링크(도청·MITM)
- 무결성: 통신링크(패킷주입·재전송·MITM·메시지삭제)
- 가용성: GCS(DoS), UAV(퍼징), 통신링크(재밍·플러딩·버퍼오버플로)

### 2. 핵심 개념
- 제어 2방식 중 이 논문은 GCS 기반(자율 임무)을 대상.
- MAVLink: 헤더 기반 메시지, 양방향(GCS→명령, UAV→상태). STX(0xFE)로 패킷 식별.
- CIA 삼각: 기밀성(도청/스푸핑), 무결성(주입/재전송), 가용성(DoS/재밍/플러딩).

### 3. 공격/방어 해석
- 이 논문이 쓰는 두 축: 무결성 침해(패킷 주입) + 가용성 침해(플러딩).
- 전제 붕괴: MITM/ARP 포이즈닝으로 "네트워크 내부는 신뢰됨" 가정이 깨짐.
- 방어 힌트(논문이 직접 언급): 메시지 암호화가 도청 방어책.

### 4. 학습 포인트
- ARP 포이즈닝 = 가짜 ARP로 트래픽을 공격자에게 돌리는 기법(MITM의 통로).
- STX가 0xFE 고정이라 암호화하면 패킷 인식이 깨진다 → 그래서 암호화를 안 함(취약점의 근원).
- 핵심 한 줄: 표 2가 UAV 공격면 지도. 우리 대회의 공격 시나리오 확장 목록으로 그대로 쓸 수 있음.

---

## [PROPOSED ATTACK METHODOLOGY (Section III)]

### 1. 직독직해

**A. Vulnerability of the MAVLink Protocol**

- English: Since the MAVLink message is a header-based protocol, it checks the first frame of the data packet and classifies the message.
- Korean: MAVLink 메시지는 헤더 기반 프로토콜이므로, 데이터 패킷의 첫 프레임을 검사하여 메시지를 분류한다.

- English: Therefore, it checks the STX value which is the initial frame and recognizes whether it is a MAVLink packet.
- Korean: 따라서, 초기 프레임인 STX 값을 검사하여 그것이 MAVLink 패킷인지 인식한다.

- English: In order to improve transfer speed and efficiency, the MAVLink message does not perform encryption [8].
- Korean: 전송 속도와 효율을 개선하기 위해, MAVLink 메시지는 암호화를 수행하지 않는다.

- English: When a message is encrypted, because the value of the header of the packet changes, the system does not recognize it as a MAVLink packet.
- Korean: 메시지가 암호화되면, 패킷 헤더의 값이 바뀌기 때문에, 시스템은 그것을 MAVLink 패킷으로 인식하지 못한다.

- English: Furthermore, it takes additional time to decrypt the data. Hence, the MAVLink protocol does not introduce encryption.
- Korean: 게다가, 데이터를 복호화하는 데 추가 시간이 걸린다. 따라서, MAVLink 프로토콜은 암호화를 도입하지 않는다.

- English: Therefore, there exists a security vulnerability of the MAVLink protocol due to non-encrypted messages.
- Korean: 따라서, 비암호화 메시지로 인해 MAVLink 프로토콜에는 보안 취약점이 존재한다.

**B. Proposed Attack Scenario**

- English: Here, by exploiting the vulnerability of the MAVLink protocol, we propose a methodology to disable a UAV. In particular, we exploit the fact that the MAVLink message is not encrypted.
- Korean: 여기서, MAVLink 프로토콜의 취약점을 악용하여, UAV를 무력화하는 방법론을 제안한다. 특히, MAVLink 메시지가 암호화되지 않는다는 사실을 악용한다.

- English: Accordingly, after sniffing the UAV network packets, we inject packets to disable the UAV.
- Korean: 그에 따라, UAV 네트워크 패킷을 스니핑한 후, UAV를 무력화하기 위해 패킷을 주입한다.

- English: We consider a UAV system in which the UAV and GCS are connected via a network an the attacker is already hacked into the network, which is possible by various existing methods.
- Korean: 우리는 UAV와 GCS가 네트워크로 연결되어 있고 공격자가 이미 네트워크에 침투한 UAV 시스템을 고려하며, 이는 기존의 다양한 방법으로 가능하다.

- English: The attack scenario is as follows: In order to decide an attack target, it is necessary to have information on the hosts connected to the network.
- Korean: 공격 시나리오는 다음과 같다: 공격 대상을 정하기 위해, 네트워크에 연결된 호스트들에 대한 정보를 갖는 것이 필요하다.

- English: Therefore, an attacker operates in the promiscuous mode and obtain all the packets and sets the target.
- Korean: 따라서, 공격자는 무차별(promiscuous) 모드로 동작하여 모든 패킷을 획득하고 대상을 설정한다.

- English: The attacker obtains the GCS and UAV packets by using an ARP poisoning attack, which sends fake ARP information to the host and makes the packet to be forwarded to the attacker.
- Korean: 공격자는 ARP 포이즈닝 공격을 사용해 GCS와 UAV 패킷을 획득하는데, 이는 호스트에 가짜 ARP 정보를 보내 패킷이 공격자에게 전달되도록 만든다.

- English: By executing packet sniffing on the drone network, an attack can get the MAVLink packets.
- Korean: 드론 네트워크에서 패킷 스니핑을 실행함으로써, 공격은 MAVLink 패킷을 얻을 수 있다.

- English: There are 160 kinds of common MAVLink packets; these packets send UAV state information or GCS commands in the MAVLink payload.
- Korean: 흔한 MAVLink 패킷은 160종류가 있다; 이 패킷들은 MAVLink payload에 UAV 상태 정보나 GCS 명령을 담아 보낸다.

- English: By analyzing the packets to be transmitted, it is possible to identify whether the UAV is currently in flight, the state of the battery, what mission is being executed.
- Korean: 전송되는 패킷을 분석함으로써, UAV가 현재 비행 중인지, 배터리 상태, 어떤 임무가 실행 중인지를 식별할 수 있다.

- English: Based on the information, the attacker can identify the actual state of the UAV and can disable the UAV by sending malicious packets to the UAV.
- Korean: 그 정보를 바탕으로, 공격자는 UAV의 실제 상태를 식별하고 UAV에 악성 패킷을 보내 UAV를 무력화할 수 있다.

- English: In this study, we use ICMP flooding attack as well as packet injection attack which exploits the vulnerability of the MAVLink waypoint protocol.
- Korean: 본 연구에서, 우리는 MAVLink 웨이포인트 프로토콜의 취약점을 악용하는 패킷 주입 공격뿐 아니라 ICMP 플러딩 공격도 사용한다.

**C. Vulnerability to Flooding Attack**

- English: Internet control message protocol (ICMP) checks the connection status of the hosts in the network and reports when there is a problem with packet transfer.
- Korean: 인터넷 제어 메시지 프로토콜(ICMP)은 네트워크 내 호스트들의 연결 상태를 확인하고 패킷 전송에 문제가 있을 때 보고한다.

- English: Using the ping command with Windows command or Linux kernel, an ICMP message can be sent.
- Korean: Windows 명령이나 Linux 커널의 ping 명령을 사용해 ICMP 메시지를 보낼 수 있다.

- English: When sending an ICMP message, the sender will send an ICMP request packet to the receiver. Then, the receiver that has successfully received the request message will respond to the sender.
- Korean: ICMP 메시지를 보낼 때, 송신자는 수신자에게 ICMP 요청 패킷을 보낸다. 그러면, 요청 메시지를 성공적으로 받은 수신자는 송신자에게 응답한다.

- English: If the sender sends a large number of request messages, the receiver will be overloaded to check and send replies.
- Korean: 송신자가 다수의 요청 메시지를 보내면, 수신자는 확인하고 응답을 보내느라 과부하가 걸린다.

- English: In this way, the ICMP flooding attack overloads the target system and invalidates the service.
- Korean: 이런 식으로, ICMP 플러딩 공격은 대상 시스템에 과부하를 걸어 서비스를 무효화한다.

**D. Vulnerability of MAVLink Waypoint Protocol to Packet Injection**

- English: When using GCS to control the UAV, UAV executes the mission commands sent by GCS. At this time, mission commands are executed based on the waypoint protocol [30] in the MAVLink protocol.
- Korean: GCS로 UAV를 제어할 때, UAV는 GCS가 보낸 임무 명령을 실행한다. 이때, 임무 명령은 MAVLink 프로토콜의 웨이포인트 프로토콜[30]에 기반해 실행된다.

- English: When the user completes the mission commands setting, the GCS sends information on the total number of missions as a MISSION_COUNT (N) message.
- Korean: 사용자가 임무 명령 설정을 완료하면, GCS는 전체 임무 수 정보를 MISSION_COUNT (N) 메시지로 보낸다.

- English: Upon receiving this message, the UAV requests the first mission information using the MISSION_REQUEST (0) message.
- Korean: 이 메시지를 받으면, UAV는 MISSION_REQUEST (0) 메시지를 사용해 첫 번째 임무 정보를 요청한다.

- English: In response to this message, the GCS sends the first mission information with a MISSION_ITEM (0) message.
- Korean: 이 메시지에 응답하여, GCS는 MISSION_ITEM (0) 메시지로 첫 번째 임무 정보를 보낸다.

- English: In this way, the GCS sends a total of N pieces of mission information to the UAV. Upon completion of the mission information transfer, the UAV transmits a MISSION_ACK message to the GCS to notify that the transmission is completed.
- Korean: 이런 식으로, GCS는 총 N개의 임무 정보를 UAV에 보낸다. 임무 정보 전송이 완료되면, UAV는 전송 완료를 알리기 위해 GCS에 MISSION_ACK 메시지를 전송한다.

- English: We exploit the vulnerability of the waypoint protocol and carry out experiments with packet injection attack. When the GCS sends a MISSION_COUNT (N) packet, the UAV erases the stored mission information and prepares to receive new mission commands.
- Korean: 우리는 웨이포인트 프로토콜의 취약점을 악용하여 패킷 주입 공격 실험을 수행한다. GCS가 MISSION_COUNT (N) 패킷을 보내면, UAV는 저장된 임무 정보를 지우고 새 임무 명령을 받을 준비를 한다.

- English: Because the attacker had intruded into the network, the attacker is able to eavesdrop the information between GCS-UAV and obtain the mission information.
- Korean: 공격자가 네트워크에 침투했기 때문에, 공격자는 GCS-UAV 사이 정보를 도청하여 임무 정보를 획득할 수 있다.

- English: After this, when the UAV executes the mission and starts the flight, the attacker sends an eavesdropped MISSION_COUNT (N) packet to the UAV and initialize the mission information.
- Korean: 이후, UAV가 임무를 실행하고 비행을 시작하면, 공격자는 도청한 MISSION_COUNT (N) 패킷을 UAV에 보내 임무 정보를 초기화한다.

- English: UAV sends MISSION_REQUEST to GCS to request mission information, but GCS has already sent mission information so it will not transmit.
- Korean: UAV는 임무 정보를 요청하기 위해 GCS에 MISSION_REQUEST를 보내지만, GCS는 이미 임무 정보를 보냈으므로 전송하지 않는다.

- English: Therefore, the UAV enters a standby state waiting for mission information.
- Korean: 따라서, UAV는 임무 정보를 기다리는 대기 상태에 들어간다.

**E. Packet Monitoring and Injection (도구)**
- Cain & Abel: 네트워크 스니핑(호스트 IP 파악) + ARP 포이즈닝.
- Jpcap: 자바 기반 패킷 캡처 → 실시간 상태 모니터링 도구 자체 개발(MISSION_SET_CURRENT로 현재 임무·비행 여부 판단).
- Packet Sender: UDP/TCP 공격 패킷 주입(원하는 payload로 변경 가능).

### 2. 핵심 개념
- 취약점 원천: STX 헤더 인식 구조 때문에 암호화 불가 → 비암호화.
- 공격 2종:
  1) ICMP 플러딩 → 수신 과부하 → 제어/센서/임무 메시지 지연·유실 (가용성 붕괴).
  2) MISSION_COUNT(N) 주입 → UAV가 저장 임무 삭제·초기화 → GCS는 재전송 안 함 → UAV 무한 대기(호버링).
- 전제: 공격자는 이미 네트워크 내부 + ARP 포이즈닝으로 MITM.

### 3. 공격/방어 해석
- 입력(공격자): 도청한 MISSION_COUNT(N) 패킷 1개.
- 출력(효과): 드론이 임무 삭제 후 제자리 호버링(추락 없이 임무 정지).
- 깨지는 가정: "MISSION_COUNT는 GCS만 보낸다"는 신뢰 → 인증 없음이 근본 원인.
- 우리 대회 매핑: MISSION_COUNT 주입 = `ExploitDroneVulnerability`→상태 교란, ICMP 플러딩 = `FloodBandwidth`(가용성 공격).

### 4. 학습 포인트
- promiscuous mode = NIC가 자기 앞 패킷뿐 아니라 모든 패킷을 받아들이는 모드(스니핑 전제).
- waypoint protocol handshake: COUNT(N) → REQUEST(0) → ITEM(0) → ... → ACK. 이 순서의 상태기계를 공격이 악용.
- 핵심 한 줄: "가짜 MISSION_COUNT 한 방"이면 드론은 스스로 임무를 지우고 멈춘다. 인증 부재가 치명적.

---

## [ATTACK IMPLEMENTATION (Section IV)]

### 1. 직독직해

**A. Testbed Configuration**
- English: We install hostapd [27] in raspberry-pi3 for the wireless access point, which will be used for connecting the UAV and GCS. We use 3DR X8 + drone ... Since this drone uses pixhawk, it can be controlled using the MAVLink protocol. ... we use raspberry-pi3, which includes installing mavproxy [28].
- Korean: 무선 AP를 위해 라즈베리파이3에 hostapd[27]를 설치하며, 이는 UAV와 GCS 연결에 사용된다. 실험에는 3DR X8+ 드론을 사용한다. 이 드론은 pixhawk를 쓰므로 MAVLink 프로토콜로 제어할 수 있다. 드론을 AP에 연결하기 위해 mavproxy[28]를 설치한 라즈베리파이3를 사용한다. (GCS는 mission planner[29].)

**B. ICMP Flooding Attack**
- English: First, when the attacker sends ICMP request packets to the GCS and the UAV at 7 Mb/s.
- Korean: 먼저, 공격자가 GCS와 UAV에 7 Mb/s로 ICMP 요청 패킷을 보낸다.

- English: In the normal case, the variance of the inter-reception time is measured at about 0.238×10⁻³; in the case of ICMP attack, the variance of the inter-reception time is measured at about 8.4×10⁻³.
- Korean: 정상 경우, 수신 간 시간(inter-reception time)의 분산은 약 0.238×10⁻³로 측정된다; ICMP 공격의 경우, 그 분산은 약 8.4×10⁻³로 측정된다.

- English: The variance of the inter-reception time during the ICMP attack is about 35 times larger than that of the normal case.
- Korean: ICMP 공격 동안 수신 간 시간의 분산은 정상 경우보다 약 35배 크다. (UAV 대상 기준. GCS 대상은 약 10배: 2.42×10⁻³.)

- English: A heartbeat message is sent between the GCS and the UAV in one second period to maintain the connection. If the heartbeat message is not received for longer than 3 seconds, the UAV will operate in failsafe mode.
- Korean: 연결 유지를 위해 GCS와 UAV 사이에 1초 주기로 하트비트 메시지가 전송된다. 하트비트 메시지가 3초 넘게 수신되지 않으면, UAV는 페일세이프 모드로 동작한다.

- English: In this experiment, because of the ICMP flooding attack, the UAV can not receive a heartbeat message within 3 seconds.
- Korean: 이 실험에서, ICMP 플러딩 공격 때문에, UAV는 3초 이내에 하트비트 메시지를 수신하지 못한다.

**C. Packet Injection Attack**
- English: As a result of the experiment, we can confirm that the UAV starts to hover immediately after receiving the MISSION_COUNT (N) packet.
- Korean: 실험 결과, UAV가 MISSION_COUNT (N) 패킷을 받은 직후 호버링을 시작함을 확인할 수 있다.

- English: This is because all of the mission information that the GCS has sent before are deleted due to the MISSION_COUNT (N) packet that has been forwarded.
- Korean: 이는 전달된 MISSION_COUNT (N) 패킷 때문에 GCS가 이전에 보낸 모든 임무 정보가 삭제되기 때문이다.

- English: In Fig. 13, "not loading waypoint" appears on the console screen after receiving the MISSION_COUNT (N) packet while waypoint 2 is executing.
- Korean: 그림 13에서, 웨이포인트 2가 실행 중일 때 MISSION_COUNT (N) 패킷을 받은 후 콘솔 화면에 "not loading waypoint"가 나타난다.

- English: In this state, the UAV continuously hovers unless the battery is exhausted or a new mission command is transmitted.
- Korean: 이 상태에서, UAV는 배터리가 소진되거나 새 임무 명령이 전송되지 않는 한 계속 호버링한다.

- English: When the UAV is in the hovering state, if an attacker injects a packet containing mission information, the UAV will execute the mission sent by the attacker.
- Korean: UAV가 호버링 상태일 때, 공격자가 임무 정보를 담은 패킷을 주입하면, UAV는 공격자가 보낸 임무를 실행하게 된다.

- English: Other UAV attacks usually cause unpredictable secondary damage due to the UAV's ground crash, while our attack does not cause crashes because the UAV is forced to be hovering around.
- Korean: 다른 UAV 공격들은 보통 UAV의 지상 추락으로 예측 불가한 2차 피해를 유발하는 반면, 우리의 공격은 UAV가 강제로 호버링하게 되므로 추락을 일으키지 않는다.

- English: Fig. 12(b) shows the ground speed of the UAV under a packet injection attack. We perform the packet injection attack just before the waypoint of the UAV is changed. ... the UAV stops the mission under the packet injection attack and hovers around in a few seconds.
- Korean: 그림 12(b)는 패킷 주입 공격 하의 UAV 지상 속도를 보여준다. 우리는 UAV의 웨이포인트가 바뀌기 직전에 패킷 주입 공격을 수행한다. ... UAV는 패킷 주입 공격 하에서 임무를 멈추고 몇 초 안에 호버링한다.

**D. SITL Simulator**
- English: Here, with the software in the loop (SITL) simulator [31], the experiment scenario conducted in Section IV.B and C are performed in the same way.
- Korean: 여기서, SITL(software in the loop) 시뮬레이터[31]로, IV.B와 C에서 수행한 실험 시나리오를 동일하게 수행한다.

- English: As in the previous experiment, when the UAV receives the MISSION_COUNT (N) packet, we can confirm that "not loading waypoints" is displayed on the command screen.
- Korean: 이전 실험과 마찬가지로, UAV가 MISSION_COUNT (N) 패킷을 받으면 명령 화면에 "not loading waypoints"가 표시됨을 확인할 수 있다.

### 2. 핵심 개념
- 테스트베드: 라즈베리파이3(AP+mavproxy) + 3DR X8+ (pixhawk) + Mission Planner(GCS).
- 플러딩 효과: 패킷 수신 간격 분산 급증(정상 대비 UAV 35배). 하트비트 3초 미수신 → 페일세이프.
- 주입 효과: MISSION_COUNT(N) 한 번 → 임무 삭제 → "not loading waypoint" → 무한 호버링.
- SITL로도 동일 재현(=우리 시뮬레이션에서도 재현 가능함을 시사).

### 3. 공격/방어 해석
- 관측 지표: (1) 패킷 수신 간 시간 분산, (2) ground speed, (3) 하트비트 수신 여부, (4) 콘솔의 "not loading waypoint".
- 공격 특성: 추락 없이 임무만 정지 → "가용성 저하"에 특화된 조용한 공격.
- 방어 관점: 이 지표들(수신 간격 분산 급증, 하트비트 유실, 예상치 못한 MISSION_COUNT)이 곧 탐지 신호.

### 4. 학습 포인트
- SITL = 실제 하드웨어 없이 오토파일럿 펌웨어를 소프트웨어로 돌리는 시뮬레이터. 우리 프로젝트와 결이 같음.
- 핵심 한 줄: 공격의 성공은 "언제 쏘느냐"(웨이포인트 전환 직전)와 결합될 때 극대화된다 → 우리 공격 에이전트의 타이밍 로직에 시사점.

---

## [RELATED WORK (Section V)]

### 1. 직독직해 (요지 문장 단위)

- English: One way to disable a UAV is to use a sensor and hardware attack on the UAV, or a network attack.
- Korean: UAV를 무력화하는 한 방법은 UAV에 대한 센서·하드웨어 공격, 또는 네트워크 공격을 사용하는 것이다.

- English: In general, communication link jamming and GPS spoofing are used for sensor attacks in UAV systems.
- Korean: 일반적으로, UAV 시스템의 센서 공격에는 통신 링크 재밍과 GPS 스푸핑이 사용된다.

- English: Jamming prevents the communication link between the UAV and the GCS or the controller from correct operation so that the control message of the UAV cannot be transmitted.
- Korean: 재밍은 UAV와 GCS 또는 컨트롤러 사이의 통신 링크가 올바르게 작동하지 못하게 하여 UAV의 제어 메시지가 전송되지 못하게 한다.

- English: A GPS spoofing attack is used to trick the UAV by broadcasting a fake GPS signal [9, 15].
- Korean: GPS 스푸핑 공격은 가짜 GPS 신호를 방송하여 UAV를 속이는 데 사용된다.

- English: These attacks either require special equipment or has a limited attack range, while our attack method can be made without any special equipment and distance constraints.
- Korean: 이런 공격들은 특수 장비를 요구하거나 공격 범위가 제한적인 반면, 우리 공격 방법은 특수 장비와 거리 제약 없이 수행할 수 있다.

- English: In [10], the authors ... use the vulnerability of wired equivalent privacy (WEP) ... disable the UAV by sending de-authentication packets to the UAV. This attack is only applied to UAVs that use Wi-Fi ... while our attack method can be applied to any UAV systems using the MAVLink protocol.
- Korean: [10]에서 저자들은 WEP 취약점을 이용해 de-authentication 패킷을 보내 UAV를 무력화한다. 이 공격은 와이파이를 쓰는 UAV에만 적용되는 반면, 우리 방법은 MAVLink를 쓰는 어떤 UAV에도 적용 가능하다.

- English: In [20], a method to hijack a UAV using the vulnerability of the MAVLink protocol is proposed. ... if the NetID is known, it is easy to hijack the UAV. ... Unlike this approach, our attack method does not require any additional information such as NetID.
- Korean: [20]에서는 MAVLink 취약점으로 UAV를 하이재킹하는 방법이 제안된다. NetID를 알면 쉽게 하이재킹된다. 이 방식과 달리, 우리 방법은 NetID 같은 추가 정보를 요구하지 않는다.

- English: In [22, 23], the authors hijack a UAV using the vulnerability of the AR drone ... (FTP port scanning / telnet port vulnerability).
- Korean: [22,23]에서는 AR 드론의 취약점(FTP 포트 스캐닝 / 텔넷 포트 취약점)으로 UAV를 하이재킹한다.

### 2. 핵심 개념
- 기존 공격 분류: 센서·하드웨어(재밍, GPS 스푸핑) vs 네트워크(WEP/deauth, MAVLink NetID 하이재킹, AR드론 포트).
- 이 논문의 차별점: 특수장비·거리제약·추가정보(NetID) 불필요 + MAVLink 쓰는 모든 드론에 범용.

### 3. 공격/방어 해석
- 우리 대회 확장 시나리오 후보가 여기 다 나열됨: 재밍, GPS 스푸핑, deauth, 하이재킹.
- 각 공격의 "제약"이 곧 방어의 실마리(장비 필요/범위 제한/특정 프로토콜 한정).

### 4. 학습 포인트
- de-authentication 패킷 = 와이파이 연결을 강제로 끊는 관리 프레임(인증 없이 전송 가능).
- 핵심 한 줄: 이 논문의 강점은 "범용성"(MAVLink만 쓰면 통함). 우리도 공격의 범용성을 강조하면 좋다.

---

## [CONCLUSIONS (Section VI)]

### 1. 직독직해

- English: In this paper, we have empirically studied the vulnerability of the MAVLink protocol.
- Korean: 본 논문에서, 우리는 MAVLink 프로토콜의 취약점을 실증적으로 연구하였다.

- English: By exploiting the unencrypted messages of the MAVLink protocol, we have devised an attack methodology to disable a UAV.
- Korean: MAVLink 프로토콜의 비암호화 메시지를 악용하여, 우리는 UAV를 무력화하는 공격 방법론을 고안하였다.

- English: In our experiments, first we have studied ICMP flooding scenario, in which we can confirm that the packet inter-reception time significantly fluctuates which can be fatal to the UAV.
- Korean: 실험에서, 먼저 ICMP 플러딩 시나리오를 연구했으며, 여기서 패킷 수신 간 시간이 크게 변동하여 UAV에 치명적일 수 있음을 확인하였다.

- English: We have further carried out packet injection experiments, in which we have exploited the vulnerability of the waypoint protocol to send malicious packets for deleting mission information of the UAV.
- Korean: 나아가 패킷 주입 실험을 수행했으며, 웨이포인트 프로토콜의 취약점을 악용해 UAV의 임무 정보를 삭제하는 악성 패킷을 전송하였다.

- English: Consequently, under the packet injection attack, the UAV on mission has stopped and hovered because of deleted mission information.
- Korean: 결과적으로, 패킷 주입 공격 하에서, 임무 수행 중인 UAV는 삭제된 임무 정보 때문에 멈추고 호버링하였다.

- English: In summary, we have found out the vulnerability of the MAVLink protocol and have verified them with empirical study.
- Korean: 요약하면, 우리는 MAVLink 프로토콜의 취약점을 발견하고 실증 연구로 검증하였다.

### 2. 핵심 개념
- 결론 2줄: (1) ICMP 플러딩 = 수신 간격 변동 → 치명적, (2) MISSION_COUNT 주입 = 임무 삭제 → 정지·호버링.

### 4. 학습 포인트
- 핵심 한 줄: 비암호화 MAVLink 하나로 두 가지 무력화(가용성 붕괴 + 임무 삭제)를 실제 드론과 SITL 양쪽에서 재현.

---

## 우리 프로젝트 적용 메모 (공격 시나리오 개선용)

1. MISSION_COUNT 주입형 공격 = 우리 `attack_agent.py`에 "임무 초기화(대기 유도)" 액션 추가 아이디어.
   CybORG에는 없지만, "장악 대신 임무 무력화로 가용성만 깎는" 조용한 공격으로 제안 가능(창의성 점수).
2. ICMP 플러딩 = 이미 `FloodBandwidth`로 대응됨. 논문의 "하트비트 3초 유실→페일세이프"가 근거 자료.
3. 타이밍: 논문은 "웨이포인트 전환 직전"에 주입 → 우리 공격 에이전트의 타이밍(전이 순간 타격) 로직 근거.
4. 방어측 탐지신호(우리 defense_agent 개선용): 수신 간격 분산 급증, 하트비트 유실, 비정상 MISSION_COUNT 수신.

출처: Y.-M. Kwon et al., "Empirical Analysis of MAVLink Protocol Vulnerability for UAVs," IEEE Access, 2018. DOI 10.1109/ACCESS.2018.2863237
