# 병렬 작업: 격리, 소유권, 통합

독립된 작업만 나누고 한 부모가 통합한다. 고정된 병렬 수는 없다. 작은 작업은 한 에이전트로 끝내도 된다. 역할과 모델은 프로젝트 루트의 `AGENTS.md` 지침을 따른다. 서브에이전트 기능이 없으면 가능한 작업을 직접 진행하고 독립 리뷰를 실행하지 못한 한계를 남긴다.

## 할당 계약

각 할당에 목표, 필요한 입력·근거, 담당 파일/디렉터리, 금지 범위, 기준 커밋과 현재 변경, 실제 cwd, 완료 기준, 검증 명령, 반환할 결과와 알려진 장애를 적는다. 쓰기 소유권은 겹치지 않게 한다. 다른 작업자가 있음을 알리고 기존 변경을 되돌리지 않도록 한다. 부모는 요구사항·설계·통합과 최종 결과에 책임을 진다.

반환 결과에는 수정 파일, 패치 또는 커밋, 실제 실행한 명령·결과, 실패 로그, 미실행 항목을 포함한다. 리뷰는 읽기 전용으로 수행하고 위치·발생 조건·영향이 있는 결함을 반환한다. 추측한 우려는 따로 표시한다.

## 읽기 전용 작업

로그 분류, 탐색, 조사, 리뷰는 공유 저장소를 읽을 수 있다. 파일 수정, formatter, 패키지 설치, 테스트의 캐시/스냅샷 쓰기도 금지 범위에 포함한다. 쓰기를 유발하는 검증이 필요하면 격리한 디렉터리에서 수행한다. 예를 들어 저장소 경로를 명시해 상태와 차이를 읽는다.

```sh
repo=/absolute/path/to/project
git -C "$repo" status --short
git -C "$repo" diff --stat
```

## 쓰기 작업: Git worktree

Git 저장소에 유효한 HEAD가 있으면 별도 worktree가 기본 선택이다. 먼저 저장소의 현재 변경과 기준을 확인한다. 아래 확인과 HEAD worktree 생성은 원본이 dirty여도 가능하지만 미커밋 변경은 전달되지 않는다. clean이면 바로 할당하고, dirty이면 뒤의 현재 변경 전달 절차를 완료한 후 할당한다.

```sh
repo=/absolute/path/to/project
git -C "$repo" rev-parse --show-toplevel
git -C "$repo" rev-parse --verify HEAD
git -C "$repo" status --short
```

유효한 HEAD를 확인한 다음, 본인 소유의 새 임시 부모 아래에 detached worktree를 만든다. dirty 원본에서도 이 생성 명령을 먼저 실행해 `experiment_root`와 `experiment_dir`를 준비한다. 자동 commit이나 stash는 필요 없다.

```sh
experiment_root=$(mktemp -d "${TMPDIR:-/tmp}/gsp-work.XXXXXX")
experiment_dir="$experiment_root/worker-a"
git -C "$repo" worktree add --detach "$experiment_dir" HEAD
git -C "$experiment_dir" rev-parse --show-toplevel
git -C "$experiment_dir" rev-parse HEAD
```

worker에 `experiment_dir`의 실제 절대 경로를 전달하고 첫 명령에서 cwd와 기준을 확인하게 한다. 부모의 shell cwd 변경이 에이전트·다른 도구에 자동 전파된다고 가정하지 않는다. 일반 서브에이전트 호출은 cwd나 sandbox를 자동 분리하지 않는다. spawn 도구에 cwd 격리 기능이 없으면 각 도구가 할당한 절대 경로와 cwd/workdir를 따르는지 검증한다. 이를 보장할 수 없으면 공유 원본에서 동시에 쓰지 말고 쓰기 작업을 순차 수행한다. 각 실행 도구의 cwd/workdir를 명시한다. shell 예시는 다음과 같다.

```sh
(cd "$experiment_dir" && pwd && git status --short)
```

worktree는 파일 변경 분리를 돕지만 보안 경계가 아니다. 자격 증명, 네트워크, 홈 디렉터리, Git 공용 메타데이터에는 접근할 수 있다. 컨테이너를 자동 생성하지 않는다. 별도 보안 격리가 필요한 작업은 사용 환경과 권한을 따로 설계한다.

## dirty baseline, HEAD 없음, 비 Git 프로젝트

HEAD worktree에는 원본의 미커밋 변경이 포함되지 않는다. 현재 작업을 실험해야 한다면 기준을 기록하고 **직접 검토한 허용 파일만** 전달한다. 추적 파일 변경은 경로별 패치를 만들고, 미추적 파일은 내용·비밀정보·크기를 확인한 명시적 파일만 복사한다. 전체 프로젝트, 홈, `.env`, 자격 증명, 캐시 또는 미추적 파일 전체를 일괄 복사하지 않는다. 원본을 정리하려고 자동 commit/stash하지 않는다.

예를 들어 현재 변경 중 `src/feature.py`와 `tests/test_feature.py`만 필요한 경우다. 패치는 민감한 내용이 없는지 검토하고 비공개 작업 경로에 둔다.

```sh
umask 077
git -C "$repo" diff --binary HEAD -- src/feature.py tests/test_feature.py > "$experiment_root/baseline.patch"
git -C "$experiment_dir" apply --check "$experiment_root/baseline.patch"
git -C "$experiment_dir" apply "$experiment_root/baseline.patch"
git -C "$experiment_dir" diff --stat
```

이 패치는 staged와 unstaged의 최종 추적 파일 상태를 HEAD와 비교한다. 필요한 현재 변경이 빠지지 않았는지 부모가 확인한다. worker는 전달받은 baseline diff를 별도로 보관하여 자신의 결과와 구분한다. 미추적 파일은 위 패치에 포함되지 않는다.

Git이 없거나 HEAD가 없으면 새 임시 폴더에 검토한 허용 목록을 복사한다. 아래 경로는 예시이므로 실제로 존재하는 필요한 파일로 바꾼다. 숨김 파일이나 디렉터리 전체를 무심코 추가하지 않는다.

```sh
copy_root=$(mktemp -d "${TMPDIR:-/tmp}/gsp-copy.XXXXXX")
mkdir -p "$copy_root/project/src" "$copy_root/project/tests"
cp -- "$repo/pyproject.toml" "$copy_root/project/pyproject.toml"
cp -- "$repo/src/feature.py" "$copy_root/project/src/feature.py"
cp -- "$repo/tests/test_feature.py" "$copy_root/project/tests/test_feature.py"
```

복사 목록, 관찰한 원본 변경·기준·해시, 누락한 의존성, 복사본의 제한을 기록한다. 원본과 복사본의 허용 파일을 비교해 현재 변경이 반영됐는지 확인한다. 기준 전달이 불완전하면 결과를 전체 통합 성공으로 보고하지 않는다.

## 출력과 실행 환경

각 worker는 독립 출력·로그 경로, 가상 환경/캐시와 필요한 포트를 갖는다. `uv`와 로컬 Python이 있는 환경에서는 다음처럼 가상 환경·uv 캐시·임시 파일·출력을 해당 실험 아래에 둔다. 실제 의존성 설치도 이 가상 환경과 캐시를 명시한다. 아래 예시는 출력 분리만 확인하며 프로젝트 검증을 대신하지 않는다.

```sh
mkdir -p "$experiment_root/cache" "$experiment_root/tmp" "$experiment_root/output"
UV_CACHE_DIR="$experiment_root/cache" uv venv --python python3 "$experiment_root/venv"
(cd "$experiment_dir" && TMPDIR="$experiment_root/tmp" "$experiment_root/venv/bin/python" -c 'from pathlib import Path; import sys; print(Path.cwd()); Path(sys.argv[1]).write_text("isolated output\n")' "$experiment_root/output/smoke.txt")
```

공유 DB, 개발 서버, 외부 서비스, 빌드 캐시 같은 자원이 충돌하는지 먼저 확인한다. 서버가 지원하면 포트 0으로 바인딩해 OS가 할당한 포트를 읽는 방식을 우선한다. 고정 포트가 필요하면 사용 가능 여부를 확인하지만 사전 확인은 포트 예약이 아니므로 실제 바인딩 실패도 처리한다. 실제 할당된 값과 프로세스 소유자를 기록한다. worktree만 나눴다고 실행 환경까지 격리되지는 않는다. 본인 작업의 프로세스만 종료한다.

## 부모의 통합과 정리

worker는 원본에 직접 merge·덮어쓰기하지 않는다. 부모가 반환된 변경을 baseline과 비교하고 소유 파일·요구사항·범위를 확인한다. 다른 사람이 원본을 바꿨는지 다시 확인하고 대상 경로의 변경만 통합한다. 예를 들어 검토한 결과 패치에는 먼저 `git apply --check path/to/result.patch`를 실행한다. 충돌하면 해당 부분을 직접 조정하고 관련 테스트와 최종 통합 검증을 실행한다. `--check` 통과는 기능 성공의 증거가 아니다.

실패 근거와 필요한 결과를 보존한 후, 더 이상 필요 없는 본인 소유의 clean worktree는 `git -C "$repo" worktree remove "$experiment_dir"`로 제거할 수 있다. dirty worktree는 필요한 패치·로그를 먼저 보존하고 확인한다. 다른 사람의 디렉터리나 변경을 지우지 않으며 `git clean -fd`, `reset --hard`, 강제 worktree 삭제를 정리 기본값으로 사용하지 않는다.

공식 환경 설명: [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [Git worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees). 설치된 정책과 현재 환경의 기능 지원은 각각 확인해야 한다.
