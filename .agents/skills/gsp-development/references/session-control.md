# 같은 VM의 선택형 세션 조정

Python 3.9+ 표준 라이브러리와 `fcntl`을 제공하는 Linux에서 실행한다. 동일 사용자 소유의 **기존** Codex app-server Unix WebSocket에만 연결한다. 설치·sudo·패키지·daemon 시작은 필요하지 않다. 연결 조건이 부족하면 A의 시작/단계/통합 경계 확인을 계속한다. 설치 성공은 대상 VM이나 실제 모델 작업자의 보류 성공 증거가 아니다.

## 목차

- [사전 조건](#사전-조건)
- [등록과 게시](#등록과-게시)
- [확인과 종결](#확인과-종결)
- [전송과 장애 복구](#전송과-장애-복구)
- [저장과 검증 경계](#저장과-검증-경계)

## 사전 조건

정본은 요구·설계·Task Markdown이다. 문서 경로는 소유권·링크 검사를 거친 정규 절대 경로로 비교하므로 `//`·`/./` 표기로 미해결 변경 검사를 우회할 수 없다. 현재 존재하는 hardlink도 같은 파일로 비교한다. 저장된 비정규 경로는 오류로 남기며, 과거 경로가 사라진 뒤의 이동·이름 변경을 영구 파일 ID로 추적하지는 않는다. 정본 이동은 기존 기록과 함께 명시적으로 조정한다. [변경 처리](change-management.md), [세션 기록](session-work.md), [DAG v2](../../gsp-tasks/references/task-dag.md)를 함께 적용한다. `session_control.py`는 설치된 형제 `gsp-tasks/scripts/task_dag.py`의 `parse_document`, `validate`, `check`를 재사용한다. v1은 기존 DAG 도구로 계속 사용할 수 있지만 세션 조정은 명시적 v2만 받는다.

모든 명령에 **절대 main checkout의 `.gsp-work` 경로**를 `--work-root`로 전달한다. 공유 루트와 등록 세션의 `sessions/ID/work.md`는 이미 있어야 한다. 조정할 Task의 v2 `owner`는 실제 등록할 세션 ID와 같아야 한다. 도구는 과거 실행이나 소유자를 자동 수정하지 않는다. `--cwd` 기본값은 공유 루트의 부모다. 명시적인 linked worktree는 `register --cwd /absolute/worktree`로 등록한다. 정본은 그 cwd 또는 main 프로젝트 아래에 있어야 하며 조회한 thread의 cwd는 등록 cwd와 정확히 같아야 한다. 등록 thread/세션의 조용한 재바인딩은 거부하며 이벤트마다 등록 identity를 보존한다.

아래 변수는 사용자가 이미 알고 있는 실제 절대 경로로 지정한다. socket 검색이나 세션 자동 수집은 하지 않는다.

```bash
control=/absolute/project/.agents/skills/gsp-development/scripts/session_control.py
work_root=/absolute/main/.gsp-work
document=/absolute/project/spec/tasks.md
control_socket=/absolute/existing/codex.sock
# 기존 Codex가 제공한 신뢰할 수 있는 경로가 링크라면 실제 경로를 확인한다.
control_socket=$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve(strict=True))' "$control_socket")
python3 "$control" --work-root "$work_root" doctor --socket "$control_socket"
```

Codex 0.166.0의 격리 실험에서는 지정한 소켓 경로가 같은 사용자 소유의 다른 `/tmp` 소켓을 가리키는 링크였다. 도구는 링크 경로를 거부하므로 확인한 실제 경로를 전달한다. 서버 재시작 뒤에는 다시 확인한다. 링크 해석만으로 서버 신원이 증명되는 것은 아니며, 등록할 thread와 cwd는 전송 전에 별도로 확인한다. 실험에서는 `SO_PEERCRED`의 PID/UID가 직접 시작한 격리 서버와 일치함을 확인했다.

`doctor`는 socket 종류·소유자와 WebSocket initialize만 검사한다. thread/turn 생성·시작·resume·interrupt는 호출하지 않는다. 오류는 JSON `mode: A`와 이유, exit 2로 반환한다. 성공은 이 연결의 초기화 가능성만 뜻한다.

## 등록과 게시

```bash
python3 "$control" --work-root "$work_root" register \
  --session session-a --thread known-thread-id --tasks T1 \
  --document "$document"
python3 "$control" --work-root "$work_root" publish \
  --change C1 --expected-revision 5 --tasks T1 \
  --reason 'R1 변경: 안전 지점에서 결과를 보존하고 보류' --document "$document"
python3 "$control" --work-root "$work_root" status
```

`register`는 기존 세션 기록과 Task 소유 관계를 확인하는 opt-in이다. 동일 등록은 멱등이다. 같은 thread/cwd/문서를 유지하며 소유가 확인된 Task를 추가하는 명시적 superset 등록은 허용한다. 기존 Task 제거와 thread/cwd/문서 재바인딩은 거부한다. 과거 이벤트의 캡처된 등록은 바꾸지 않는다. thread당 하나의 등록만 가능하다. 영향 작업은 게시 시 존재하고 stale 또는 hold 상태여야 한다. 의미 영향은 lead가 판단해 정본에 선언한다. 도구가 의미를 추론하지 않는다.

`publish`는 현재 `plan_revision`을 정확히 확인한다. 동일 ID·내용·정본 해시는 멱등이며 다른 내용에 ID를 재사용하면 실패한다. 대상 Task별 basis 키 집합과 **그 키들에 해당하는 현재 contracts 값**을 저장한다. 과거 basis 값이나 무관한 모든 계약을 저장하지 않는다. 겹치는 등록 세션에만 전달 대상을 만들며 미등록 Task는 `unregistered`로 남는다. 이후 등록이 과거 이벤트에 자동 ACK나 대상을 만들어 주지는 않는다. 필요하면 전체 영향을 포함한 새 이벤트를 게시하고 명시적으로 대체한다.

## 확인과 종결

```bash
python3 "$control" --work-root "$work_root" ack \
  --session session-a --change C1 --revision 5 --state held \
  --evidence '보존한 결과 경로와 실제 보류 지점'
python3 "$control" --work-root "$work_root" ack \
  --session session-a --change C1 --revision 5 --state applied \
  --evidence '새 기준 반영과 해당 검증 결과'
python3 "$control" --work-root "$work_root" check --document "$document"
# lead가 정본의 hold를 해제하고 plan_revision을 6으로 갱신한 뒤:
python3 "$control" --work-root "$work_root" resolve \
  --change C1 --expected-revision 6 --document "$document" \
  --evidence '현재 수용 검사와 원래 이벤트 applied ACK 확인'
python3 "$control" --work-root "$work_root" check --document "$document"
```

ACK는 정확한 이벤트 ID·게시 개정·대상 세션에 속한다. `read → held → applied`는 단조 전이다. held 직접 확인은 가능하고 applied는 held 이후만 가능하다. 실제 근거가 있어야 ACK한다. 전달 성공은 read/held/applied가 아니다. 각 ACK 근거는 누적 보존한다.

`resolve`는 현재 개정을 정확히 지정하고, 현재 계획이 이벤트 이상이며 게시 시 캡처한 영향 계약의 **현재 값**과 해당 Task별 basis 키 집합이 유지되는지 검사한다. 현재 수용 PASS, 모든 대상 applied, 미등록 Task 없음도 필요하다. R1@2를 유지하며 r5의 hold를 해제해 r6으로 올렸다면 C1/r5 ACK로 r6에서 종결할 수 있다. 무관한 계획/계약 갱신은 이 계약 비교를 막지 않는다. 별도 C2는 자체 ACK/종결이 필요하다.

영향 계약이 다시 바뀌면 새 이벤트를 현재 정본으로 게시한다. 새 이벤트는 이전 Task와 세션을 모두 포함해야 한다. 과거 이력과 ACK는 보존하고 새 이벤트 ACK로 복사하지 않는다.

```bash
python3 "$control" --work-root "$work_root" supersede \
  --change C1 --by C2 --evidence 'R1 새 개정과 영향 전체를 C2로 승계'
```

`check`는 명시한 문서의 현재 수용과 그 문서의 모든 최신 미해결 이벤트를 함께 확인한다. 같은 공유 루트의 다른 문서 이벤트는 check/run에서 변경하거나 차단하지 않는다. supersede는 같은 정본 문서의 이벤트 사이에서만 허용한다. 종결 가능한 이벤트라도 lead의 명시적 resolve 전에는 unresolved다. 완료 exit 0, 유효하지만 미완료 exit 1, 입력/접근/구조 오류 exit 2다. `status`는 운영 기록을 반환하며 전체 수용 완료를 선언하지 않는다.

## 전송과 장애 복구

```bash
python3 "$control" --work-root "$work_root" run \
  --socket "$control_socket" --document "$document" --once
# 사용자가 전경에서 유지할 때만 --once를 생략한다. Ctrl-C로 종료한다.
```

등록된 thread만 `thread/read(includeTurns=true)`로 읽는다. 정확한 cwd, activeFlags가 빈 active thread와 유일한 inProgress turn이 확인되고 `canAcceptDirectInput=true`가 확인될 때만 `turn/steer(expectedTurnId)`를 보낸다. active/inProgress는 로드된 실행의 근거로 사용한다. `canAcceptDirectInput=null`은 입력 가능성 미확인이므로 전송하지 않는다. idle·미로드·모호한 상태는 deferred이며 깨우지 않는다. thread/start, turn/start, resume, interrupt, daemon 설치/시작은 구현하지 않는다.

현재 정본 해시/개정이 게시 상태와 달라지면 전송은 deferred다. 수동 ACK/hold 해제 후 resolve의 계약 비교와 자동 전송의 정확한 소스 비교는 서로 다른 검사다. `run` 출력은 처리 호출 성공일 뿐이며 각 결과는 `status`에서 확인한다.

전송 전에 sending과 시도 횟수를 원자적으로 저장한다. 기본 `--max-attempts 3`은 연결·초기 조회를 포함한 대상별 유한 시도 한도다. `--timeout 5`는 각 WebSocket 작업의 제한이며 `--interval 5`는 전경 감시 간격이다. 연결 실패·idle 조회도 시도를 소비한다. 한도 뒤에는 수동 경계 확인/ACK 또는 현재 기준의 새 이벤트와 명시적 supersede로 이어간다. 자동 무한 재시도는 없다.

steer 전송 경계 이후 응답 유실은 uncertain이다. 재시작 시 남은 sending도 uncertain으로 바꾸며 자동 재송신하지 않는다. 명백한 서버 거부도 보수적으로 uncertain에 남을 수 있다. 실제 세션과 원래 이벤트 ID/개정을 수동 대조하고 실제 read/held/applied 근거를 남긴다. 불확실한 내용을 확인 없이 재게시하지 않는다. 이 절차는 exactly-once나 작업자의 지시 준수를 보장하지 않는다. A 모드에서도 미해결 상태와 ACK 이력은 유지된다.

## 저장과 검증 경계

`control/state.json`을 `fcntl.flock`과 임시 파일/fsync/원자적 교체로 직렬화한다. 네트워크 대기 중 state lock은 잡지 않는다. 별도 비차단 watcher lock으로 프로젝트당 감시 하나만 허용한다. 손상된 JSON/중복 key/잘못된 상태/소유자/심볼릭 링크는 실패하고 빈 상태로 덮어쓰지 않는다. 손상 복구는 원본을 보존하고 실제 정본·세션 근거와 대조한 뒤 수행한다. 세션별 work.md와 다른 작업자의 소스는 수정하지 않는다.

운영 상태는 누적 이벤트/ACK를 담으며 대용량 전사나 모델 결과를 저장하지 않는다. 상태 상한은 16 MiB, WebSocket 메시지 상한은 8 MiB다. 제한을 넘으면 실패하고 기록 정리를 자동 수행하지 않는다. WebSocket은 handshake digest, masked client text, 응답 ID, fragment·ping/pong·close와 시간 제한을 검사한다. 같은 계정의 협력 도구이며 악성 동일 계정 프로세스에 대한 보안 경계는 아니다.

검증은 임시 프로젝트 CLI, 동시 ACK 프로세스와 synthetic Unix WebSocket 서버를 사용한다. 이들은 실제 사용자/모델 작업자의 보류·ACK나 대상 VM 동작을 입증하지 않는다. 실제 격리 Codex initialize 검사는 별도 실행 근거로 보고한다. 설치 자체는 서버나 감시를 시작하지 않는다.
