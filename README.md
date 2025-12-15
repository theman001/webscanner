# 🛡️ WebScanner  
**사전 정보 수집용 웹 취약점 분석 프레임워크**

---

## 📌 개요 (Overview)

**WebScanner**는  
웹 취약점 분석을 수행하기 전, 대상 시스템의 **외부 노출 정보와 변화 추이**를
**안전하게 수집·분석**하기 위한 **사전 정보 수집 전용 스캐너**입니다.

> ❗ 이 도구는 **익스플로잇·공격 기능을 포함하지 않습니다.**  
> ❗ 정보 수집과 변화 분석, 보고서 생성을 목적으로 설계되었습니다.

---

## 🎯 주요 목적

- 웹 서비스의 **기술 스택 및 노출 면 식별**
- **시간 흐름에 따른 변화 추적**
- 취약점 분석 우선순위 판단을 위한 **위험도 지표 산출**
- 보안 점검 보고서용 **정형 데이터 및 시각 자료 생성**

---

## 🧩 주요 기능 요약

### 🔍 단일 스캔 기능
- 웹 프레임워크 및 버전 탐지
- 하위 도메인 탐색 (asyncio 병렬)
- 포트 스캔 (asyncio 병렬)
- 포트 기반 서비스 추론 (HTTP / HTTPS 등)
- TLS 인증서 정보 수집
- 보안 헤더 분석
- 기술 스택 요약

### 📊 분석 및 추적 기능
- 스캔 결과 diff (이전 스캔 대비)
- diff 요약 (사람이 읽기 쉬운 형태)
- 장기 스캔 변화 트렌드 분석
- 안정성 점수(`stability_score`) 및 위험 등급 산출
- 포트 / 서브도메인 변화 그래프 생성

### 🧠 AI 보조 기능 (비활성 기본값)
- 위험 등급에 대한 **자연어 설명 생성**
- ❗ 판단·점수 산출에는 관여하지 않음 (설명 전용)

---

## 📁 프로젝트 구조

```text
webscanner/
├── scanner.py              # 메인 실행 파일
├── core/                   # 기능별 모듈
├── data/                   # 지문/워드리스트
├── history/                # 스캔 이력(JSON)
├── report/                 # 결과 리포트 및 그래프
└── requirements.txt
```

---

## ⚙️ 설치 방법

### 1️⃣ Python 환경
- Python **3.9 이상** 권장

### 2️⃣ 의존성 설치
```bash
pip install -r requirements.txt
```

---

## 🚀 실행 방법

```bash
python scanner.py
```

---

## 🧭 실행 흐름 (중요)

WebScanner는 **실행 시 사용자에게 선택지를 제시**합니다.

### 1️⃣ 옵션 선택 (Options)

```text
[ OPTIONS ]
1. Scan history diff
2. Save scan snapshot
3. Record metadata
4. Configure scan performance
5. Long-term trend analysis
6. AI risk explanation
7. FULL OPTIONS
```

#### ✔ 다중 선택 가능
```text
예시: 1,2,5
```

#### ✔ FULL OPTIONS 선택 시
- 나머지 옵션은 자동 무시
- 전체 옵션 활성화

---

### 2️⃣ 스캔 항목 선택 (Scans)

```text
[ SCANS ]
1. Web framework & version
2. Subdomain scan
3. Port scan
4. Port → service inference
5. TLS / certificate
6. Security headers
7. Technology stack summary
8. FULL SCAN
```

#### ✔ 다중 선택 가능
```text
예시: 1,2,3
```

#### ✔ FULL SCAN 선택 시
- 모든 스캔 항목 실행

---

## ⚡ 성능 설정 (선택)

옵션 4번 선택 시:

```text
dns_timeout [1.0]
port_timeout [1.0]
http_timeout [5.0]
concurrency [50]
```

- Enter 입력 시 기본값 유지
- 네트워크 환경에 따라 조정 가능

---

## 📦 결과물 설명

### 📄 report/result.json
- 스캔 결과 전체
- 메타데이터 포함
- diff / trend / ai 설명 포함

### 📄 report/diff_summary.md
- 이전 스캔 대비 변경 요약
- Markdown / Notion 호환

### 📄 report/trend_report.md
- 장기 변화 분석 리포트
- 안정성 점수 및 위험 등급 포함

### 📊 그래프
- `ports_trend.png`
- `subdomains_trend.png`

---

## 📈 안정성 점수 & 위험 등급

| stability_score | 위험 등급 | 의미 |
|----------------|-----------|------|
| ≥ 0.85 | 🟢 LOW | 변화 거의 없음 |
| 0.70 ~ 0.84 | 🟡 MEDIUM | 간헐적 변화 |
| 0.50 ~ 0.69 | 🟠 HIGH | 변화 빈번 |
| < 0.50 | 🔴 CRITICAL | 매우 불안정 |

---

## 🧠 AI 위험 설명 기능

- 기본적으로 **비활성**
- 옵션 선택 시 결과를 바탕으로
  > “왜 위험한지”를 **자연어 문장으로 설명**
- 분석/판단 결과를 변경하지 않음

---

## 🔐 안전성 및 윤리 가이드

- ❌ 익스플로잇 없음
- ❌ 공격 트래픽 없음
- ✅ 합법적 정보 수집 전용
- ✅ 자신이 관리/허가된 대상만 사용 권장

---

## 🧪 사용 시 권장 시나리오

- 보안 점검 전 사전 조사
- 버그바운티 대상 자산 파악
- 자산 노출면 변화 추적
- 정기 보안 점검 자동화

---

## 🔜 향후 확장 포인트

- CI/CD 연동
- Slack / Email 알림
- 위험도 기반 자동 우선순위
- AI 설명 활성화

---

## 📎 라이선스 및 주의사항

본 도구는 **연구 및 합법적 보안 점검 목적**으로만 사용해야 합니다.  
무단 사용 시 발생하는 법적 책임은 사용자에게 있습니다.

---

## ✨ 마무리

WebScanner는  
**“한 번 스캔하고 끝나는 도구”가 아니라  
“시간 흐름 속에서 위험을 이해하는 도구”**를 목표로 합니다.

필요한 기능은 언제든 확장 가능합니다.
