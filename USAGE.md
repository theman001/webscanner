# 📖 WebScanner 사용 가이드

기본적인 설치부터 실행, 결과 확인까지 빠르게 따라 할 수 있는 가이드입니다. 기능 전체 설명은 [README.md](README.md)를 참고하세요.

---

## 1. 설치

```bash
git clone <repo-url>
cd webscanner
pip install -r requirements.txt
```

Python 3.9 이상 필요.

---

## 2. 대화형으로 실행하기 (처음 써볼 때)

```bash
python scanner.py
```

순서대로 물어봅니다:

1. **대상 URL** — `http://` 또는 `https://`로 시작해야 함
2. **OPTIONS** (쉼표로 다중 선택, 예: `1,2,4`)
   ```text
   1. Scan history diff        이전 스캔과 비교
   2. Save scan snapshot       history/에 결과 저장 (diff/trend의 전제조건)
   3. Configure scan performance   타임아웃/동시성 값을 직접 입력
   4. Long-term trend analysis 스냅샷 2개 이상 쌓인 뒤부터 의미 있음
   5. AI risk explanation      현재는 비활성 스텁
   6. FULL OPTIONS             전부 실행
   ```
3. **SCANS** (쉼표로 다중 선택, 예: `1,2,3`)
   ```text
   1. Web framework & version
   2. Subdomain scan
   3. Port scan
   4. Port → service inference   (3번 실행 결과가 있어야 값이 채워짐)
   5. TLS / certificate
   6. Security headers
   7. Technology stack summary
   8. FULL SCAN                  전부 실행
   ```
4. OPTIONS에서 **3**을 골랐다면 성능 값을 물어봅니다. Enter만 누르면 기본값 유지:
   ```text
   dns_timeout [1.0]:
   port_timeout [1.0]:
   http_timeout [5.0]:
   concurrency [50]:
   ```

**처음 실행할 때 권장 조합**: OPTIONS `2` (저장), SCANS `8` (FULL SCAN) — 이렇게 몇 번 돌려서 history를 쌓아두면 이후 diff/trend가 의미를 가짐.

---

## 3. 자동화(비대화형)로 실행하기

cron이나 스크립트에서 쓸 때는 URL과 `--options`/`--scans`를 인자로 바로 넘깁니다. 대화형 프롬프트는 전혀 뜨지 않습니다.

```bash
python scanner.py https://target.example --options FULL --scans FULL
```

번호를 직접 지정할 수도 있습니다 (메뉴 번호와 동일):

```bash
python scanner.py https://target.example --options 1,2,4 --scans 2,3,5,6
```

성능 값도 인자로 오버라이드 가능 (안 주면 기본값 사용, 프롬프트는 뜨지 않음):

```bash
python scanner.py https://target.example \
  --options FULL --scans FULL \
  --dns-timeout 0.5 --port-timeout 0.5 --http-timeout 5 --concurrency 100
```

cron 등록 예시 (매일 03:00):
```cron
0 3 * * * cd /path/to/webscanner && /usr/bin/python3 scanner.py https://target.example --options FULL --scans FULL >> /var/log/webscanner.log 2>&1
```

> `--options`/`--scans` 없이 URL만 주면 에러로 종료합니다 — 자동화 모드에서는 두 값이 필수입니다.

---

## 4. 결과 확인하기

실행이 끝나면 `report/`, `history/`에 파일이 쌓입니다 (스크립트 실행 위치와 무관하게 항상 프로젝트 루트 기준).

`report/`는 **대상 호스트별 → 버전별**로 나뉩니다. 스캔할 때마다 새 `v<N>` 폴더가 생기고 이전 결과는 그대로 남습니다:
```text
report/
└── example.com/
    ├── v1/  result.json, diff_summary.md, trend_report.md, ...
    └── v2/  result.json, diff_summary.md, trend_report.md, ...
```

| 경로 | 내용 |
|------|------|
| `report/<host>/v<N>/result.json` | 해당 회차 스캔의 전체 결과 (metadata, timing, 스캔별 결과, diff/trend/ai) |
| `report/<host>/v<N>/diff_summary.md` | 이전 스캔과의 변경점 (OPTIONS `1` 선택 시) |
| `report/<host>/v<N>/trend_report.md` | 안정성 점수·위험 등급 (OPTIONS `4` 선택 시, 스냅샷 2개 이상 필요) |
| `report/<host>/v<N>/ports_trend.png`, `subdomains_trend.png` | 시간에 따른 포트/서브도메인 개수 그래프 |
| `history/<host>/scan_*.json` | OPTIONS `2` 선택 시 저장되는 스냅샷 (diff/trend의 원본 데이터, 대상 호스트별로 격리) |

`history/`도 `report/`처럼 대상 호스트별 폴더로 나뉩니다. 서로 다른 대상을 번갈아 스캔해도 diff/trend는 항상 같은 호스트의 이전 스냅샷하고만 비교됩니다.

위험 등급 기준(`stability_score`):

| 점수 | 등급 |
|------|------|
| ≥ 0.85 | 🟢 LOW |
| 0.70 ~ 0.84 | 🟡 MEDIUM |
| 0.50 ~ 0.69 | 🟠 HIGH |
| < 0.50 | 🔴 CRITICAL |

---

## 5. 자주 하는 실수

- **diff/trend가 안 나옴** → OPTIONS `2`(저장)를 최소 2번 실행해서 `history/`에 스냅샷을 쌓아야 함
- **포트 스캔인데 서비스 추론 결과가 비어있음** → SCANS `4`(서비스 추론)는 `3`(포트 스캔) 결과가 있어야 채워짐 — 같이 선택
- **`--options`/`--scans`에 `FULL` 대신 숫자로 다 나열해도 됨**, 대소문자는 `FULL`/`full` 둘 다 허용
- 이 도구는 **정찰(recon) 전용**입니다 — 자신이 소유했거나 명시적으로 허가받은 대상에만 사용하세요

---

## 6. 테스트

```bash
python tests/test_utils.py
python tests/test_history.py
```
