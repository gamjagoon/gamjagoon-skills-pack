# gsp-adopt 팩 포함

- 현재 단계: 구현·저자 검증 및 독립 development 리뷰 PASS. 완료.
- 요청: “gsp-adopt도 여기에 포함시켜”.
- 결과: 기존 개인 스킬 내용을 그대로 팩에 포함했다. 설치 대상은 **스킬 6개, 총 11개 파일**이다.
- 미해결 결정·차단: 없음.
- 범위: 현재 로컬 팩의 소스·설치 스크립트·안내·테스트 갱신. 원격 배포는 수행하지 않았다.

## 목차

- [기준과 변경](#기준과-변경)
- [검증 결과](#검증-결과)
- [독립 리뷰](#독립-리뷰)
- [사용법과 한계](#사용법과-한계)

## 기준과 변경

이전 [설치 범위 확인](install-scope-review.md)은 gsp-adopt를 포함하기 전 10개 파일 기준이다. 이번 요청으로 아래 항목을 변경했다. 기존 스킬 계약을 그대로 배포하는 작은 패키징 변경이므로 별도 요구사항·아키텍처·Task 문서 대신 이 보고서에 기준과 검증을 모았다.

| ID | 완료 기준 | 변경 위치 |
| --- | --- | --- |
| B1 | 검증된 gsp-adopt를 팩에 포함하고 명시된 설치 목록에 추가 | [스킬](../.agents/skills/gsp-adopt/SKILL.md), [install.sh](../install.sh) |
| B2 | 6개 스킬과 기존 프로젝트 adoption 사용법 안내, 설치만으로 adoption 실행 안 함 | [README](../README.md), [AGENTS](../AGENTS.md) |
| B3 | 새 설치 11파일, 불필요한 파일 제외, 재설치·충돌·백업·rollback 유지 | [installer tests](../tests/test_install.py) |

설치 목록에는 `.agents/skills/gsp-adopt/SKILL.md` 한 경로만 추가했다. 기존 10개 경로 및 제외 규칙은 유지한다. `AGENTS.md`는 기존 프로젝트의 GSP 전환 요청을 새 스킬로 연결하고 README는 사용법·파일 트리·스킬 수를 갱신한다. 여섯 번째 스킬은 기존 8단계의 별도 경쟁 절차가 아니라 요구사항·아키텍처·Task 기준을 복원하는 진입점이다.

개인 스킬과 팩의 스킬 내용은 byte 단위로 동일하다. SHA256은 `b222e4768e18540c2d38ac06d3db34e6a30ac50090a98fb52497c59943f13120`이다. 기존 개인 스킬은 변경하거나 삭제하지 않았다. CodeGraph 인덱스 확인·생성·갱신·실제 질의와 세 문서 정리 규칙을 그대로 보존한다.

## 검증 결과

기준: HEAD `bd656b1eed3d7800b7162ce97ea4dec0e5081540` + 기존 dirty 변경 + 이번 한정 변경. 임시 fixture에서 실제 Bash installer를 실행했다.

| 검사 | 결과 | 증거 범위 |
| --- | --- | --- |
| `python3 tests/test_install.py -v` | **5/5 PASS** | fresh 11파일·내용 일치, dry-run 무변경, 재설치, 기존 자료 보존, 합성 잡파일 13개 미유입 |
| development/adopt 관리 파일 충돌·overwrite | **PASS** | 기본 거절, preview 무변경, 사용자 수정본 백업, 재설치 무변경 |
| 중간 파일 교체 실패 주입 | **PASS** | 기존 관리 파일 복구와 새로 생성한 adopt 포함 파일 제거, 기존 자료 보존 |
| 변경 전 실제 5스킬 설치본 → 새 팩 | **PASS** | AGENTS 차이는 기본 preview에서 거절, overwrite preview 후 설치, 관리 파일 11개와 이전 AGENTS 백업 1개 |
| `bash -n install.sh` 및 `git diff --check` | **PASS** | Bash 문법 및 diff 공백 검사 |
| `/usr/bin/python3 .../quick_validate.py .agents/skills/gsp-adopt` | **PASS** | 스킬 메타데이터·기본 형식 |
| 개인/팩 스킬 비교 | **PASS** | byte 동일 |

기본 `python3`로 validator를 처음 실행했을 때는 환경에 PyYAML이 없어 실패했다. 이미 PyYAML이 있는 `/usr/bin/python3`로 같은 validator를 실행해 성공했다. 의존 패키지를 설치하거나 환경을 변경하지 않았다.

검증 로그: [checks.json](../.gsp-work/sessions/session-bundle-adopt-t9z1a5e5/checks.json), [실제 이전 설치본 갱신](../.gsp-work/sessions/session-bundle-adopt-t9z1a5e5/upgrade.json). 변경 전 소스 및 현재 검토 기준 해시는 [세션 기록](../.gsp-work/sessions/session-bundle-adopt-t9z1a5e5/work.md)에서 연결한다. 로컬 Git 제외 자료이므로 다른 checkout에서는 unavailable일 수 있다.

## 독립 리뷰

native `gsp-reviewer`(`gpt-6.1-sol / medium`), mode `development`가 B1–B3에 **PASS**를 반환했다. 확정 결함·필수 미검증·사용자 결정은 없으며 이전 PASS를 재사용하지 않았다.

리뷰어는 `/tmp/gsp-bundle-independent-w9azi1fi`의 허용 파일 복사본에서 installer tests **5/5 PASS**(4.063초), Bash 문법 PASS를 직접 확인했다. 원본 diff 공백 검사, README·AGENTS·신규 스킬의 로컬 링크, 개인/팩 스킬 byte 비교, 저장된 before와 현재 파일로 재생성한 `task.diff` 일치도 확인했다. rollback의 실패 지점은 신규 adopt 파일 설치 이후이므로 해당 파일 제거까지 검증된다.

이전 5스킬 설치본의 upgrade와 validator는 저자 로그를 검토했으며 독립 재실행한 것으로 표시하지 않는다. 검토한 소스·보고서 16개와 추가 검토 자료·개인 스킬은 종료 시 기준을 유지했다. 검토 당시 이 보고서 SHA256은 `1dc84e1322905728cd52c0ef2008d3236d4c431aafff4d163464dd4500f2a374`이며 이후 lead가 이 리뷰를 반영했다.

Lead comment: 결과를 수용한다. 추가 수정이 필요한 결함은 없으며 B1–B3을 완료로 기록한다. 독립 installer 실행과 저자 로그 검토를 구분하고, 이 결과를 새 Codex 세션의 탐지나 전체 adoption 성공으로 확대하지 않는다.

## 사용법과 한계

수정된 팩 설치 후 대상 프로젝트에서 다음과 같이 요청할 수 있다.

```text
gsp-adopt로 기존 코드와 문서를 조사해서 요구사항, 아키텍처, Task를 정리해줘.
```

설치 자체는 지침 파일만 배포한다. CodeGraph 도구 설치·인덱스 생성, 대상 프로젝트 문서 작성 및 실제 개발은 실행하지 않는다. CodeGraph는 adoption을 수행할 때 필요한 사전 준비다.

이번 검증은 Linux/WSL의 실제 installer 실행과 패키징 확인이다. 다른 OS, 새 Codex 세션의 스킬 자동 탐지·agent 로딩, 모든 프로젝트에서의 전체 adoption 실행, 원격 배포는 확인하지 않았다. 스킬 내용이 동일하므로 기존 문서 산출·CodeGraph 행동 검증을 새로 반복하지 않았다.
