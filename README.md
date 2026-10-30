# gamjagoon-skills-pack

**A uv-installable Codex starter for hackathons and timeboxed development.**

Install Korean workflow prompts, a project-local skill, and a read-only reviewer.
Track requirements through implementation and verification. Keep your existing project
instructions and model settings. No API key, Node.js, or external skills are required
for the core workflow. This tool does not invoke Codex or solve tasks automatically.

## 빠른 시작

Python 3.11 이상과 [uv](https://docs.astral.sh/uv/getting-started/installation/)가 필요합니다.
Git URL에서 설치할 때는 Git도 필요합니다. Codex는 제공된 환경의 설치·로그인을 사용합니다.

```bash
uv tool install git+https://github.com/gamjagoon/gamjagoon-skills-pack.git@v0.1.0

# 실제 제작에 쓸 수 있는 시간으로 지정하세요.
gsp init ./my-project --minutes 180 --dry-run
gsp init ./my-project --minutes 180
cd my-project

gsp doctor
gsp prompt start
```

출력된 프롬프트를 프로젝트를 연 Codex 대화에 전달하세요. 새 지침과 리뷰어가
보이지 않으면 해당 프로젝트에서 새 Codex 세션을 시작하고 인식 여부를 확인하세요.
`doctor`는 설치 파일과 설정을 정적으로 검사하며 실제 Codex 실행은 하지 않습니다.

CLI를 계속 설치하지 않고 실행하려면 다음과 같이 사용할 수 있습니다.

```bash
uvx --from git+https://github.com/gamjagoon/gamjagoon-skills-pack.git@v0.1.0 gsp init ./my-project
```

이후 명령도 같은 `uvx --from ... gsp` 형식으로 실행하거나 `uv tool install`을 사용하세요.

## 어떤 순서로 쓰나요?

| 단계 | 명령 | 확인할 것 |
| --- | --- | --- |
| 시작·환경 확인 | `gsp prompt start` | 실제 제작 시간, 원문, 파일, 도구 |
| 요구사항 | `gsp prompt requirements` | 모든 필수 항목과 관찰 가능한 완료 기준 |
| 내 리뷰 | `gsp prompt requirements-review` | 원문 해석과 범위, 중요한 미결정 |
| 설계·task | `gsp prompt design-tasks` | 단순한 구조와 실행·검증 가능한 작업 |
| 통합 계획 리뷰 | `gsp prompt plan-review` | 누락, 기술적 가정, 작업 의존성 |
| 위험 확인 | `gsp prompt feasibility` | 가장 불확실한 부분의 작은 실행 |
| 개발·검증 | `gsp prompt implement` | 핵심 흐름부터 작은 단위로 실행 |
| 구현 리뷰 | `gsp prompt implementation-review` | 변경 코드와 실제 검증 근거 |
| 최종 검증 | `gsp prompt verify` | 요구사항별 실제 결과와 미확인 부분 |
| 직접 확인·전달 | `gsp prompt handoff` | 재실행, 남은 문제, 제출 조건 |

모든 단계에서 별도 문서를 만들 필요는 없습니다. `TASK.md`에 요구사항, 설계,
작업, 결정, 검증을 모읍니다. 이미 승인된 범위는 불필요한 재확인 없이 진행하고,
범위나 결과를 크게 바꾸는 미결정은 사용자에게 확인합니다.

4시간 시험에서도 서술형과 제출 시간을 빼고 **실제 제작 시간**을 지정하세요.
`--minutes` 기본값은 240이며 타이머를 실행하거나 마감 시각을 임의로 확정하지 않습니다.
단계별 시간 배분은 [한국어 사용 안내](docs/guide.ko.md)를 참고하세요.

## 무엇이 설치되나요?

```text
my-project/
├── AGENTS.md                         # 기존 본문 + 워크플로 관리 블록
├── TASK.md                           # 없을 때만 생성
├── .gitignore                        # 기존 본문 + 로컬 백업 제외 블록
├── .agents/skills/timeboxed-workflow/
│   ├── SKILL.md
│   └── references/                    # 단계별 한국어 프롬프트
├── .codex/agents/gsp-reviewer.toml     # 읽기 전용, 모델·effort 미지정
└── .gamjagoon-skills-pack/             # 교체 전 백업·선택 스킬 설치 기록
```

기본 구성은 직접 작성한 워크플로 스킬 하나와 프롬프트·리뷰어입니다.
**외부 스킬은 기본으로 설치하지 않습니다.** 글로벌 Codex 설정, 모델, 추론 강도,
권한을 변경하지 않습니다. 리뷰어의 실제 모델은 Codex의 부모·역할 기본 설정을 따릅니다.

서브에이전트를 지원하는 환경에서는 `gsp-reviewer`에 원문, `TASK.md`, 변경 파일과
실행 근거를 전달하세요. 지원하지 않는 환경에서는 같은 리뷰 프롬프트를 별도 대화에서
사용하세요. 이 패키지는 대화 전송이나 서브에이전트 호출을 자동화하지 않습니다.

## 기존 프로젝트에 적용하기

```bash
gsp init /path/to/existing-project --dry-run
gsp init /path/to/existing-project
```

- 기존 `AGENTS.md`와 `.gitignore`의 관리 블록 밖 내용은 유지합니다.
- 기존 `TASK.md`는 `--overwrite`를 지정해도 유지합니다.
- 동일한 설치를 반복하면 파일을 다시 쓰지 않습니다.
- 관리 파일이 다른 내용이면 실제 파일 변경 전에 충돌을 보고합니다.
- 확인 후 `--overwrite`를 사용하면 교체 파일을 로컬 백업에 남깁니다.
- 관리 경로의 심볼릭 링크는 거부합니다. 설치 도중 동시 수정을 피하세요.
- `AGENTS.override.md`가 있으면 같은 경로의 `AGENTS.md`를 가릴 수 있습니다.

```bash
gsp init /path/to/existing-project --overwrite --dry-run
gsp init /path/to/existing-project --overwrite
```

백업은 `.gamjagoon-skills-pack/backups/<id>/`에서 원래 상대 경로로 찾을 수 있습니다.
설치 도중 쓰기에 실패하면 이미 변경한 파일 내용을 복구하려고 시도합니다.
복구하지 못한 파일은 오류에 표시하며 백업 경로를 안내합니다.

## 선택 외부 스킬

```bash
gsp skills list
gsp skills add frontend-design --path ./my-project --dry-run
gsp skills add frontend-design --path ./my-project
```

| 이름 | 출처 | 상태 |
| --- | --- | --- |
| `frontend-design` | Anthropic | 선택 다운로드, Apache-2.0 |
| `systematic-debugging` | obra/Superpowers | 선택 다운로드, MIT |
| `verification-before-completion` | obra/Superpowers | 선택 다운로드, MIT |
| `pdf` | OpenAI | 라이선스가 확인된 legacy 고정 버전, Apache-2.0 |
| `web-design-guidelines` | Vercel | 원본 링크 안내 |

선택 다운로드는 카탈로그의 고정 커밋에서 전체 스킬 폴더와 라이선스를 받아 Git blob
해시를 확인합니다. 기존 스킬 폴더는 덮어쓰지 않습니다. npm, 외부 모델 계정이나
개인 API 키를 사용하지 않으며, 내려받은 스크립트도 실행하지 않습니다.
기본 `init`, `prompt`, `doctor`는 네트워크 요청을 하지 않습니다.

각 스킬의 후속 도구 의존성과 참조 스킬은 별도입니다. PDF 도구의 Python 패키지와
Poppler 등은 필요할 때 준비하세요. 고정 소스·라이선스·legacy 및 링크 안내 이유는
[외부 스킬 출처](docs/third-party.md)에 정리했습니다.

## 개발과 검증

```bash
git clone https://github.com/gamjagoon/gamjagoon-skills-pack.git
cd gamjagoon-skills-pack
uv sync --frozen
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv build
uv run python tools/smoke_install.py
```

Linux/WSL을 우선 대상으로 합니다. CI는 Linux에서 Python 버전별 테스트와 격리된
wheel 설치를 수행합니다. Windows·macOS의 실제 설치, Codex의 지침·리뷰어 런타임
탐색, 특정 시험환경의 허용 여부와 동작은 별도 확인 대상입니다. 검증 상태와 구체적인
실행 근거는 [검증 기록](docs/validation.md)에 남깁니다.

이 프로젝트는 특정 대회나 OpenAI·Anthropic·Vercel의 공식 제품이 아닙니다.
실제 과제의 규칙과 제출 조건을 우선하세요.

## License and references

Original code, prompts, and documentation: [MIT](LICENSE). Optional third-party skills
retain their own upstream licenses; their source content is not bundled here.

- [Codex project instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [uv tools](https://docs.astral.sh/uv/guides/tools/)
