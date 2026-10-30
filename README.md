# gamjagoon-skills-pack

**A project-local Codex workflow pack for focused, 180-minute development.**

작업 내용을 주면 Codex가 요구사항 정리부터 구현·검증·인계까지 진행하도록 돕는
프로젝트 설정 팩입니다. 180분 기본 흐름, 역할별 에이전트 설정, 병렬 실험 지침,
작업 기록 양식과 Enter 줄바꿈 설정을 설치합니다.

## 설치와 사용

새 폴더 또는 기존 프로젝트에서 Codex를 켜고 요청하세요.

> gamjagoon-skills-pack 설치해줘.

Codex가 공개 저장소의 [설치 안내](INSTALL.md)를 따라 현재 폴더에 구성합니다.
설치 명령이나 단계별 프롬프트를 외울 필요가 없습니다. 설치 후에는 **원하는 작업 내용만
전달하세요.** 추가로 “180분으로 진행해줘”라고 입력하지 않아도 기본 흐름이 적용됩니다.
설치 자체로 작업 시간이 시작되지는 않습니다.

이미 정한 시간·마감·프로젝트 지침이 있으면 그것을 우선합니다. 간단한 질문이나 작은
수정에 전체 180분 절차를 강제하지 않으며, 작업이 일찍 끝나면 바로 결과를 전달합니다.

최초 설치에는 공개 GitHub와 uv 배포처에 접근할 수 있어야 합니다. Codex가 이름으로
저장소를 찾지 못하면 [이 저장소 주소](https://github.com/gamjagoon/gamjagoon-skills-pack)를
전달하세요. 새 역할이나 입력 키가 인식되지 않으면 해당 프로젝트에서 Codex를 다시 실행하세요.

## 기본 작업 흐름

| 경과 시간 | 진행할 일 |
| --- | --- |
| 0–20분 | 요구사항과 완료 기준, 최소 설계·작업 순서 정리 |
| 20–130분 | 핵심 기능부터 구현·실행, 60분 안에 핵심 흐름 첫 실행 |
| 130–165분 | 요구사항 검증, 독립 구현 리뷰 1회, 중요한 결함 수정 |
| 165–180분 | 최종 실행, 사용법·결과·남은 한계 정리 |

Codex는 실제 작업 시작과 진행 상황을 `TASK.md`에 기록합니다. 문서마다 사용자 승인을
기다리는 절차가 아니며, 결과에 영향을 주는 중요한 미결정만 질문합니다. 시간이 부족하면
필수 기능과 최종 검증을 우선하고, 구현하지 못한 항목을 명시합니다.

이 흐름은 설치된 지침을 읽은 Codex가 수행합니다. 설치 프로그램 자체는 모델을 호출하거나
백그라운드 타이머를 실행하지 않습니다.

## 설치되는 구성

| 파일·폴더 | 용도 |
| --- | --- |
| `AGENTS.md` 관리 블록 | 기본 시간 배분, 역할 선택, 작업 운영 지침 |
| `TASK.md` | 요구사항·완료 기준·결정·진행·실행 근거 기록; 기존 파일 유지 |
| `.agents/skills/timeboxed-workflow/` | 필요한 단계에서 읽는 워크플로와 병렬 작업 참조 문서 |
| `.codex/agents/gsp-*.toml` | 역할별 모델·추론 강도·작업 지침 |
| `.codex/config.toml` | 프로젝트 로컬 줄바꿈·전송 키 |
| `.gamjagoon-skills-pack/` | 변경 전 백업과 로컬 설치 기록 |

기본 설치는 외부 스킬을 추가하지 않습니다. 사용자 전역 설정과 현재 대화의 모델은
변경하지 않습니다. 기존 `AGENTS.md`와 `.gitignore`의 관리 블록 밖 내용도 보존합니다.

## 역할별 에이전트

| 역할 | 모델 | effort | 용도 |
| --- | --- | --- | --- |
| `gsp-triage` | GPT-6 Luna | low | 읽기 전용 사실 추출·로그 확인 |
| `gsp-researcher` | GPT-6 Luna | medium | 읽기 전용 조사·코드 탐색 |
| `gsp-worker` | GPT-6 Luna | medium | 범위가 명확한 구현·작은 실험 |
| `gsp-integrator` | GPT-6.1 Sol | medium | 복잡한 구현·결과 통합 |
| `gsp-debugger` | GPT-6.1 Sol | high | 원인이 불명확한 오류·위험한 변경 |
| `gsp-reviewer` | GPT-6.1 Sol | medium | 읽기 전용 독립 구현 리뷰 |

주 작업에는 Sol medium을 권장하되 현재 모델을 자동 변경하지 않습니다. 역할은 필요한
경우에만 사용하며, 모든 작업을 여섯 에이전트에 나눠 보내지 않습니다. 사용자 지정 모델과
플랫폼 제약을 우선하고, 모델이나 서브에이전트 기능이 없으면 제한을 알립니다.
설정 파일 설치만으로 해당 모델의 이용 가능성이나 실제 실행이 확인되지는 않습니다.

## 병렬 조사와 실험

독립적인 조사는 읽기 전용으로 병렬 진행하고, 파일을 바꾸는 실험은 작업 공간을 분리합니다.
Git 프로젝트는 실험별 worktree를, Git을 사용할 수 없는 프로젝트는 필요한 파일만 복사한
임시 폴더를 사용합니다. 각 작업에 담당 파일·완료 기준·출력 경로·환경·포트를 지정하고,
주 에이전트가 결과를 비교해 검증된 변경만 통합합니다.

설치 시 빈 worktree나 컨테이너를 미리 만들지는 않습니다. 실제 작업에서 필요할 때
Codex가 준비합니다. worktree는 파일 변경을 분리하지만 보안 샌드박스는 아닙니다.
생성부터 실험·통합·정리까지의 절차와 명령 예시는 [병렬 작업 안내](docs/parallel-work.md)를 참고하세요.

## 입력 키

| 키 | 동작 |
| --- | --- |
| Enter, Ctrl+J | 줄바꿈 |
| Alt+Enter | 전송 |
| Ctrl+Enter | 터미널이 구분해서 전달하는 경우 전송 |

Codex CLI 0.165.0 설정 형식을 기준으로 합니다. 실제 키 전달과 프로젝트 설정 인식은
사용하는 터미널에서 확인하세요. [입력 키 안내](docs/keyboard.ko.md)에 복원 방법도 있습니다.

## 업데이트와 기존 프로젝트

Codex에 `gamjagoon-skills-pack 최신 버전으로 업데이트해줘`라고 요청할 수 있습니다.
설치 안내에 따라 변경을 미리 확인하고 기존 사용자 내용을 보존합니다. 같은 버전의 같은
구성을 다시 설치하면 파일을 다시 쓰지 않습니다. 변경된 관리 파일은 차이를 확인한 뒤
백업하고 교체하며, 기존 `TASK.md`는 덮어쓰지 않습니다. 기존 TASK에 기록된 시간이
180분과 다르면 해당 예산을 유지합니다.

## 수동 실행과 개발

일반 사용자는 위 설치 요청만 하면 됩니다. 직접 실행하려면 Python 3.11 이상과
[uv](https://docs.astral.sh/uv/getting-started/installation/)를 사용하세요. 아래 아카이브 경로는 Git 설치가 필요 없습니다.

```bash
uvx --python '>=3.11' --from https://github.com/gamjagoon/gamjagoon-skills-pack/archive/refs/tags/v0.3.0.tar.gz gsp setup ./my-project
```

`setup`은 전체 구성을, `init`은 입력 키를 제외한 구성을 설치합니다. 두 명령 모두
180분이 기본이며 `--minutes N`으로 새 TASK의 예산을 지정할 수 있습니다.
`--dry-run`은 변경 계획만 출력합니다. `setup --no-keyboard`는 기존 입력 키를 유지합니다.
`gsp doctor`는 설치 파일을 정적으로 검사하며, `gsp prompt`는 필요할 때 참조 내용을
확인하는 보조 명령입니다. 별도 프롬프트 입력은 기본 사용 절차에 필요하지 않습니다.

소스 개발과 검증:

```bash
uv sync --frozen
uv run --frozen pytest -q
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv build
uv run --frozen python tools/smoke_install.py
```

Linux/WSL을 우선 검증합니다. 파일 설치 검사와 실제 에이전트·터미널 동작 검사는 구분합니다.
구체적인 실행 결과는 [검증 기록](docs/validation.md), 자세한 사용법은
[사용 안내](docs/guide.ko.md)에 있습니다.

원본 코드와 문서는 [MIT](LICENSE)로 배포합니다.
