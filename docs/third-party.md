# 선택 외부 스킬 출처

확인일: 2026-10-30. 이 저장소는 외부 스킬 원문을 동봉하지 않는다. 선택 설치 시에만
GitHub의 고정 커밋에서 필요한 파일을 내려받는다. 설치 자체는 해당 지침을 실행하거나
스킬이 요구하는 프로그램을 설치하지 않는다.

| 항목 | 고정 커밋과 경로 | 라이선스 근거 |
| --- | --- | --- |
| frontend-design | [Anthropic](https://github.com/anthropics/skills/tree/ca45fc496a3436251f191354091d557da31c15b5/skills/frontend-design) | [Apache-2.0](https://github.com/anthropics/skills/blob/ca45fc496a3436251f191354091d557da31c15b5/skills/frontend-design/LICENSE.txt) |
| systematic-debugging | [Superpowers](https://github.com/obra/superpowers/tree/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/systematic-debugging) | [MIT](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/LICENSE) |
| verification-before-completion | [Superpowers](https://github.com/obra/superpowers/tree/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/verification-before-completion) | [MIT](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/LICENSE) |
| pdf | [OpenAI legacy skill](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/pdf) | [Apache-2.0](https://github.com/openai/skills/blob/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/pdf/LICENSE.txt) |

OpenAI `skills` 저장소의 [고정 README](https://github.com/openai/skills/blob/49f948faa9258a0c61caceaf225e179651397431/README.md)는 deprecated 상태이며
현재 예제를 `openai/plugins`로 안내한다. 이 카탈로그의 `pdf`는 라이선스가 확인된
legacy 버전으로 명시적으로 고정한 것이며 최신 플러그인 동작을 뜻하지 않는다.

Vercel의 [web-design-guidelines](https://github.com/vercel-labs/agent-skills/tree/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/web-design-guidelines)는
해당 커밋에서 라이선스 파일을 찾지 못해 원본 링크만 제공한다. 이 결과는 다른 허가의
존재 여부를 판정하지 않는다. 자동 다운로드 카탈로그를 변경하려면 원본 조건을 다시 확인한다.

Anthropic의 문서용 스킬을 모두 같은 라이선스로 가정하지 않는다. 이 팩에는 공개 사용
조건을 확인한 `frontend-design`만 선택 설치 대상으로 포함한다.

## 설치 기록과 통신

- `.gamjagoon-skills-pack/skills-lock.json`은 저장소·전체 커밋·경로·라이선스·파일 해시를 기록한다.
- 다운로드는 `api.github.com`과 `raw.githubusercontent.com`의 공개 소스에 GET 요청을 보낸다.
- 로컬 프로젝트의 코드·TASK·대화·인증 토큰을 요청에 포함하지 않는다.
- GitHub 공개 API의 요청 제한이나 네트워크 오류가 생기면 설치를 실패로 보고한다.
- Git blob 비교는 고정 커밋의 바이트와 일치하는지 확인한다. 스킬 동작의 품질이나 안전성을 증명하지 않는다.
