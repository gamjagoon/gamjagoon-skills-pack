# 설계

## CLI

- 사용자 진입 문장은 `gamjagoon-skills-pack 설치해줘`다. 저장소의 README/INSTALL.md/llms.txt와 AGENTS.md가 설치 에이전트의 공개 진입점을 제공한다. 빈 폴더에서 아직 설치되지 않은 지침을 자동 탐색한다고 가정하지 않는다.
- `gsp setup [PATH] [--minutes N] [--dry-run] [--overwrite] [--no-keyboard]`: 기본 180분, 워크플로·리뷰어·줄바꿈을 한 번에 사전 검사해 적용하고 doctor를 수행한다. 설치 에이전트가 실행하며 사용자는 명령을 외우지 않는다.

- 패키지 `gamjagoon-skills-pack`, 실행 명령 `gsp` 및 `gamjagoon-skills-pack`.
- Python 3.11+ 표준 라이브러리; 빌드 도구는 hatchling, 개발 검증은 uv/pytest/ruff.
- `gsp init [PATH] [--minutes N] [--dry-run] [--overwrite]`: 자체 워크플로와 리뷰어 설치.
- `gsp prompt [STAGE]`: 단계 목록 또는 해당 한국어 프롬프트를 stdout으로 출력.
- `gsp doctor [PATH]`: 파일·TOML·명령 존재의 로컬 정적 검사. 실제 에이전트 실행 증거로 표현하지 않는다.
- `gsp keyboard [PATH] [--enter newline|submit] [--dry-run]`: 별도 선택 명령. `.codex/config.toml`의 composer.submit과 editor.insert_newline만 변경한다. 기본 init에는 입력 키 변경을 포함하지 않는다.
- `gsp skills list`: 선택 외부 스킬, 고정 커밋, 출처, 라이선스 정보 출력.
- `gsp skills add NAME [--path PATH] [--dry-run]`: 명시적으로 고른 스킬 폴더 전체 다운로드. 기존 스킬은 덮어쓰지 않는다.

## 설치 파일

- `AGENTS.md`의 명시적 관리 블록: 기존 본문을 보존하며 워크플로 참조 추가.
- `TASK.md`: 없을 때만 생성. 실제 제작 시간 예산, 원문 요구사항, 설계, task, 결정과 검증 결과.
- `.agents/skills/timeboxed-workflow/`: 자체 SKILL.md와 필요한 단계별 references.
- `.codex/agents/gsp-reviewer.toml`: Sol medium 읽기 전용 리뷰어. 다른 5개 역할과 함께 모델·effort·sandbox_mode를 프로젝트 범위에 지정한다.
- `.gitignore`의 관리 블록: 로컬 백업·설치 기록 제외.
- `.gamjagoon-skills-pack/`: 로컬 설치 기록과 교체 전 백업. 프로젝트 자료를 전송하지 않는다.

## 보호와 업데이트

모든 대상 파일과 경로를 사전 검사한다. 관리 대상 경로에 심볼릭 링크가 있으면 중단한다. dry-run은 새 폴더도 만들지 않는다. 동일 설치는 무변경이며 TASK.md는 보존한다. 다른 내용의 관리 파일은 기본적으로 충돌 처리하고, 명시적 --overwrite에서만 백업 후 교체한다. AGENTS.md와 .gitignore의 기존 본문은 관리 블록 외부까지 유지한다. 교체 쓰기는 임시 파일과 os.replace를 이용하며, 실패 시 이전 파일 내용 복구를 시도하고 실패 상태를 보고한다. 동시 실행은 지원하지 않으며 작업 중 다른 프로세스가 파일을 바꾸면 중단한다.

## 선택 외부 스킬

외부 스킬 원문은 이 저장소에 동봉하지 않는다. 카탈로그는 원본 저장소, 40자리 커밋, 스킬 폴더, 라이선스 링크만 가진다. GitHub tree와 raw endpoint에서 해당 커밋의 필요한 파일만 받아 경로·크기·종류와 Git blob 해시를 검사한다. 라이선스 파일이 스킬 밖에 있으면 별도 포함한다. 인증 토큰을 자동으로 읽지 않으며 프로젝트 자료 업로드, npm, 원격 코드 실행은 하지 않는다. 선택 스킬의 후속 지침이나 도구 의존성은 사용자가 별도로 검토한다.

## 단계와 검증

프롬프트 stage ID: start, requirements, requirements-review, design-tasks, plan-review, feasibility, implement, implementation-review, verify, handoff.

리뷰어는 읽기 전용이며 원문·현재 TASK·변경 파일·실제 검증 근거를 검토한다. 지원 환경에서 서브에이전트 호출을 사용하고, 지원하지 않는 경우 같은 프롬프트를 별도 리뷰 대화에 전달한다. 설치와 doctor는 런타임 호출을 보장하지 않는다. setup/init의 기본 180분은 사용자 조정 가능한 초기값이다. 기존 TASK의 예산과 진행 시각은 유지한다.


## v0.3.0 기본 운영

설치는 작업 타이머를 시작하지 않는다. 사용자가 개발 작업을 주면 AGENTS 관리 블록과
워크플로 스킬을 읽은 Codex가 0–20분 정리, 20–130분 구현, 130–165분 검증·독립 리뷰,
165–180분 인계를 적용한다. 60분에 핵심 흐름의 첫 실행을 목표로 한다. 별도 start 프롬프트나
열 단계별 승인을 요구하지 않는다. 명시된 다른 예산·마감과 기존 진행 기록은 우선하며,
짧은 수정·질문은 작업 규모에 맞춰 처리한다. 코드로 시간을 강제하거나 백그라운드 작업을
시작하는 기능은 없다.

역할은 gsp-triage(Luna low/read-only), gsp-researcher(Luna medium/read-only),
gsp-worker(Luna medium/workspace-write), gsp-integrator(Sol medium/workspace-write),
gsp-debugger(Sol high/workspace-write), gsp-reviewer(Sol medium/read-only)다.
model 값은 gpt-6-luna/gpt-6.1-sol, 추론 필드는 model_reasoning_effort를 사용한다.
모든 역할 TOML은 관리 파일 충돌·백업 규칙을 따른다. doctor는 필드와 기본 역할 정책을
검사하며 모델 이용 가능성이나 실제 spawn을 검증하지 않는다. 주 모델·전역 설정·서비스
티어·동시 실행 수는 변경하지 않는다.

병렬 실행은 작업을 하는 Codex가 필요할 때 수행한다. 독립 읽기 전용 조사는 원본을
공유할 수 있고, 쓰기 실험은 개별 worktree나 필요한 파일만 복사한 임시 폴더에서 수행한다.
기존 변경을 보존하고 각 에이전트의 경로·소유 파일·환경·출력을 지정하며 주 에이전트가
검증된 결과만 통합한다. worktree는 보안 경계가 아니며 에이전트 생성만으로 개별 작업
공간이 보장되지 않는다. 구체 절차는 [병렬 작업 안내](parallel-work.md)를 따른다.

기존 버전 업데이트는 관리 파일 차이를 확인한 후 --overwrite로 백업·교체한다.
사용자 수정이 섞여 있으면 병합 판단을 먼저 하며, 기존 TASK와 관리 블록 밖 내용은 보존한다.
