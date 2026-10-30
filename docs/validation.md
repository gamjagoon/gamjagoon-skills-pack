# 검증 기록

## v0.3.0 — 180분 기본 흐름과 프로젝트 역할 (2026-10-31)

- 단위·회귀 검사: PASS, **113개**. 여섯 역할의 모델·effort·읽기 전용 범위,
  누락·잘못된 TOML, 기본 180분, 사용자 역할 설정, 충돌·백업·재설치, 기존 TASK 보존을 확인했다.
- 전역 경로 보호 회귀 검사: PASS. 기본 Codex 홈과 사용자 지정 CODEX_HOME 자체를
  setup/init/keyboard/skills add의 대상으로 지정하면 dry-run과 실제 실행 모두 거부한다.
  임시 가짜 홈을 사용했으며 실제 사용자 전역 설정을 변경하지 않았다.
- Ruff check/format, git diff --check, wheel/sdist 빌드, 격리된 uv tool 설치: PASS.
  패키지에서 여섯 역할과 병렬·모델 참조 문서를 설치하고 재설치 변경 0을 확인했다.
- 공개 v0.2.0 아카이브 → 로컬 v0.3.0 wheel 업데이트: PASS. 충돌 사전 거부와
  dry-run 무변경, 교체 전 백업, 기존 135분 TASK·사용자 지침·주 모델 설정의 보존을 확인했다.
  독립 리뷰에서도 이전 소스의 240분 TASK를 유지하는 업데이트를 별도로 확인했다.
- 문서와 스킬 형식: PASS. 로컬 Markdown 링크, README 범위, skill-creator quick_validate 확인.
- worktree 예시: PASS. 임시 Git 저장소에서 detached worktree 생성과 허용 파일의
  dirty baseline 패치 전달을 실행했다. uv 가상환경·캐시·임시 파일·출력 분리 예시도 실행했다.
- 독립 코드 리뷰: 발견된 전역 Codex 루트 보호 누락과 dirty baseline 설명의 준비 단계
  누락을 수정하고 재검증했다. 수정 후 확인된 잔여 결함 없음.
- 설치 지침 행동 확인: PASS, 한 개의 작은 CSV CLI 과제. 독립 에이전트에 설치된 폴더와
  과제만 제공하자 추가 시간·시작 프롬프트 없이 180분 예산·시작/마감과 완료 기준을 기록하고,
  구현·다섯 CLI 사례 실행·사용법·인계를 완료했다. 별도 위임이 제한된 평가여서 독립 리뷰
  미실행을 정확히 기록했다. 실제 180분 장기 작업의 성과를 증명하는 검사는 아니다.

- 공개 v0.3.0 아카이브 설치: PASS. 임시 uv tools/cache와 새 폴더에서 버전, dry-run,
  기본 180분, 여섯 역할, 병렬·모델 참조, Enter 설정, doctor와 재설치 변경 0을 확인했다.
- Linux CI: PASS, Python 3.11/3.13 모두 테스트·형식 검사·빌드·격리 설치 성공.
  [v0.3.0 코드 검증](https://github.com/gamjagoon/gamjagoon-skills-pack/actions/runs/41105631391).

다음은 별도 검증 대상이다: 설치된 네이티브 역할의 실제 모델 호출 및 이용 가능성,
실제 CLI 키 입력, 장시간 병렬 에이전트 실행, Windows·macOS. 파일과 설정의 정적 검사를
이 동작들의 성공으로 해석하지 않는다. 아래는 이전 릴리스의 역사적 검증 기록이다.


검증일: 2026-10-30. 로컬 환경은 Linux/WSL2 x86_64, Python 3.13.14, uv 0.11.33이다.

| 검사 | 관찰 결과 |
| --- | --- |
| `uv run --frozen pytest -q` | PASS, 59개. dry-run, 기존 내용 보존, 충돌, 백업, 재설치, 링크 거부, 실패 복구·재시도, mocked 다운로드 무결성, 입력 키와 전역 경로 보호 포함 |
| Ruff check / format check | PASS |
| `uv build` | PASS, sdist와 wheel 생성 |
| 격리된 uv tool 설치·uvx 경로 | PASS, 임시 tools/bin/cache에서 설치 후 init/doctor/prompt/catalog/재설치 확인 |
| 패키지 내용과 로컬 Markdown 링크 | PASS, 패키지에서 로컬 캐시·환경 파일 제외와 문서 연결 확인 |
| skill-creator quick_validate | PASS, 프런트매터·스킬 형식 검사 |
| 독립 구현 리뷰 | PASS, 실패 후 빈 디렉터리가 재시도를 막는 결함을 수정하고 회귀 검사로 확인 |
| 프롬프트 forward check | PASS, 한 개의 가상 CSV 과제에서 요구사항과 미결정만 정리하고 사용자 리뷰 전 설계·구현을 시작하지 않음 |
| 선택 외부 스킬 실제 다운로드 | PASS, frontend-design / systematic-debugging / verification-before-completion / pdf를 임시 폴더로 받아 고정 커밋 blob과 라이선스·설치 기록 확인 |
| Codex CLI 입력 키 설정 파싱 | PASS, 설치된 0.165.0에서 features list로 설정 해석 확인. 실제 입력 키 전달은 별도 |
| 입력 키 추가 변경 독립 리뷰 | PASS, HOME/활성 전역 설정/같은 파일 충돌을 거부하고 다른 설정 값·기록 검색 키를 보존 |
| 공개 Git URL 설치 | PASS, d3c86c7e7ba83b4e30939c1f23d75123246d6c31을 임시 uv tools/bin/cache에 설치하고 init/keyboard/doctor/prompt 실행 |
| Linux GitHub Actions | PASS, 입력 키 추가 버전의 Python 3.11/3.13 검사·빌드·격리 설치. [d3c86c7 실행](https://github.com/gamjagoon/gamjagoon-skills-pack/actions/runs/41027264551) |

외부 스킬 다운로드 검증은 실제 공개 GitHub에 접근했으며 내려받은 스크립트를 실행하지 않았다.
mock 기반 검사와 실제 다운로드 검사는 서로 다른 근거다. forward check는 한 개의 요구사항 단계
사례에 한정하며, 모든 단계의 효과나 다른 과제에서의 성공을 증명하지 않는다.

다음은 실행하지 않았다.

- 실제 Codex 지침 탐색·서브에이전트 실행: NOT_RUN
- 실제 시험 웹 터미널의 Enter/Alt+Enter/Ctrl+Enter 전달: NOT_RUN
- 특정 시험환경·Windows·macOS 실행: NOT_RUN

## v0.2.0 이름으로 요청하는 설치

- 단위·회귀 검사: PASS, 68개. 통합 setup의 전체 구성, 재설치, dry-run, 전체 사전 검사,
  쓰기 실패 복구, 기존 입력 설정 유지, 빈 TASK 사전 거부를 포함한다.
- 공식 uv 0.11.33 설치기: PASS, 임시 unmanaged 디렉터리 설치. 실제 글로벌 셸 설정을 바꾸지 않았다.
- wheel·sdist 빌드와 격리된 uv tool setup: PASS. INSTALL.md와 llms.txt의 sdist 포함 확인.
- 독립 코드 리뷰: PASS. 설치 후 오류가 나던 빈 TASK 사례를 사전 거부하도록 수정했다.
- 이름만 제공한 독립 에이전트의 공개 소스 설치: PASS. 이전 대화·저장소 URL을 주지 않고
  `gamjagoon-skills-pack 설치해줘` 요청만 전달했다. 에이전트가 공개 GitHub 검색으로 소스를
  찾고 별도의 uv를 임시 설치한 뒤 v0.2.0을 새 폴더에 적용하고 설치 지침을 읽었다.
  생성된 16개 파일, 열 단계 참조, 읽기 전용 리뷰어와 입력 키를 별도로 확인했다.
- Git 없는 환경의 공개 아카이브 설치: PASS. 기본 coreutils만 유지한 PATH에서 v0.2.0을
  받아 setup 완료를 확인했다. 패키지 소스 트리를 대상 프로젝트에 복사하지 않았다.
- Linux CI: PASS, Python 3.11/3.13에서 [v0.2.0 코드 검사·빌드·설치](https://github.com/gamjagoon/gamjagoon-skills-pack/actions/runs/41029635639).

새 폴더는 아직 설치되지 않은 로컬 지침을 자동으로 읽을 수 없다. 따라서 이름으로
공개 저장소를 찾는 단계와, 설치 후 현재 대화에서 지침을 읽는 단계를 구분한다.
일반 검색엔진의 색인과 각 에이전트의 검색·실행 능력을 모든 환경에서 보장하지 않는다.
