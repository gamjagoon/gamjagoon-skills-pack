# gamjagoon-skills-pack

**AGENTS.md + six Codex skills for requirements, architecture, development, and reviews.**

`AGENTS.md`에 공통 작업 지침을 두고, 각 단계를 별도 스킬로 나눈 팩입니다.
`install.sh`가 Markdown 파일을 프로젝트에 설치합니다. Python·uv·npm 패키지는 필요 없습니다.

## 사용하기

작업 폴더에서 Codex를 켜고 요청하세요.

> gamjagoon-skills-pack 설치해줘.

Codex가 이 저장소를 찾아 `install.sh`로 `AGENTS.md`와 `.agents/skills/`를 현재 프로젝트에 적용합니다.
그다음에는 작업 내용만 전달하세요. 특정 단계만 원하면 “요구사항만 작성해줘” 또는
“아키텍처 리뷰해줘”처럼 요청할 수 있습니다.

이름으로 저장소를 찾지 못하면 [저장소 주소](https://github.com/gamjagoon/gamjagoon-skills-pack)를 전달하세요.
새 스킬이 보이지 않으면 프로젝트에서 Codex를 다시 실행하거나 해당 `SKILL.md`를 읽도록 요청하세요.

## 구성과 흐름

```text
install.sh
AGENTS.md
.agents/skills/
├── gsp-requirements/SKILL.md
├── gsp-requirements-review/SKILL.md
├── gsp-architecture/SKILL.md
├── gsp-architecture-review/SKILL.md
├── gsp-development/
│   ├── SKILL.md
│   └── references/parallel-work.md
└── gsp-development-review/SKILL.md
```

| 순서 | 스킬 | 하는 일 |
| --- | --- | --- |
| 1 | [요구사항 작성](.agents/skills/gsp-requirements/SKILL.md) | 원문·범위·완료 기준 정리 |
| 2 | [요구사항 리뷰](.agents/skills/gsp-requirements-review/SKILL.md) | 누락·모순·검증 가능성 확인 |
| 3 | [아키텍처](.agents/skills/gsp-architecture/SKILL.md) | 최소 구조·인터페이스·구현 작업 설계 |
| 4 | [아키텍처 리뷰](.agents/skills/gsp-architecture-review/SKILL.md) | 요구사항 충족·실행 가능성 확인 |
| 5 | [개발](.agents/skills/gsp-development/SKILL.md) | 구현·실험·실제 검증 |
| 6 | [개발 리뷰](.agents/skills/gsp-development-review/SKILL.md) | 결함·회귀 확인, 수정·재검증·인계 |

리뷰마다 사용자 승인을 기다리지는 않습니다. 중요한 미결정만 질문하며, 기존 문서가
없으면 실제 작업 중 `TASK.md` 하나에 결과를 모읍니다. 단순한 수정은 필요한 단계만 사용합니다.

## 모델과 병렬 작업

[AGENTS.md](AGENTS.md)에 Sol/Luna의 역할별 effort 권장값이 있습니다. 현재 모델이나
전역 설정을 자동 변경하지 않으며, 실제 모델 선택은 사용하는 Codex 환경의 기능을 따릅니다.

읽기 전용 조사는 원본을 공유하고, 파일을 바꾸는 실험은 worktree나 임시 폴더로 분리합니다.
실행 가능한 예시와 환경·출력·포트 분리, 결과 통합 방법은
[병렬 작업 안내](.agents/skills/gsp-development/references/parallel-work.md)에 있습니다.

## 설치를 수행하는 Codex에게

사용자가 설치나 업데이트를 요청하면 **이 저장소의 `install.sh`를 사용하세요.**
개별 스킬만 내려받는 기본 skill-installer나 수동 파일 복사로 설치를 대신하지 않습니다.

1. 사용자의 원래 작업 폴더의 절대 경로를 기록한다. 공개 저장소의 **현재 main**을 임시 소스 경로에 내려받고 README와 `install.sh`를 읽는다. 스크립트와 `.agents/skills/`, `AGENTS.md`를 함께 받아야 한다.
2. 아래처럼 원래 프로젝트를 명시해 먼저 미리 보고, 성공하면 실제 설치를 실행한다. 사용자가 명령을 외우거나 직접 입력할 필요는 없다.

   ```bash
   bash "$source_dir/install.sh" --dry-run "$project_dir"
   bash "$source_dir/install.sh" "$project_dir"
   ```

3. 충돌하면 대상과 소스의 차이를 확인한다. 기존 사용자 수정은 보존·병합하고, 교체가 적절한 관리 파일은 `--overwrite --dry-run` 확인 후 `--overwrite`로 백업·교체한다. 설치를 통과시키기 위해 사용자 내용을 버리지 않는다.
4. Codex가 `.agents` 쓰기 승인을 요구하면 정상 승인 절차를 이용한다. 승인이 불가능하면 설치 미완료와 차단 원인을 알린다. 스크립트가 플랫폼 권한을 우회하지는 않는다.
5. 설치한 프로젝트의 `AGENTS.md`, 여섯 `SKILL.md`와 참조 문서를 읽어 현재 대화에 적용한다. 스크립트 성공은 파일 설치 확인이며, 실제 스킬 탐색·서브에이전트 실행과 구분한다. 작업 원문이 없으면 설치 완료 후 기다린다.

구버전 업데이트에서 기존 `TASK.md`와 입력 키 설정은 유지합니다. 스크립트는 구버전의
`timeboxed-workflow`나 `.codex/agents/gsp-*.toml`을 자동 삭제하지 않습니다.
Codex가 해당 파일의 출처와 사용자 수정을 확인한 뒤, 이전 팩에서 온 지침만 백업으로
옮겨 중복을 정리하세요. 소유가 불명확하면 삭제하지 않습니다.

## 스크립트 동작

Linux/WSL의 Bash와 기본 Unix 도구를 사용합니다. 스크립트는 다운로드나 모델 호출 없이
같이 받은 파일을 설치합니다. 대상 폴더를 생략하면 현재 작업 폴더를 사용합니다.

- `--dry-run`: 충돌과 변경 계획만 확인합니다.
- `--overwrite`: 다른 내용의 관리 파일을 백업한 후 교체합니다.
- 기존 `AGENTS.md`의 관리 블록 밖 내용, 다른 스킬과 `TASK.md`는 유지합니다.
- 같은 파일은 다시 쓰지 않으며 백업은 `.gsp-backups/`에 남깁니다.
- 사용자 홈·전역 Codex 설정 경로와 관리 대상 심볼릭 링크는 거부합니다.

[MIT License](LICENSE)
