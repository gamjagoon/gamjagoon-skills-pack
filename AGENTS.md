# Installing or updating this pack

When the user asks to install or update **gamjagoon-skills-pack**, read this
repository's README and `install.sh`. Download the current repository into a
temporary source directory, preserve the user's original project path, and run
`bash install.sh --dry-run <project-path>` followed by `bash install.sh <project-path>`
when the preview succeeds. Use this script instead of manually copying files or
using the generic skill installer for individual folders. Preserve custom conflicts;
use `--overwrite` only after reviewing the differences. If Codex protects `.agents`,
use its normal approval flow and report a blocked installation if approval is unavailable.
After installation, read the target AGENTS and skills in the current conversation.
The script installs only the managed block below, not this source-only entrypoint.

<!-- GAMJAGOON-SKILLS-PACK:START -->
# gamjagoon-skills-pack

## 작업 흐름

개발 작업은 아래 순서로 진행한다. 현재 단계의 스킬을 읽고 산출물과 미해결 사항을 다음 단계에 전달한다. 사용자에게 단계별 호출을 요구하지 않는다. 사용자가 단계 하나만 요청하면 해당 단계까지만 수행한다. 단순 질문·작은 수정은 필요한 단계만 적용하고 생략 이유를 짧게 남긴다.

| 순서 | 스킬 | 산출물 |
| --- | --- | --- |
| 1 | [요구사항 작성](.agents/skills/gsp-requirements/SKILL.md) | 원문 근거, 범위, 요구사항별 완료 기준 |
| 2 | [요구사항 리뷰](.agents/skills/gsp-requirements-review/SKILL.md) | 누락·모순·검증 가능성 검토 |
| 3 | [아키텍처](.agents/skills/gsp-architecture/SKILL.md) | 최소 구조, 인터페이스, 구현 작업·검증 계획 |
| 4 | [아키텍처 리뷰](.agents/skills/gsp-architecture-review/SKILL.md) | 요구사항 충족, 실행 가능성·복잡성 검토 |
| 5 | [개발](.agents/skills/gsp-development/SKILL.md) | 구현, 실행·테스트 결과 |
| 6 | [개발 리뷰](.agents/skills/gsp-development-review/SKILL.md) | 결함·회귀 검토, 수정·재검증, 사용법과 한계 |

시작할 때 현재 요청이 기존 작업의 계속인지 별도 작업인지 원문·미완료 항목과 대조한다. 같은 작업이면 유효한 산출물부터 이어가고, 별도 작업이면 새 제목과 시작·마감 구획을 만든다. 완료된 작업의 PASS와 시간을 새 요청에 재사용하지 않는다. 실제 제작·개발 작업의 기록은 기존 위치를 우선하며, 없으면 `TASK.md` 하나에 아래 내용을 모은다. 단순 질의응답에는 작업 기록·새 마감을 만들지 않는다. 설치만 요청받았을 때는 TASK나 제작 작업을 시작하지 않는다.

- 현재 작업: 원문 또는 원문 위치, 요청 변경 사항, 범위·예산, 현재 단계와 다음 행동.
- 요구사항 → 설계/작업 → 실제 검증의 연결. 기존 기록·ID는 유지하고 변경분을 구분한다.
- 각 리뷰: 읽은 원문·산출물 경로와 기준 상태, 검토 방식, 판정과 발견 사항, 수정·재확인 근거.

이미 승인된 작업은 단계마다 재승인을 받지 않는다. 파일·도구로 확인할 수 있는 사실은 조사하고, 결과를 바꾸는 중요한 사용자 결정만 묻는다. 그 결정이나 차단 결함에 의존하지 않는 작업은 계속한다.

## 리뷰와 단계 전환

리뷰는 가능한 경우 작성자와 다른 읽기 전용 서브에이전트에 맡긴다. 원문·현재 산출물의 실제 경로, 관련 요구사항 ID, 변경 범위, 실행 근거와 질문을 전달한다. 리뷰어는 요약만 믿지 않고 해당 파일을 직접 읽으며, 검토한 기준 상태를 기록한다. Git이면 commit과 관련 working diff, 비 Git이면 해당 파일의 확인 시점·변경 내역처럼 상태를 식별할 근거를 쓴다. 리뷰 중 대상이 바뀌면 변경된 부분을 재확인한다.

| 판정 | 의미와 주 작업자의 행동 |
| --- | --- |
| PASS | 해당 검토 범위에 차단 사항이 없고 판정 근거가 있음. 유효한 산출물을 다음 단계로 전달한다. |
| WARN | 비차단 제안이나 검토 한계가 있음. 영향과 처리 여부를 남기고 진행한다. |
| FAIL | 필수 동작 결함 또는 단계 진행에 필요한 결정·근거가 빠짐. 그 항목에 의존하는 후속 작업과 완료 판정을 보류한다. |

발견에는 ID, 관련 요구사항, 위치·발생 조건·영향, 차단 여부를 적는다. 미확인은 확정 결함과 구분한다. 필요한 원문·실행 근거가 없는데 누락 없음·실행 성공으로 판정하지 않는다. 코드만 검토하라는 요청이면 판정 범위를 코드 검토로 제한하고 실행 여부를 따로 적는다.

주 작업자는 중요한 발견마다 `수정 위치 / 원래 재현 조건의 재확인 / 결과 / 확인자`를 남긴다. 수정과 영향 부분만 재확인하며 전체 리뷰를 관성적으로 반복하지 않는다. 작성자만 재검증했으면 이전 리뷰의 PASS를 최신 결과처럼 바꾸지 말고 독립 재리뷰 미실행을 적는다. 재현과 직접 관련된 확인 없이 발견을 닫지 않는다.

서브에이전트를 사용할 수 없으면 자체 점검으로 진행하고 독립 리뷰 미실행을 명시한다. 요구사항이나 인터페이스가 바뀌면 영향을 받는 설계·구현·검증·리뷰만 다시 연다. 최종 완료는 현재 필수 요구사항의 실제 근거와 미해결 차단 사항으로 판단한다. 리뷰의 PASS나 테스트 개수만으로 완료를 선언하지 않는다.

## 시간과 범위

사용자 지정 예산·마감과 기존 진행 기록을 우선한다. 별도 지시가 없는 실제 개발의 기본 예산은 180분이다. 시작할 때 실제 시계로 시작·마감·시간대를 기록하고 재개해도 초기화하지 않는다. 시계를 확인할 수 없으면 시각을 지어내지 않는다.

기본 예산에서 요구사항·아키텍처와 두 짧은 리뷰는 첫 20분 안에 정리한다. 60분까지 핵심 흐름을 실행하고, 130분부터 검증·개발 리뷰와 중요한 수정에 집중하며, 마지막 15분은 최종 실행·사용법·인계에 남긴다. 다른 예산이면 비례 조정한다. 일찍 끝나면 바로 인계하며 고정 대기하지 않는다.

핵심 실행이 늦어지면 막힌 원인, 남은 필수 항목, 가장 작은 실행 경로를 재평가한다. 부가 기능을 미루고 검증·인계 시간을 지킨다. 필수 범위·성공 기준을 바꾸려면 사용자 결정을 받으며, 임의로 삭제하거나 mock 결과로 대체하지 않는다. 사용자가 정한 하드 마감에는 완료·미완료와 재현 방법을 남겨 인계한다. 별도 하드 마감이 없는 기본 예산은 재계획 기준이며, 초과 사실과 남은 일을 알리고 완료를 꾸며내지 않는다.

## 모델 활용

아래는 사용 가능한 에이전트 도구에서 역할을 선택할 때의 권장값이다. 별도 역할 TOML은 설치하지 않으며, 이 문서가 모델을 강제로 전환하지는 않는다. 현재 주 모델·전역 설정·사용자의 명시적 선택을 유지한다.

| 작업 | 모델 | effort |
| --- | --- | --- |
| 좁은 사실 추출·로그 분류 | GPT-6 Luna (`gpt-6-luna`) | low |
| 조사·탐색·명확한 구현·작은 실험 | GPT-6 Luna (`gpt-6-luna`) | medium |
| 주 작업·아키텍처·통합·세 단계의 리뷰 | GPT-6.1 Sol (`gpt-6.1-sol`) | medium |
| 모호한 디버깅·위험한 변경 | GPT-6.1 Sol (`gpt-6.1-sol`) | high |

문제에 맞는 역할로 바로 배정한다. 값싼 모델부터 순서대로 거치거나 고정 병렬 수를 두지 않는다. 모델·effort 지정 기능이 없으면 현재 사용 가능한 설정으로 수행하고 실제 사용 모델과 권장값을 혼동하지 않는다. 지정 모델을 사용할 수 없으면 한계를 알리고 사용자에게 이미 허용받은 대안만 사용한다. 선택에 막히지 않는 주 작업은 계속한다.

## 병렬 작업과 근거

독립적인 읽기 전용 조사는 원본을 공유할 수 있다. 쓰기 실험은 별도 worktree 또는 필요한 파일만 복사한 임시 폴더에서 수행한다. 병렬 작업 전 개발 스킬의 [격리 절차](.agents/skills/gsp-development/references/parallel-work.md)를 읽는다. 담당 파일·실제 cwd·기준 상태·출력·환경·포트·완료 기준을 명시하고, 한 명의 통합 담당자만 검증된 변경을 반영한다.

원본의 미커밋 변경과 다른 작업자의 수정을 보존한다. 실제 실행·정적 검사·모의 결과를 구분하고 실행하지 않은 검증을 성공으로 표시하지 않는다. 외부 스킬을 기본으로 추가하지 않는다. 프로젝트·플랫폼 지침과 사용자가 허용한 작업 범위를 따른다.
<!-- GAMJAGOON-SKILLS-PACK:END -->
