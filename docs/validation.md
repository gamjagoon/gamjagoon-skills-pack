# 검증 기록

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
