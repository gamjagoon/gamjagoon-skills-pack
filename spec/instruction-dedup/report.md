# GSP 지침의 보수적 중복 정리

현재 단계: 구현·검증·독립 개발 검토 완료. C1은 새로운 요청이며 과거 벤치마크의 PASS/후보를 재사용하지 않는다. 기존 원본의 반복 설명만 줄이고 필수 정책은 유지한다. PoC 불필요(기존 설치 경로로 확인 가능한 문서 리팩터링). 요청 범위의 PoR 완료.

## 목차

- [요청과 완료 기준](#요청과-완료-기준)
- [정리 범위와 기준 소유자](#정리-범위와-기준-소유자)
- [분량과 기준 상태](#분량과-기준-상태)
- [실제 검증](#실제-검증)
- [독립 개발 검토](#독립-개발-검토)

## 요청과 완료 기준

원문: “AGENTS.md 랑 skills 같은 파일에 중복된 내용이 있다면 보수적으로 줄여줘 그리고 gsp에서 사용하는 AGENTS.md 파일으 200줄 이내로 만들어줘”. 시작: 2026-11-04 Asia/Seoul. 사용자 지정 기한 없음. 새 서비스·유료 벤치마크·외부 설치·commit/push 없음.

| ID | 완료 기준 | 검증 |
| --- | --- | --- |
| ID-R1 | 동일한 필수 정책을 유지하면서 반복 상세를 기존 기준 문서로 통합한다. 새 항상 읽는 문서로 옮기지 않는다. | 원본/변경 diff, 아래 매핑, 독립 의미 검토 |
| ID-R2 | 저장소 AGENTS 및 fresh 설치 AGENTS/관리블록은 실제 200줄 이내다. 사용자 지침은 줄 수와 관계없이 보존한다. | 줄 수, fresh/upgrade/backup/reinstall 회귀 |
| ID-R3 | standalone 스킬의 단계별 진입 안내와 설치된 기준 링크가 작동한다. | frontmatter, 설치본 링크/anchor 및 배포 파일 확인 |
| ID-R4 | 기존 dirty/실험 자료를 보존하며 검증 한계를 명시한다. | 수신 baseline과 추가 delta 분리, 해시/검토 기록 |

C1 설계: 전역 라우팅/문서 계약은 AGENTS, 질문 절차는 gsp-grilling, 검토 상세는 reviewer TOML, 세션/변경/격리 상세는 기존 references가 소유한다. 단계 스킬은 고유 입력·출력·종료 조건을 유지한다. 기존 절차를 바꾸지 않는 한정 변경이므로 새 요구/설계/DAG 8단계를 재작성하지 않고 이 기록에서 수용 기준·설계 매핑·실행·독립 개발 검토를 연결한다. 코드/DAG 동작 변경이 없으며 일반 구현 계획을 새로 만들지 않는다. 사용자에게 결정받을 미해결 의도/정책은 발견되지 않았다.

## 정리 범위와 기준 소유자

삭제는 동일 정책의 중복 서술에 한정한다. 전체 문단을 새 reference로 재배치한 항목은 없다. 아래 기준 문서는 모두 기존 파일이며 수정하지 않았다.

| 원래 반복 내용 / 위치 | 남은 기준 위치와 읽기 조건 | 처리 및 보존 |
| --- | --- | --- |
| AGENTS 변경 절차 상세와 development의 change-management | [change-management](../../.agents/skills/gsp-development/references/change-management.md), 계약/테스트/통합 기준 변경 시 read and apply | 요약·직접 링크 유지; 이전 done/PASS, 안전 checkpoint, 새 검증 task, DAG v2/수용 binding은 기준 문서에 남음 |
| AGENTS 세션 필드 목록과 session-work 상세 | [session-work](../../.agents/skills/gsp-development/references/session-work.md), 파일 변경 시작/재개 전 read and apply | 반복 필드 목록 삭제; 공통 main checkout root, 자기 기록만 쓰기, 경계 확인, 비-lock/비통보, 사용자 기록 보존 유지 |
| AGENTS grilling rounds와 단계 SKILL의 질문 전달 반복 | [gsp-grilling](../../.agents/skills/gsp-grilling/SKILL.md), 각 해당 단계 read and apply | 단계별 질문 trigger는 유지; 실제 사용자/선행 질문/답변 재사용/의존 부분 보류는 기존 skill이 소유 |
| AGENTS 검토 상세와 세 단계 SKILL의 같은 native/fallback 설명 | [reviewer TOML](../../.codex/agents/gsp-reviewer.toml), review 요청 전 읽기; [AGENTS review](../../AGENTS.md#reviews-and-stage-transitions) | 기준/입력/증거/오류수정 상세는 기존 TOML, 전체4mode·read-only·native 미로딩 공개·독립 fallback·self-check 공개는 AGENTS에 유지 |
| AGENTS 병렬/최적화 전달 목록과 parallel-work 상세 | [parallel-work](../../.agents/skills/gsp-development/references/parallel-work.md), 병렬 배정/실험 전 read and apply | 기본 격리/소유권/후보와 통합 구분 유지; 세부 측정·baseline·통합 조건은 기존 reference |
| 네 단계 SKILL의 동일한 문서 언어/형식/경로/보존/handoff 문단 | [AGENTS 문서 계약](../../AGENTS.md#documents-for-human-review), 각 skill에서 read and follow | 반복 전역 규칙 삭제; 단계별 default 경로/기록 내용/범위/종료 조건 유지 |
| CodeGraph/brief/PoC·PoR/예산/8단계 표/정확 모델 ID | [AGENTS](../../AGENTS.md) 원래 위치 | 이 구간은 원문 그대로 보존. gsp-adopt/gsp-grilling 및 기존 references도 원문 보존 |

## 분량과 기준 상태

기준 HEAD: `b35639393dfad227c1e33157390068f5f9809b55`. 수신 당시 AGENTS.md/README.md/reviewer TOML dirty 및 experiments/, spec/prompt-bench/, spec/shuttle-bench/ 미추적 상태를 유지했다. source-only 설치 prefix는 byte 일치한다. 원본 snapshot/해시/추가 delta: `/home/minjae/ws/gamjagoon-skills-pack/.gsp-work/sessions/session-instruction-dedup-xy4e76oj`. 공유 기록은 [work.md](/home/minjae/ws/gamjagoon-skills-pack/.gsp-work/sessions/session-instruction-dedup-xy4e76oj/work.md).

| 지침 파일 | 실제 줄 수 전 → 후 | byte 전 → 후 |
| --- | --- | --- |
| `AGENTS.md` | 184 → 179 | 30,358 → 27,489 |
| `.agents/skills/gsp-requirements/SKILL.md` | 46 → 45 | 5,958 → 5,485 |
| `.agents/skills/gsp-architecture/SKILL.md` | 43 → 42 | 5,886 → 5,496 |
| `.agents/skills/gsp-tasks/SKILL.md` | 60 → 59 | 8,005 → 7,909 |
| `.agents/skills/gsp-development/SKILL.md` | 52 → 51 | 8,706 → 8,287 |
| 수정한 지침 5파일 합계 | 385 → 376 | 58,913 → 54,666 |

실제 감소: 4,247 B. 변경 없는 gsp-adopt/gsp-grilling을 포함한 AGENTS+6개 SKILL 합계는 525줄/78,930 B → 516줄/74,683 B. 관리블록/새 설치 AGENTS는 170 → 165줄, 29,343 → 26,474 B. 새 파일로 지침을 옮긴 byte는 0. 문서 증거와 테스트는 위 지침 합계에서 제외했다. 줄을 합쳐 제한을 맞추지 않았으며 AGENTS 최대 행 byte는 1,231 → 1,201이다. 정적 byte 감소로 성능·실제 모델 token·품질 개선을 주장하지 않는다.

## 실제 검증

| 확인 | 기대 / 관측 | 증거 / 상태 |
| --- | --- | --- |
| `python3 -B -m unittest discover -s tests -p test_install.py -v` | 8개 통과. fresh preview/install/repeat, managed conflict/backup/rollback/기존 파일 보존, 설치 DAG/선택 coordination 경로 확인 | 실제 로컬 설치 회귀 PASS, 8.687s |
| 200줄 회귀 및 201줄 사용자 prefix+footer fixture | source/managed/fresh ≤200. 기존 사용자 지침은 combined >200이어도 byte 보존; 기본 충돌 중단/overwrite preview/backup/reinstall 확인 | 새 하드계약 회귀 PASS |
| 현재 source로 별도 fresh preview→install 후 상대 Markdown 링크/anchor 순회 | AGENTS, 6개 SKILL, 기존 references의 62개 local 링크/anchor 존재. source prefix 일치, root179/installed165줄 | 정적·설치 확인 PASS; `/home/minjae/ws/gamjagoon-skills-pack/.gsp-work/sessions/session-instruction-dedup-xy4e76oj/install-links.json` |
| skill-creator `quick_validate.py` × 변경 skill4 | 기본 python3는 PyYAML 없음으로 실행 불가; 기존 격리 Python(`/tmp/gsp-prompt-bench-mb1iwcog/venv/bin/python`, PyYAML 6.0.3)으로 4개 모두 통과 | frontmatter/scaffold 정적 PASS |
| `git diff --check` | 오류 없음 | 정적 PASS |

검증용 fresh 설치본: `/tmp/gsp-dedup-final-installed-ei56b0ca/project/AGENTS.md`. installer allowlist에 모든 필요한 references가 이미 포함되어 있어 install.sh/README 변경은 불필요하다. recursive 링크 확인은 설치된 파일에서 수행했다. 전역/사용자 프로젝트 설정은 변경하지 않았다. 전체 DAG·notification 테스트/추가 LLM 벤치마크는 이 문서 중복 정리 범위에서 실행하지 않았다. 설치 smoke는 모델의 이후 행동이나 실행 성능을 증명하지 않는다.

## 독립 개발 검토

ID-F1(차단, ID-R1/R3): 요구사항 skill 새 Default가 `spec/requirements.md`로 잘못 복수화됨. native reviewer가 원본 단수 경로와 불일치를 발견했다. 수정: `gsp-requirements/SKILL.md` Default를 `spec/requirement.md`로 복원. 원래 조건 재확인: 새 fresh preview/install 후 설치된 skill의 단수 Default/복수 부재 확인, 62개 링크/anchor 재통과. frontmatter PASS 및 fresh install 회귀 표적 재실행 PASS(0.997s). verifier: 저자 및 native gsp-reviewer 독립 표적 재검토 PASS, 종결.

native `gsp-reviewer`(`/root/conservative_dedup/dedup_review`), mode=development, `gpt-6.1-sol` high 실제 실행: **PASS**, ID-R1–4. TOML 읽기만 한 확인과 구분한다. 원본 snapshots/baseline, 현재 5개 지침, tests diff, reviewer/grilling/change/session/isolation 기준, peer 기록과 이 보고서를 직접 읽었다. ID-F1 수정 이후 독립 원조건 재검증 및 아래 회귀를 완료했고 남은 결함/사용자 결정은 없었다.

| 독립 확인 | 관측 결과 | 증거 범위 |
| --- | --- | --- |
| 원본→현재 의미/소유자/필수 읽기 조건 | 삭제된 중복의 기존 소유자와 진입 경로 확인, 주요 7개 AGENTS 구간 byte 동일 | 정적 의미 검토 PASS |
| 격리 복사본 installer suite | 8/8 통과, 9.783s | 실제 로컬 설치 회귀 PASS |
| 별도 fresh preview/install 및 전체 `.agents` Markdown 상대 링크/anchor 순회 | source179/installed165줄, 67개 검사 오류0, 설치 requirements skill 해시 일치 | 정적·설치 PASS |
| 현재 source/reviewer/references/test/report 기준 안정성 | tested-state.json의 지침5개 해시 및 복사본 일치; 기존 README/reviewer 보존 해시 일치 | 상태 확인 PASS |
| `git diff --check` | 오류0 | 정적 PASS |

독립 검증 경로: `/tmp/gsp-dedup-review-pw_ix4_4`. reviewer는 원본/기록을 쓰지 않았다. 저자62개 링크 검사는 AGENTS+6개 SKILL+references, reviewer67개 검사는 설치된 `.agents`의 Markdown 전체를 순회한 별도 검사다. 필수 검증의 의미 보존/로컬 설치 범위에서 PASS이며 모델 행동·성능 향상을 증명하지 않는다. 리뷰 당시 보고서 SHA는 `8cb9f693…`; 이후 이 최종 판정/상태 기록만 저자가 갱신했다. 지침·테스트는 독립 검토 후 변경하지 않았다.
