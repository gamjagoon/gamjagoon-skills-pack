# gamjagoon-skills-pack

**AGENTS.md + six Codex skills for requirements, architecture, development, and reviews.**

`AGENTS.md`에 공통 작업 지침을 두고, 각 단계를 별도 스킬로 나눈 팩입니다.
설치 프로그램이나 패키지 의존성 없이 Markdown 파일을 프로젝트에 복사해서 사용합니다.

## 사용하기

작업 폴더에서 Codex를 켜고 요청하세요.

> gamjagoon-skills-pack 설치해줘.

Codex가 이 저장소의 `AGENTS.md`와 `.agents/skills/`를 현재 프로젝트에 적용하면 됩니다.
그다음에는 작업 내용만 전달하세요. 특정 단계만 원하면 “요구사항만 작성해줘” 또는
“아키텍처 리뷰해줘”처럼 요청할 수 있습니다.

이름으로 저장소를 찾지 못하면 [저장소 주소](https://github.com/gamjagoon/gamjagoon-skills-pack)를 전달하세요.
새 스킬이 보이지 않으면 프로젝트에서 Codex를 다시 실행하거나 해당 `SKILL.md`를 읽도록 요청하세요.

## 구성과 흐름

```text
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

1. 사용자의 원래 작업 폴더를 대상으로 삼는다. 공개 저장소의 **현재 main**에서 파일을 읽거나 임시 경로에 내려받는다. 다운로드한 소스 폴더를 사용자 프로젝트로 착각하지 않는다.
2. `AGENTS.md`가 없으면 복사한다. 기존 파일이 있으면 내용을 보존하고 이 팩의 관리 블록을 병합한다. 같은 블록을 중복 추가하지 않는다. 기존 관리 블록에 사용자 수정이 있으면 먼저 비교하고 보존한다.
3. `.agents/skills/`의 위 여섯 폴더만 같은 프로젝트 경로에 복사한다. 다른 스킬은 유지한다. 같은 이름의 폴더가 있으면 차이를 확인하고 사용자 변경을 보존한다. 교체 전 사본은 프로젝트의 `.gsp-backups/`에 두고 해당 경로를 기존 `.gitignore`를 보존하며 제외한다. 동일한 파일은 다시 쓰지 않는다.
4. 대상이 사용자 홈 또는 전역 Codex 설정 폴더라면 적용하지 않는다. 대상 경로에 심볼릭 링크가 있으면 따라 써서 원본을 바꾸지 말고 충돌을 알린다. 설치 후 대상의 AGENTS와 여섯 SKILL 및 참조 파일을 읽어 현재 대화에 적용하고, 원래 사용자 내용이 보존됐는지 확인한다.
5. 구버전에서 업데이트할 때는 기존 `TASK.md`와 입력 키 설정을 유지한다. 이전 팩에서 온 `timeboxed-workflow` 폴더와 `.codex/agents/gsp-*.toml`만 출처와 사용자 수정 여부를 확인한 뒤 백업으로 옮겨 중복 지침을 정리한다. 소유가 불명확하면 삭제하지 말고 충돌을 알린다. 과거 태그의 설치 프로그램은 실행하지 않는다.

설치가 끝나면 사용자의 작업 요청을 기다립니다. Git·Python·uv로 설치 프로그램을 실행할
필요가 없으며, 파일 설치 성공이 실제 서브에이전트 실행을 보장하지는 않습니다.

[MIT License](LICENSE)
