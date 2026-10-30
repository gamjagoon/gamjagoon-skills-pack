# gamjagoon-skills-pack

**AGENTS.md + 작업 스킬 3개 + 공통 질문 스킬 + 리뷰 에이전트 1개**

`AGENTS.md`에 공통 작업 지침을 두고, 요구사항·아키텍처·개발은 스킬로 수행하는 팩입니다.
세 단계의 리뷰는 하나의 `gsp-reviewer` 에이전트가 담당합니다.
지침·스킬·리뷰 에이전트는 영어로 작성하며, 이 README는 한국어로 사용법을 설명합니다.
`install.sh`가 Markdown과 에이전트 TOML을 프로젝트에 설치합니다. Python·uv·npm 패키지는 필요 없습니다.

## 사용하기

작업 폴더에서 Codex를 켜고 요청하세요.

> gamjagoon-skills-pack 설치해줘.

Codex가 이 저장소를 찾아 `install.sh`로 `AGENTS.md`, `.agents/skills/`, `.codex/agents/gsp-reviewer.toml`을 현재 프로젝트에 적용합니다.
그다음에는 작업 내용만 전달하세요. 특정 단계만 원하면 “요구사항만 작성해줘” 또는
“아키텍처 리뷰해줘”처럼 요청할 수 있습니다.

이름으로 저장소를 찾지 못하면 [저장소 주소](https://github.com/gamjagoon/gamjagoon-skills-pack)를 전달하세요.
새 스킬이나 에이전트가 보이지 않으면 Codex에서 해당 프로젝트의 신뢰 상태를 확인하고 다시 실행하세요.
설치 스크립트는 프로젝트를 자동으로 신뢰 처리하거나 전역 설정을 수정하지 않습니다.
파일 설치와 에이전트의 실제 로드는 별개입니다. 지원하지 않는 환경에서는 해당 한계를 알리고,
같은 검토 지침으로 독립 리뷰를 수행하거나 독립 리뷰 미실행을 명시합니다.

## 구성과 흐름

```text
install.sh
AGENTS.md
.codex/agents/
└── gsp-reviewer.toml
.agents/skills/
├── gsp-grilling/SKILL.md
├── gsp-requirements/SKILL.md
├── gsp-architecture/SKILL.md
└── gsp-development/
    ├── SKILL.md
    └── references/parallel-work.md
```

| 순서 | 스킬 또는 에이전트 | 하는 일 |
| --- | --- | --- |
| 1 | [요구사항 작성](.agents/skills/gsp-requirements/SKILL.md) | 원문·범위·완료 기준 정리 |
| 2 | [gsp-reviewer](.codex/agents/gsp-reviewer.toml) · `requirements` 모드 | 누락·모순·검증 가능성 확인 |
| 3 | [아키텍처](.agents/skills/gsp-architecture/SKILL.md) | 최소 구조·인터페이스·구현 작업 설계 |
| 4 | [gsp-reviewer](.codex/agents/gsp-reviewer.toml) · `architecture` 모드 | 요구사항 충족·실행 가능성 확인 |
| 5 | [개발](.agents/skills/gsp-development/SKILL.md) | 구현·실험·실제 검증 |
| 6 | [gsp-reviewer](.codex/agents/gsp-reviewer.toml) · `development` 모드 | 결함·회귀 확인, 수정·재검증·인계 |

리뷰 에이전트 정의는 하나이며, 가능하면 같은 리뷰 대화를 이어 사용합니다. 매번 현재 원문·산출물과
검토 모드를 전달하고, 리뷰어는 검토 결과를 반환하며 주 작업자가 수정·다음 단계 진행을 담당합니다.
리뷰마다 사용자 승인을 기다리지는 않습니다. 중요한 미결정만 질문하며, 기존 문서가
없으면 실제 작업 중 `TASK.md` 하나에 결과를 모읍니다. 단순한 수정은 필요한 단계만 사용합니다.

리뷰는 실제 원문·파일·검증 근거를 읽고 PASS/WARN/FAIL과 차단 여부를 남깁니다.
차단된 항목에 의존하는 다음 작업은 해결 근거가 생긴 뒤 진행하며, 수정한 결함은 원래
실패 조건으로 다시 확인합니다. 새 작업과 재개를 구분하고, 변경된 부분의 이전 리뷰만
다시 확인합니다. 최종 결과에는 완료 근거와 미실행 항목을 함께 남깁니다.

## 모호한 내용은 질문으로 확인

모든 단계에 공통 보조 스킬 [gsp-grilling](.agents/skills/gsp-grilling/SKILL.md)이 연결됩니다.
별도 설치나 “질문해줘” 프롬프트 없이, 결과를 바꾸는 모호한 내용은 선택지·추천안과 함께 묻습니다.
답변이 필요한 부분은 기다리고, 답변과 무관한 작업은 계속합니다. 파일이나 실행으로 알 수 있는
사실은 먼저 조사하며 이미 답한 내용은 다시 묻지 않습니다.

리뷰 서브에이전트가 발견한 질문도 주 작업자가 모아서 전달합니다. 답변에 따라 후속 질문을
이어가고, 결정이 끝나면 해당 단계부터 진행합니다. 작업 흐름은 기존 여섯 단계 그대로이며,
설치되는 구성은 작업 스킬 3개, 질문용 스킬 1개, 리뷰 에이전트 1개입니다.

## 모델과 병렬 작업

[AGENTS.md](AGENTS.md)에 Sol/Luna의 역할별 effort 권장값이 있습니다.
리뷰 에이전트는 **GPT-6.1 Sol / medium**으로 설정됩니다. 주 작업 모델·전역 설정·서비스 속도는 변경하지 않습니다.
프로젝트 에이전트는 [공식 Codex 형식](https://learn.chatgpt.com/docs/agent-configuration/subagents)에 따라
`.codex/agents/gsp-reviewer.toml` 하나로 정의하며, 별도의 `config.toml`을 추가하지 않습니다.
읽기 전용은 리뷰 수행 지침입니다. 에이전트는 부모의 권한을 상속하므로, 파일을 쓰는 검증은 격리된 복사본에서 실행합니다.

읽기 전용 조사는 원본을 공유하고, 파일을 바꾸는 실험은 worktree나 임시 폴더로 분리합니다.
실행 가능한 예시와 환경·출력·포트 분리, 결과 통합 방법은
[병렬 작업 안내](.agents/skills/gsp-development/references/parallel-work.md)에 있습니다.

## 설치를 수행하는 Codex에게

사용자가 설치나 업데이트를 요청하면 **이 저장소의 `install.sh`를 사용하세요.**
개별 스킬만 내려받는 기본 skill-installer나 수동 파일 복사로 설치를 대신하지 않습니다.

1. 사용자의 원래 작업 폴더의 절대 경로를 기록한다. 공개 저장소의 **현재 main**을 임시 소스 경로에 내려받고 README와 `install.sh`를 읽는다. 스크립트와 `.agents/skills/`, `.codex/agents/gsp-reviewer.toml`, `AGENTS.md`를 함께 받아야 한다.
2. 아래처럼 원래 프로젝트를 명시해 먼저 미리 보고, 성공하면 실제 설치를 실행한다. 사용자가 명령을 외우거나 직접 입력할 필요는 없다.

   ```bash
   bash "$source_dir/install.sh" --dry-run "$project_dir"
   bash "$source_dir/install.sh" "$project_dir"
   ```

3. 충돌하면 대상과 소스의 차이를 확인한다. 기존 사용자 수정은 보존·병합하고, 교체가 적절한 관리 파일은 `--overwrite --dry-run` 확인 후 `--overwrite`로 백업·교체한다. 구버전의 세 리뷰 `SKILL.md` 정리도 미리보기에서 확인하며, 사용자 수정이 있으면 차이를 검토해 먼저 보존·병합한다. 설치를 통과시키기 위해 사용자 내용을 버리지 않는다.
4. Codex가 `.agents`나 `.codex` 쓰기 승인을 요구하면 정상 승인 절차를 이용한다. 승인이 불가능하면 설치 미완료와 차단 원인을 알린다. 스크립트가 플랫폼 권한을 우회하지는 않는다.
5. 설치한 프로젝트의 `AGENTS.md`, 네 개의 `SKILL.md`, 참조 문서와 `gsp-reviewer.toml`를 읽어 현재 대화에 적용한다. 스크립트 성공은 파일 설치 확인이며, 실제 스킬 탐색·서브에이전트 실행과 구분한다. 작업 원문이 없으면 설치 완료 후 기다린다.

구버전 업데이트에서는 세 리뷰 스킬의 `SKILL.md`가 남아 있으면 기본 설치를 중단합니다.
차이를 검토한 뒤 `--overwrite`를 사용하면 해당 파일들을 `.gsp-backups/`에 백업하고 제거해
리뷰 스킬과 리뷰 에이전트가 중복되지 않게 합니다. 같은 폴더의 다른 파일은 보존합니다.
기존 `TASK.md`, `.codex/config.toml`, 다른 에이전트와 입력 키 설정도 유지합니다.
스크립트는 구버전의
`timeboxed-workflow`나 `.codex/agents/gsp-*.toml`을 자동 삭제하지 않습니다.
현재 팩의 `gsp-reviewer.toml`은 정리 대상이 아닙니다.
Codex가 해당 파일의 출처와 사용자 수정을 확인한 뒤, 이전 팩에서 온 지침만 백업으로
옮겨 중복을 정리하세요. 소유가 불명확하면 삭제하지 않습니다.

## 스크립트 동작

Linux/WSL의 Bash와 기본 Unix 도구를 사용합니다. 스크립트는 다운로드나 모델 호출 없이
같이 받은 파일을 설치합니다. 대상 폴더를 생략하면 현재 작업 폴더를 사용합니다.

- `--dry-run`: 충돌과 변경 계획만 확인합니다.
- `--overwrite`: 다른 내용의 관리 파일을 백업·교체하고, 구버전의 세 리뷰 스킬 파일을 백업·제거합니다.
- 기존 `AGENTS.md`의 관리 블록 밖 내용, 다른 스킬·에이전트·프로젝트 설정과 `TASK.md`는 유지합니다.
- 같은 파일은 다시 쓰지 않으며 백업은 `.gsp-backups/`에 남깁니다.
- 사용자 홈·전역 Codex 설정 경로와 관리 대상 심볼릭 링크는 거부합니다.

[MIT 라이선스](LICENSE)
