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
- `.codex/agents/gsp-reviewer.toml`: name/description/developer_instructions/sandbox_mode만 지정, 모델과 effort 상속.
- `.gitignore`의 관리 블록: 로컬 백업·설치 기록 제외.
- `.gamjagoon-skills-pack/`: 로컬 설치 기록과 교체 전 백업. 프로젝트 자료를 전송하지 않는다.

## 보호와 업데이트

모든 대상 파일과 경로를 사전 검사한다. 관리 대상 경로에 심볼릭 링크가 있으면 중단한다. dry-run은 새 폴더도 만들지 않는다. 동일 설치는 무변경이며 TASK.md는 보존한다. 다른 내용의 관리 파일은 기본적으로 충돌 처리하고, 명시적 --overwrite에서만 백업 후 교체한다. AGENTS.md와 .gitignore의 기존 본문은 관리 블록 외부까지 유지한다. 교체 쓰기는 임시 파일과 os.replace를 이용하며, 실패 시 이전 파일 내용 복구를 시도하고 실패 상태를 보고한다. 동시 실행은 지원하지 않으며 작업 중 다른 프로세스가 파일을 바꾸면 중단한다.

## 선택 외부 스킬

외부 스킬 원문은 이 저장소에 동봉하지 않는다. 카탈로그는 원본 저장소, 40자리 커밋, 스킬 폴더, 라이선스 링크만 가진다. GitHub tree와 raw endpoint에서 해당 커밋의 필요한 파일만 받아 경로·크기·종류와 Git blob 해시를 검사한다. 라이선스 파일이 스킬 밖에 있으면 별도 포함한다. 인증 토큰을 자동으로 읽지 않으며 프로젝트 자료 업로드, npm, 원격 코드 실행은 하지 않는다. 선택 스킬의 후속 지침이나 도구 의존성은 사용자가 별도로 검토한다.

## 단계와 검증

프롬프트 stage ID: start, requirements, requirements-review, design-tasks, plan-review, feasibility, implement, implementation-review, verify, handoff.

리뷰어는 읽기 전용이며 원문·현재 TASK·변경 파일·실제 검증 근거를 검토한다. 지원 환경에서 서브에이전트 호출을 사용하고, 지원하지 않는 경우 같은 프롬프트를 별도 리뷰 대화에 전달한다. 설치와 doctor는 런타임 호출을 보장하지 않는다. 실제 제작 시간 예산은 전체 시험 시간과 분리하며, 기본 240분은 사용자 조정 가능한 초기값이다.
