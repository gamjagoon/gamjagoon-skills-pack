# Task DAG 검증·라우팅 설계

- 단계: 독립 architecture 리뷰 PASS. Task 계획으로 인계.
- 근거: [요구사항 R1–R7](requirement.md), requirements 리뷰 PASS.
- 선택: Markdown 안의 단일 JSON DAG와 Python 표준라이브러리 CLI. 자동 agent 실행 없음.
- 미해결 결정·차단: 없음.

## 목차

- [구조와 책임](#구조와-책임)
- [DAG 계약](#dag-계약)
- [검증과 충돌 규칙](#검증과-충돌-규칙)
- [배정 알고리즘](#배정-알고리즘)
- [CLI 계약과 통합](#cli-계약과-통합)
- [검증 전략과 설계 리뷰](#검증-전략과-설계-리뷰)

## 구조와 책임

| 구성 | 책임 | 요구사항 |
| --- | --- | --- |
| `gsp-tasks/references/task-dag.md` | 입력 형식·예제·CLI·제약 문서 | R1–R5 |
| `gsp-tasks/scripts/task_dag.py` | 입력 파싱·구조 검증·위상 정렬·후속 배정·Mermaid 출력 | R1–R5 |
| tasks/development/adopt/reviewer 지침 | 생성·변경 시 검증, 현재 실행 상태 기록, 결과 재확인 후 agent 배정 | R6 |
| installer와 tests | 두 새 자원 설치 및 실제 경로·회귀 확인 | R6–R7 |

스크립트는 입력을 읽고 stdout에 결과를 쓴다. 네트워크·shell·agent 호출이나 입력 수정·파일 잠금 기능은 없다. lead가 `.gsp-work`·소스 기준선·실제 가용 자원을 확인하고 실행 권한을 유지한다. 별도 DAG 서비스나 solver를 추가하지 않는다.

JSON 파일을 별도 정본으로 두면 Markdown과 상태가 어긋날 수 있으므로 작업 문서 안에 넣는다. YAML 라이브러리나 최적화 패키지는 설치 부담을 늘리므로 사용하지 않는다. 전역 최적해 대신 재현 가능한 긴 잔여 경로 우선 탐욕 배정을 사용한다.

## DAG 계약

작업 문서에 독립된 줄의 `<!-- GSP-DAG:START -->`와 `<!-- GSP-DAG:END -->`가 각각 한 번 있어야 한다. 그 사이에는 단일 `json` fenced block만 둔다. DAG의 상태·선행 ID·라우팅 소유권은 이 블록이 정본이며 Markdown 상세 설명은 안정적인 Task ID로 연결한다. 출력한 Mermaid는 이 블록에서 파생한 표시다.

루트 객체 필수 키는 `version: 1`, 양의 정수 `max_parallel`, 비어 있지 않은 `tasks` 배열이다. 다른 키는 거절한다. `max_parallel`은 실제 가용 agent와 자원에 맞게 명시하며 CLI에 임의 기본값을 두지 않는다.

각 Task의 필수 키:

| 키 | 형식 |
| --- | --- |
| `id` | `[A-Za-z][A-Za-z0-9_.-]*` 형태의 고유 ID, 기존 ID 유지 |
| `title` | 공백만으로 이루어지지 않은 문자열 |
| `deps` | 선행 ID 문자열 배열, 중복 없음 |
| `status` | `pending`, `running`, `done`, `blocked` 중 하나 |
| `owner` | 담당 worker 식별 문자열 또는 `null`; 역할·모델명이 아니라 동일 담당자의 동시 배정을 막는 ID |
| `reads`, `writes` | 프로젝트 기준 정규화된 상대 POSIX 경로 배열, 각각 중복 없음 |
| `resources` | 독점 자원 식별 문자열 배열, 중복 없음. 예: `port:8080`, `gpu:0` |

선택 키는 `estimate_minutes`와 `estimate_basis`(항상 함께 제공), `evidence`, `reason`이다. 추정은 bool이 아닌 유한 양수, 근거는 비어 있지 않은 문자열이어야 한다. `done`은 `evidence`, `blocked`는 `reason`이 반드시 필요하다. 제공한 선택 문자열도 비어 있으면 오류다. `running`은 null이 아닌 owner가 필요하다. `pending`의 null owner는 계획 단계에서 허용하지만 배정하지 않고 사유를 표시한다. 완료 증거의 내용 진위는 사람의 검토 범위다.

## 검증과 충돌 규칙

1. JSON 문법·중복 객체 키·NaN/Infinity를 거절한다. 버전·필드·타입은 엄격히 검사하며 bool을 정수/숫자로 받아들이지 않는다.
2. 중복/자기/존재하지 않는 의존성과 순환을 검사한다. 위상 정렬은 ID 오름차순으로 동률을 해결한다.
3. `running` 또는 `done`인 작업의 모든 직접 선행 작업은 `done`이어야 한다. running 수가 병렬 한도를 초과하거나 running 간 충돌이 있으면 입력을 거절한다.
4. 경로는 `.`(프로젝트 전체) 또는 정규화된 상대 POSIX 경로다. 절대 경로, `..`, 중복 구분자, 끝 `/`, `./`, 역슬래시, glob을 거절한다. 경로가 아직 존재할 필요는 없다.
5. 같은 경로 또는 부모/자식 범위는 겹친다. read/read는 허용하고 write/write와 write/read는 충돌한다. 예: `src`와 `src/a.py`는 겹치지만 `src/a`와 `src/ab`는 다르다.
6. 같은 owner 또는 공유 독점 resource도 충돌한다. 같은 작업 내부의 read/write 중첩은 허용한다.

경로 검사는 선언된 범위의 문자열 비교다. symlink/hardlink·대소문자 별칭, 미신고 파일과 서비스 충돌을 완전히 탐지하지 않는다. 주 작업자가 실제 별칭을 정규화하거나 공통 resource ID로 묶는다. 선언된 제약의 유효성 검사를 실행 중인 시스템의 lock으로 오해하지 않는다.

## 배정 알고리즘

- 위상 순서를 역순으로 순회해 `score(task) = weight(task) + max(score(미완료 후속 작업))`을 계산한다. done의 score는 0이다.
- 모든 미완료 작업에 시간과 근거가 있으면 weight는 `estimate_minutes`, `priority_basis`는 `estimated_minutes`다. 하나라도 없으면 전체를 weight=1로 계산하고 `dependency_steps`라고 표시한다. 부분 시간 추정을 임의 보완하지 않는다.
- pending이며 모든 deps가 done인 작업만 `ready` 후보로 취급한다. 후보는 score 내림차순, ID 오름차순으로 정렬한다.
- running 작업이 이미 차지한 슬롯·owner·경로·resource를 예약한 상태에서, 남은 슬롯 안에서 충돌 없는 후보를 차례로 선택한다. owner 미지정은 선택하지 않는다.
- 선택하지 않은 작업은 선행 미완료, blocked reason, owner 미지정, capacity, 충돌 상대와 이유 등을 출력한다. done은 대기 목록에 넣지 않는다.
- 작업 하나가 완료되면 lead가 해당 상태와 증거를 갱신하고 재실행한다. 같은 단계의 모든 작업 완료를 기다리는 배치 장벽을 두지 않는다. 실패/차단은 blocked로 기록하고 독립 작업은 계속 배정할 수 있다.

라우팅은 선언된 현재 상태 기준의 휴리스틱이다. 오래된 출력으로 배정하지 않으며 실제 spawn 이전에 상태·소유권을 다시 확인한다. 실행시간, 예상 총완료 시간 또는 속도 개선을 자동 주장하지 않는다.

## CLI 계약과 통합

```bash
python3 .agents/skills/gsp-tasks/scripts/task_dag.py validate spec/tasks.md
python3 .agents/skills/gsp-tasks/scripts/task_dag.py route spec/tasks.md
python3 .agents/skills/gsp-tasks/scripts/task_dag.py render spec/tasks.md
```

- `validate`: `valid`, `topological_order`, `edges`, `warnings`를 JSON으로 출력.
- `route`: 위 검증 정보에 `priority_basis`, `priorities`, `running`, `ready`, `dispatch`, `waiting` 추가. `dispatch` 원소는 `task`, `owner`, `score`; `waiting`은 Task ID → 사유 목록.
- `render`: 유효한 입력만 ID/상태와 의존 화살표를 가진 Mermaid fenced block으로 출력. 내부 node 이름을 생성하여 원래 ID를 Mermaid 문법으로 해석하지 않는다.
- 성공 exit 0. 읽기/문법/스키마/의존/상태 오류는 `valid:false`, `errors` JSON과 exit 2; 유효한 dispatch를 섞지 않는다. CLI 사용 오류는 argparse의 표준 exit 2.

새 스크립트·참조 문서 두 파일을 installer 명시 목록에 추가한다. 기존 6스킬 11파일은 총13파일이 된다. 설치는 Python/CodeGraph를 실행하거나 대상 프로젝트 DAG를 만들지 않는다. 실행 시 Python 3.9+를 사용하며 외부 패키지는 필요 없다.

Tasks 작성/수정과 stage handoff에서 validate를 실제 실행한다. development는 dispatch 제안 후 실제 상태를 기록하며 재계산한다. adopt는 준비된 Task 기준에 DAG를 포함하되 구현을 실행하지 않는다. reviewer는 구조 검사 결과와 실제 설계/소스 의미를 따로 확인한다. 단순 질의나 task가 없는 설치만으로 DAG를 만들지 않는다.

## 검증 전략과 설계 리뷰

R1–R3/R5: 파서·스키마 오류와 그래프 경계, 상태·경로·owner/resource 충돌을 unittest 및 실제 CLI로 검증한다. R4: 완전/부분 추정과 결정성, running 슬롯, 독립 작업·후속 작업의 즉시 배정, 합성 일정 비교를 검증한다. R6–R7: 설치 fixture의 정확한 13개 파일과 설치된 경로의 실제 validate/route 실행, 기존 보존·백업·rollback을 확인한다.

native gsp-reviewer, mode architecture, Sol medium: **PASS**. R1–R7에 대한 형식·배정·오류·설치 인터페이스를 확인했으며 결함·미결정 없음. 검토 설계 SHA256 `9002cd2493fa138368aff7a270d74a9f01197f139c03de1027d68ddaf7e855e1`과 관련 7개 파일의 해시 보존을 확인했다. Lead는 결과를 수용한다. 정적 설계 리뷰이며 구현·CLI·설치·성능은 아직 검증하지 않았다.
