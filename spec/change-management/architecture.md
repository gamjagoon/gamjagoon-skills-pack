# 변경 대응과 VM 세션 조정 설계

- 단계: 독립 설계 리뷰 및 CM-A1/CM-A2 재검토 완료. 구현·최종 검증은 [Task 문서](tasks.md)에 기록했다.
- 범위: [R1–R9](requirement.md#확정-구현-계약), 합의된 Q1–Q6. 기존 [대안 조사](architecture-options.md)는 이력으로 보존한다.
- 결과: Markdown 정본 + 선택형 DAG v2 + 로컬 세션 조정 도구. 추가 패키지·서비스 설치와 자동 모델 시작 없음.

## 목차

- [구성과 책임](#구성과-책임)
- [변경 처리와 DAG v2](#변경-처리와-dag-v2)
- [세션 조정 계약](#세션-조정-계약)
- [연결과 장애](#연결과-장애)
- [검증과 소유권](#검증과-소유권)
- [설계 리뷰](#설계-리뷰)

## 구성과 책임

| 구성 | 책임 | 요구 |
| --- | --- | --- |
| development/references/change-management.md | 모든 단계에서 변경 포착→영향→기준 수정→새 작업→검증→종결. 스킬은 필요한 부분만 연결 | R1–R4 |
| tasks/scripts/task_dag.py + task-dag.md | 기존 v1 보존, 명시적 v2 계약 개정·작업 기준·현재 수용·hold 검사, 안전한 배정 | R2–R5 |
| development/scripts/session_control.py | 사용자 권한 로컬 상태 기록·등록·게시·ACK·감시·상태/통합 확인 | R4,R6–R8 |
| development/references/session-control.md | 무설치 실행 조건, 실제 명령, A/B 전환, 실패·복구 절차 | R6–R8 |
| AGENTS, 6개 skills, reviewer, README, installer | 공통 계약·검토·설치·사용 진입점 | R1,R9 |

정본은 기존 세 Markdown 문서다. `.gsp-work/control`은 운영 이벤트·전달·ACK 기록만 보관하며 요구/설계/Task 정본을 대신하지 않는다. 기존 세션별 work.md는 각 소유자만 쓴다. B가 다른 작업자의 소스·세션 기록을 수정하지 않는다.

## 변경 처리와 DAG v2

최초 영향 단계에 C ID, 근거, 이전/새 계약 개정, 영향·미확인 범위, 담당, 종결 증거를 기록한다. 이전 done/PASS와 실행 기준은 보존하고 수정·재검증을 새 Task로 추가한다. 영향을 받는 pending 소비자·최종 수용 연결도 새 작업으로 갱신한다. 의미 불변 문서 수정은 개정을 올릴 필요가 없다.

v1의 입력·출력은 유지한다. v2는 기존 필드에 아래를 추가하며 알 수 없는 필드·잘못된 타입을 거부한다.

| 필드 | 계약 |
| --- | --- |
| root `version: 2`, `plan_revision` | 양의 정수 계획 개정. 기준/의존성/hold/수용 연결 변경 시 증가. 단순 진행/증거 갱신은 기존 개정 유지 가능 |
| root `contracts` | 계약 ID→현재 양의 정수 개정. 요구/설계/인터페이스 ID 사용, 적어도 하나 |
| task `basis` | 실행이 따른 계약 ID→개정. 등록 계약만 참조, 미래 개정 거부. 빈 객체는 계약 무관 관리 작업에만 사용하며 Markdown에 이유 기록 |
| task optional `hold` | 의미 영향·갱신 중·ACK 미확인 등에 대한 비어 있지 않은 사유. 과거 실행 상태와 독립적으로 배정/현재 수용 제한 |
| task optional `revalidates` | 직접 deps 중 과거 done 실행 ID. 현재 기준으로 재검증하는 명시적 경계. 그 직접 의존 경로로 유입된 과거 실행과 조상의 stale을 입력으로 허용하되, 모든 hold와 자신/다른 비재검증 경로의 stale은 면제하지 않음 |
| root `acceptance` | 비어 있지 않은 `{id, contracts, tasks}` 목록. contracts는 등록된 계약의 양의 개정으로 이루어진 비어 있지 않은 부분집합. 미래 개정은 오류, 과거 개정은 현재 수용 미충족으로 표시하되 독립 작업 배정을 막는 구조 오류로 삼지 않음. check의 완료 조건은 현재 개정과 정확히 일치하는 것. tasks는 이 수용 조건을 입증할 비어 있지 않은 고유 Task ID 목록 |

개정이 오래된 done/running은 역사적 사실로 유효한 JSON이다. 검증기는 삭제하거나 pending으로 바꾸지 않는다. stale/hold 작업과 그 실행 의존 소비자는 현재 사용할 수 없다고 표시한다. revalidates 경계는 과거 합성 산출물의 전체 역사적 stale 경로를 입력으로 받을 수 있게 하지만 과거 결과를 직접 현재 수용으로 바꾸지 않는다. 원인은 경로별 필터 후 병합해 같은 조상이 다른 비재검증 경로로 들어오면 그 stale을 유지한다. hold는 재검증 경계로 우회할 수 없다.

`route`는 현재 사용할 수 없는 pending 작업을 제외하고, 영향받은 running은 `pause_required`로 보고한다. running 예약은 실제 보류 전까지 유지한다. 보류가 확인되면 원래 실행은 `blocked`+reason으로 보존하고 새 실행을 추가한다. 새 요청은 기존 우선순위 알고리즘에 들어가며 진행 중 작업을 빼앗지 않는다.

`check`는 현재 수용 조건의 참조가 현재 계약과 일치하고, 각 증거 Task가 done·현재 유효하며, 수용의 계약 개정이 해당 증거 Task의 basis에 포함되는지 확인한다. `complete`는 모든 필수 수용 조건 충족 여부다. 구조 오류는 exit 2, 구조 유효하지만 현재 미충족은 exit 1, 충족은 0. v1 check는 개정 검증을 제공하지 않는다고 표시하고 실행 완료만 별도 보고한다. `route`의 빈 dispatch는 완료가 아니다. 순수 함수 `parse_document(text)`, `validate(data)`, `route(data)`, 새 `check(data)`를 외부 도구에서 재사용한다.

## 세션 조정 계약

Python 3.9+ 표준 라이브러리만 사용한다. 각 실행에 절대 `--work-root <main>/.gsp-work`를 지정한다. CLI의 정본 문서 경로도 명시한다. 실제 명령 이름/필드는 아래 계약을 따른다.

| 명령 | 동작 |
| --- | --- |
| `doctor --socket PATH` | 같은 계정의 기존 Unix socket 확인과 initialize 핸드셰이크. 설치/서버 시작/세션 시작 없음. B 가능 여부 또는 A 사유 출력 |
| `register --session ID --thread ID --tasks T... --document PATH` | 기존 sessions/ID/work.md와 v2 Task 소유 관계를 확인하고 opt-in 등록. thread당 중복 등록/조용한 재바인딩 거부. 같은 thread/cwd/문서의 Task superset 추가만 명시적으로 허용. task.owner는 세션 ID와 일치해야 하며 linked worktree는 --cwd로 지정. 사용자 세션 목록 자동 수집 없음 |
| `publish --change ID --expected-revision N --tasks T... --reason TEXT --document PATH` | v2의 현재 revision과 대상 작업 존재·stale/hold 조건 확인 후 변경 게시. 동일 ID/내용은 멱등, 다른 내용 재사용은 거부. 겹치는 등록 세션에만 전달 대상 생성. 미등록 영향 Task는 미배정/미확인으로 노출 |
| `ack --session ID --change ID --revision N --state read|held|applied --evidence TEXT` | 정확한 변경/개정/대상 세션에 업무 확인. read→held→applied 단조 전이, held로 직접 확인 가능, applied는 held 이후만 허용. 변경마다 근거 보존. 승인된 새 요청을 임의 생성하지 않음 |
| `run --socket PATH --document PATH --once` | 기존 socket에 연결하고 등록 thread만 조회, active turn에만 steer. idle은 deferred로 기록하고 자동 turn 시작/재개 없음. --once 없으면 사용자가 유지하는 전경 감시 프로세스 |
| `status` | 미전달/불확실/읽음/보류/적용 상태, 재시도 횟수, A 사유, 미등록 대상 표시. 이 상태만으로 현재 수용 완료를 선언하지 않음 |
| `check --document PATH` | v2 현재 수용 검사와 모든 unresolved 이벤트를 함께 확인. 종결하려면 관련 대상 전부 applied, 미등록 대상 없음, 현재 plan_revision >= 이벤트 개정 및 저장된 영향 계약의 현재 값 일치가 필요. resolve와 같은 기준을 사용하며 ACK 없이 오래된 이벤트를 성공 처리하지 않음 |
| `resolve --change ID --expected-revision N --document PATH --evidence TEXT` | lead가 명시한 현재 expected-revision, 현재 수용 검사와 대상 applied ACK 근거를 확인한 뒤 종결. 현재 plan_revision은 이벤트 이상이어야 하고 게시 시 영향 Task의 basis가 참조한 계약의 현재 개정이 같아야 함. hold 해제/무관한 계획 갱신은 종결을 막지 않음. 영향 계약이 바뀌면 새 이벤트 ID와 기존 이벤트의 명시적 대체 관계/근거로 연결하는 `supersede` 경로 필요 |

`supersede --change OLD --by NEW --evidence TEXT`는 NEW가 현재 계획 기준으로 게시됐고 OLD의 대상 Task/세션을 포함하는지 검사한다. 이전 이력은 보존하고 check는 최신 미해결 이벤트를 추적한다. 이전 read/held/applied는 새 이벤트 ACK로 복사하지 않는다. 게시 시 대상 Task의 basis 키 집합과 그 키들의 현재 계약 개정을 저장하며, 기준 비교는 무관한 계약까지 전역 무효화하지 않는다. ACK는 원래 이벤트 ID·개정에만 속한다. 이전 이벤트 resolve는 별도의 최신 미해결 이벤트를 닫지 않는다.

예: 계약 R1@2는 유지한 채 plan r5에서 T1에 hold를 걸고 C1을 게시한다. 작업자가 C1/r5에 held·applied를 남긴 뒤 lead가 hold를 해제해 plan r6으로 올린다. C1은 게시 당시 `contracts[R1]=2`(과거 T1.basis의 값이 아님)를 저장했으므로 현재 수용 검사가 충족되면 expected-revision=6으로 resolve할 수 있다. ACK 개정은 여전히 C1/r5다. 별도로 C2가 게시됐다면 C1 종결과 무관하게 C2 ACK/종결을 확인하기 전 전체 check는 미완료다.

공유 운영 파일은 하나의 `state.json`으로 작게 유지하며 `fcntl.flock` + 임시 파일/fsync/원자적 rename으로 명령 간 갱신을 직렬화한다. 원본 손상은 실패하며 빈 상태로 재생성하지 않는다. 네트워크를 기다리면서 상태 잠금을 오래 잡지 않는다. 감시 프로세스는 별도 비차단 lock으로 프로젝트당 하나만 허용한다. 경로·파일 소유자·심볼릭 링크를 확인해 자기 계정의 지정된 루트 안에서만 쓴다. 악성 동일 계정의 프로세스를 막는 보안 경계는 아니다.

변경 메시지는 C ID·정확한 개정·대상 Task·문서/공유 루트·ACK 명령을 포함한다. 작업자에게 안전 지점 결과 보존과 ACK를 요구하지만 지시 준수를 기술적으로 보장하지 않는다. 내용은 프로젝트 데이터이며 새로운 상위 권한이나 임의 shell 실행으로 해석하지 않는다. shell 문자열로 명령을 실행하지 않는다.

## 연결과 장애

설치된 Codex 0.166.0의 Unix socket은 WebSocket이다. Python 표준 라이브러리의 AF_UNIX+HTTP Upgrade+마스킹된 text frame로 격리 initialize 성공. 기존 proxy에 JSONL을 넣는 경로는 두 소켓에서 응답하지 않았으므로 사용하지 않는다. 최소 WebSocket 클라이언트는 handshake digest, 프레임 크기 상한, ping/pong/close, fragment 조합, 응답 ID·타임아웃을 처리한다. 지원 범위는 로컬 Unix socket만이며 외부 TCP나 인증 토큰을 다루지 않는다.

등록 thread의 `thread/read`(turns 포함)로 현재 상태를 읽고 active turn ID에 `turn/steer`+expectedTurnId를 사용한다. active 여부를 확정하지 못하면 전송하지 않는다. thread/start, turn/start, thread/resume, interrupt, daemon 설치/시작을 호출하지 않는다. 직접 읽기가 로드되지 않은 thread를 발견해도 깨우지 않는다. 필요한 정확한 프로토콜은 설치 버전 스키마로 확인하고 모르면 A로 남긴다.

전송 전에 `sending`과 시도 횟수를 저장한다. 연결/초기 조회에서 확실히 실패하면 제한된 횟수(설정 가능, 유한 기본값)만 재시도한다. steer를 보낸 뒤 응답이 유실되면 `uncertain`으로 남기고 자동 재송신하지 않는다. 재시작 시 남은 sending도 uncertain 처리한다. 이는 중복 모델 입력을 피하는 보수적 정책이며 exactly-once 보장이 아니다. worker는 변경 ID/개정으로 중복 처리하지 않고 상태를 확인한다. delivered도 업무 ACK가 아니다.

조정 프로세스/VM 종료, 버전 부족, 접근 거부, socket 부재 시 A의 작업 경계 확인으로 돌아간다. 기존 미해결 상태를 지우거나 held/applied로 만들지 않는다. 사용자가 read/held/applied를 자신의 기록과 도구에 남길 수 있으므로 자동 전송이 없어도 수동 절차가 이어진다.

## 검증과 소유권

| 검사 | 증거와 한계 |
| --- | --- |
| 과거 done + 새 계약 + 후속 재검증 | v1 회귀 및 v2 CLI: stale 소비자 제외, 독립 배정, revalidates, hold 우회 거부, 현재 수용 갱신 |
| 실제 CLI 명령으로 등록→게시→ACK→check/resolve | 임시 프로젝트와 운영 상태. stale revision·중복·미등록·잘못된 ACK·손상·동시 명령·재시작 포함 |
| scripted Unix WebSocket 서버 | 실제 stdlib 소켓·프레이밍·전송, active/idle·응답 유실·재접속. 모델/실제 Codex worker 증거가 아님 |
| 격리 실제 Codex app-server | initialize와 모델 없는 thread 메타데이터 경로. 실제 사용자 daemon/모델 worker 행동은 NOT_RUN |
| 설치 및 설치된 CLI | 관리 파일만 설치, noise 제외, 기존 충돌/backup/rollback. 설치가 프로세스를 실행하지 않음 |
| 독립 skill 시나리오 리뷰 | 요구 변경·테스트 실패·독립 새 작업에서 단계 되감기와 근거 기록 확인 |

실험 비용 경계는 요구 문서에 따른다. 원래 VM이나 실제 모델 작업을 검증했다고 주장하지 않는다. PoR 전달은 pack 구현/문서/로컬 검증 범위이며 대상 VM 배포 완료와 구분한다.

독립 소유: DAG worker는 task_dag.py와 해당 테스트/참조, coordinator worker는 새 session_control.py와 해당 테스트/참조, lead는 공통 참조·기존 지침·설치·문서·통합. 모두 격리 후보 디렉터리에서 쓰고 같은 main .gsp-work에 자기 기록만 남긴다. lead만 원본에 통합한다.

## 설계 리뷰

- 방법/판정: native gsp-reviewer mode architecture, 독립 읽기 전용, PASS.
- CM-A1 (R3/R4/R8): hold 해제 시 plan 개정이 올라 이벤트 종결이 불가능하던 조건을 수정. 현재 plan>=event와 영향 계약 현재 값 비교, 원래 ID/개정 ACK 유지로 수정했다. r5→hold 해제 r6 재현 조건과 독립 C2 gate를 reviewer가 실제 문서에서 재검토해 종결했다.
- 검토 기준: HEAD `bd656b1eed3d7800b7162ce97ea4dec0e5081540`+dirty, 최종 검토 설계 SHA256 `ed40f118f7d7b68b2ac2e75ddb577e4cd198bba8ce2288398cc09dd581cd704b`. 기존 16개 소스 기준 유지.
- 한계: 설계 리뷰와 격리 연결 증거만. 구현/동시성/실제 모델 worker 성공 판정 아님. CM-A1은 구현 테스트에 포함한다.

- CM-A2 추가 설계 재검토: 과거 T1→T2 모두 stale인 합성 산출물을 T3가 명시적으로 재검증할 때 조상의 stale이 영구 차단하는 후보 문제를 독립 재현했다. 경로별 revalidates에서 stale 전체를 허용하되 hold/자신/다른 경로 stale을 유지하는 수정 설계 PASS. 사용자 정책 추가 없음. 후보 수정과 체인·조상 hold·이중 경로·현재 수용 테스트는 개발 단계 종결 조건이다.

- 구현 구체화: check/run은 명시한 정본 문서의 이벤트만 처리하고 다른 문서의 작업을 막거나 바꾸지 않는다. supersede는 같은 문서에서만 가능하다. 등록 core identity를 보존한 Task 추가는 허용하되 이전 이벤트의 등록 snapshot은 유지한다. 이 경계와 basis 키 집합 변경·입력 가능성 null·유한 시간 검사에 대한 회귀 테스트를 추가했다.
