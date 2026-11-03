# 기존 프로젝트의 GSP 전환 문서 정리 스킬

> 이후 사용자 요청으로 이 스킬을 팩에도 포함했다. 배포 원본은 [.agents/skills/gsp-adopt/SKILL.md](../.agents/skills/gsp-adopt/SKILL.md)이며 [패키징 변경·검증](bundle-gsp-adopt.md)을 참조한다. 아래는 최초 개인 스킬 작성과 CodeGraph 보완의 기록이다.

- 리비전: r4
- 현재 단계: CodeGraph 우선 조사·누락 인덱스 생성 보완 완료. CLI 실행 검증과 해당 변경의 독립 리뷰 PASS.
- 산출물: [gsp-adopt/SKILL.md](/home/minjae/.codex/skills/gsp-adopt/SKILL.md).
- 목적: 기존 코드와 흩어진 자료에서 근거를 수집해 향후 GSP 개발의 기준 문서 세 개를 정리한다.
- 범위: 요구사항·현재 아키텍처·작업 계획의 정리와 인계. 조사에 필요한 로컬 CodeGraph 인덱스 생성·갱신은 포함하며 GSP/도구 설치와 실제 기능 구현은 수행하지 않는다.
- 이전 초안: 의도를 잘못 이해해 작성했던 `implement-and-report`와 `gsp-setup`은 활성 스킬 경로에서 제거했다. 이전 초안은 로컬 작업 기록에만 보존한다.
- 미해결 사용자 결정: 없음.

## 목차

- [원문과 완료 기준](#원문과-완료-기준)
- [스킬 동작](#스킬-동작)
- [검증](#검증)
- [독립 리뷰](#독립-리뷰)
- [CodeGraph 조사 보완](#codegraph-조사-보완)
- [사용법과 범위](#사용법과-범위)

## 원문과 완료 기준

> 그게 아니라 설치는 다른데서 하는거고, 내가 하고싶은건 gsp 로 개발되지 않았던 프로젝트에서 gsp로 개발할 수 있게 프로젝트를 파악하고 요구사항, 아키텍처, Task 이렇게 3개를 세팅하는 스킬을 의미하는거야 아마 저런 정보들이 흩어져 있겠지

| ID | 기준 | 확인 방법 |
| --- | --- | --- |
| C1 | 기존 코드·테스트·설정·흩어진 문서에서 근거를 수집하고 사실·의도·추정·충돌을 구분한다 | 기존 프로젝트 예제의 문서와 소스 대조 |
| C2 | 요구사항·아키텍처·Task 세 문서를 안정적인 ID와 근거로 연결한다 | 세 문서의 링크·추적성 확인 |
| C3 | 코드 존재나 과거 완료 표시를 현재 검증 완료로 격상하지 않고, 중요한 미확정 의도만 질문한다 | 오래된 완료 표시와 문서/코드 불일치 사례 확인 |
| C4 | 문서 준비 범위에서 마치며 설치·구현·HTML 생성·기존 파일 훼손이 없다 | 허용 변경 경로와 전후 해시 확인 |
| C5 | 독립 스킬로 배치하고 형식·실제 문서 산출·독립 리뷰를 구분해 확인한다 | validator, 격리 평가, reviewer 결과 |
| C6 | 코드 조사 전에 CodeGraph 인덱스를 확인하고 없으면 생성한 뒤 실제 질의한다 | 초기 미색인 프로젝트의 init·status·explore 실행 |
| C7 | 대상 root·최신성·부분 실패를 확인하고 필요 시 sync한다 | 변경 탐지·sync·새 함수 질의 확인 |
| C8 | 로컬 색인 외에 hook·전역 설정·구현을 추가 변경하지 않는다 | Git metadata 및 소스 해시 보존 확인 |

작은 지침 스킬 작성이므로 별도 제품 요구사항·설계·개발 단계 문서는 만들지 않고 이 문서에 작성 기준과 검증 결과를 모았다. 이는 스킬을 실행할 대상 프로젝트의 세 문서를 대신하지 않는다.

## 스킬 동작

1. 대상 프로젝트의 root·지침·변경 상태를 확인하고, CodeGraph 인덱스를 생성·갱신한 뒤 실제 질의로 진입점과 구조를 조사한다.
2. 요구사항의 출처와 현재 동작을 대조한다. 구현된 동작을 자동으로 승인된 요구사항으로 취급하지 않는다.
3. 실제 컴포넌트·인터페이스·흐름을 아키텍처로 정리하고, 확인된 구조와 제안을 구분한다.
4. 과거 작업 기록과 현재 근거를 대조해 미완료 구현·검증 공백·후속 결정을 Task로 연결한다.
5. 사용 가능한 GSP 단계 지침과 리뷰 규칙을 적용한다. 사용할 수 없는 기능은 설치하지 않고 한계를 밝힌다.
6. 세 문서의 근거·추적성·미결정·다음 작업을 인계하고 끝낸다.

기본 위치는 `spec/requirement.md`, `spec/architecture.md`, `spec/tasks.md`다. 사용자 지정 경로와 이미 유효한 정본이 있으면 우선 활용한다. 기존 내용을 덮어쓰거나 문서를 강제로 이동하지 않는다. 문서는 사용자 언어의 Markdown으로만 작성한다.

## 검증

| 검사 | 결과 | 증거 범위 |
| --- | --- | --- |
| skill-creator `quick_validate.py` | PASS | 이름·frontmatter·기본 형식 검사 |
| 첫 기존 프로젝트 문서 산출 평가 | FAIL — F1/F2/F3 확인 | 세 문서는 작성했으나 ID 유지·출처·대상 정보 경계에 문제가 있음 |
| 스킬 보완 후 문서 재평가 | PASS | 기존 R10–R12·T7–T8 유지, 출처 대조, 원본 7파일 보존, 추가 파일은 세 Markdown뿐 |
| 독립 리뷰 | PASS — F1/F2/F3 종결 | 스킬 계약과 단일 예제의 문서 산출물에 한정한 development 검토 |

평가자는 `$gsp-adopt`를 사용해 한국어 세 문서를 작성한다. 원본 파일 수정·테스트 실행·기능 구현·설치·추가 agent 위임은 평가 범위에서 금지했다. 따라서 평가의 검증 근거는 실제 문서 산출과 정적 근거 대조이며, 예제 프로그램의 실행 성공을 뜻하지 않는다.

## 독립 리뷰

native `gsp-reviewer`가 첫 평가의 아래 결함을 직접 확인했다. 첫 평가 결과와 이전 다른 작업의 PASS를 최종 성공으로 재사용하지 않는다.

| ID | 관련 기준 | 첫 산출물 문제와 영향 | 보완·재확인 상태 |
| --- | --- | --- | --- |
| F1 | C2 | 기존 R10–R12를 R1–R3로 재번호해 원래 ID를 사용하는 추적성을 약화함 | 스킬에 ID 보존 명시. r2 세 문서에서 원 ID와 추적성 유지 확인 — 독립 reviewer 종결 |
| F2 | C1·C2 | 세 문서의 expense.py 줄 인용이 실제 위치와 다름 | 스킬에 출처 검증 명시. 원본 함수·진입점과 r2 인용 대조 일치 — 독립 reviewer 종결 |
| F3 | C1·C4 | 다른 프로젝트의 평가 세션 경로를 대상 프로젝트의 작업 기록 기준으로 포함함 | 스킬에 정보 경계 명시. r2 외부 경로 제거 및 향후 담당자 미지정 상태 확인 — 독립 reviewer 종결 |

첫 산출물은 세션의 `evaluation-r1/`에 보존했다. 수정된 스킬로 같은 평가자가 영향을 받은 세 문서를 다시 확인하고, 독립 리뷰어가 현재 원본과 대조한다.

최종 native `gsp-reviewer`(`gpt-6.1-sol / medium`) 판정은 **PASS**다. 스킬과 r2 문서 3개 해시, 예제 원본 7파일 해시, 이 저장소의 기존 13파일 해시를 독립 확인했다. 추가 파일은 세 Markdown 문서뿐이었다. 첫 결과의 FAIL은 수정 이력으로 남긴다.

이는 스킬과 한 예제의 정적 문서 작성 검증이다. 일반 프로젝트 전체의 성공이나 예제 프로그램의 실행 성공을 보증하지 않는다. 예제 문서의 요구사항·아키텍처·Task native 단계 리뷰는 수행되지 않았고 문서에도 한계를 명시했다. 이번 스킬 검토를 그 세 단계 리뷰 실행으로 바꾸어 기록하지 않는다.

근거: [형식·행동 검증 기록](../.gsp-work/sessions/session-o834hzzf/adopt-verification.md), [독립 리뷰](../.gsp-work/sessions/session-o834hzzf/adopt-reviewer.md), [최종 요구사항 예제](../.gsp-work/sessions/session-o834hzzf/evaluation-r2/requirement.md), [최종 아키텍처 예제](../.gsp-work/sessions/session-o834hzzf/evaluation-r2/architecture.md), [최종 Task 예제](../.gsp-work/sessions/session-o834hzzf/evaluation-r2/tasks.md).

## CodeGraph 조사 보완

추가 원문:

> 보안해줘 index가 없다면 인덱스를 생성하고 그다음 조사하도록

보완 요청으로 해석해 코드 조사 전에 `status → 필요한 init/sync → status → 실제 explore 질의`를 수행하도록 추가했다. 단순 `.codegraph` 폴더 유무가 아닌 실제 초기화 상태와 대상 프로젝트를 확인한다. 코드 구조를 CodeGraph로 먼저 파악한 뒤 문서·설정·지원하지 않는 영역은 필요한 파일 검색으로 보완한다.

CodeGraph 명령과 동작은 설치된 1.6.1의 help·소스와 [공식 저장소](https://github.com/colbymchenry/codegraph)를 확인했다. 현재 버전에서 `init --yes`는 watcher가 비활성화된 Git 환경에 hook을 설치할 수 있다. 스킬은 이를 무조건 사용하지 않고 sync 방식 질문에서 수동 sync를 선택하도록 한다. 상태 확인이 상위 저장소의 인덱스로 해석되는 경우와 `.codegraph-wsl` 같은 별도 색인 경로도 확인한다.

| 검사 | 실제 결과 | 증거 범위 |
| --- | --- | --- |
| 새 임시 Git 프로젝트의 status | exit 0이지만 initialized=false | 실제 CLI 실행 |
| init과 수동 sync 선택 | 2 files / 5 nodes / 6 edges, exit 0 | 실제 색인 생성 |
| 생성 후 status와 explore | 대상 root 일치, complete, pending 0; run/total 코드와 호출부 반환 | 실제 코드 질의 |
| fixture 코드 2파일 의도적 변경 후 sync | modified=2 탐지, sync 후 pending 0, 새 net_total 소스·호출부 반환 | 실제 갱신·질의 |
| 소스와 Git metadata/hooks 비교 | init/query는 원본 4파일 보존; sync도 시험자가 의도한 fixture 변경 외 수정 없음 | 해시 비교 |
| 수정 스킬 validator | exit 0, `Skill is valid!` | 형식 검사 |
| CodeGraph 보완 독립 리뷰 | PASS — C6–C8 | 별도 복사본에서 init·status·explore 독립 실행; 원본 4파일 보존 |

native `gsp-reviewer`(`gpt-6.1-sol / medium`)의 표적 development 리뷰는 **PASS**이며 확정 결함과 미해결 결정은 없다. 검토한 스킬 SHA256은 `b222e4768e18540c2d38ac06d3db34e6a30ac50090a98fb52497c59943f13120`이다. 리뷰어는 격리한 별도 복사본에서 미색인 상태 확인 → init → complete/pending 0 확인 → run/net_total/total 실제 질의를 수행했다. Git 환경의 PTY 선택과 sync 경로는 저자 실행 기록 및 설치된 소스 대조로 확인했으며 독립 재실행으로 표시하지 않는다. 상세 결과: [CodeGraph 독립 리뷰](../.gsp-work/sessions/session-o834hzzf/codegraph-reviewer.md).

실제 명령·출력: [CodeGraph 검증 기록](../.gsp-work/sessions/session-o834hzzf/codegraph-verification.md), [sync 로그](../.gsp-work/sessions/session-o834hzzf/codegraph-sync.log). CLI 검증이며 MCP 경로, 대규모 저장소의 속도 개선, 모든 언어와 실패 복구는 미검증이다. 프로그램 자체를 실행한 증거는 아니다. 도구 부재·초기화 실패 시 필수 단계를 건너뛴 조사 성공으로 표시하지 않도록 했다.

## 사용법과 범위

대상 프로젝트에서 다음과 같이 요청한다.

```text
$gsp-adopt
이 프로젝트의 코드와 흩어진 문서를 조사해서
GSP로 개발을 이어갈 요구사항, 아키텍처, Task 세 문서를 정리해줘.
```

이번 작업은 개인 스킬 생성이며 이 저장소 자체의 세 기준 문서를 재구성하라는 요청으로 확대하지 않았다. 기존 GSP 스킬·installer·전역 설정은 변경하지 않았다.

[세션 기록](../.gsp-work/sessions/session-o834hzzf/work.md)은 로컬 Git 제외 대상이며 다른 checkout에서는 unavailable일 수 있다.
