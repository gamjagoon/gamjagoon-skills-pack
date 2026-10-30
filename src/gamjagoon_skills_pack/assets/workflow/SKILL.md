---
name: timeboxed-workflow
description: 제한된 실제 개발 시간 안에 원문 요구사항, 설계, 구현과 검증을 추적하는 작업에 사용합니다.
---

# 제한 시간 개발 워크플로

사용자의 원문과 `TASK.md`를 기준으로 필수 요구사항을 빠짐없이 추적한다. 실제 제작 시간과 질의응답·제출 시간을 구분하고, 시작과 마감 시각을 모르면 임의로 정하지 않는다. 사용자가 범위와 중요한 미결정을 판단하도록 필요한 근거를 제시한다. 이미 승인된 범위는 반복 허락 없이 진행한다.

현재 단계에 해당하는 문서만 읽는다. 단계는 상황에 맞게 반복할 수 있다.

- 시작과 시간 확인: [start](references/start.md)
- 원문 요구사항과 완료 기준: [requirements](references/requirements.md)
- 사람의 범위 검토: [requirements-review](references/requirements-review.md)
- 간단한 설계와 실행 작업: [design-tasks](references/design-tasks.md)
- 통합 계획의 독립 검토: [plan-review](references/plan-review.md)
- 위험한 의존성의 작은 실험: [feasibility](references/feasibility.md)
- 점진적 구현: [implement](references/implement.md)
- 읽기 전용 구현 검토와 수정: [implementation-review](references/implementation-review.md)
- 실제 결과 확인: [verify](references/verify.md)
- 사용자의 직접 실행과 인계: [handoff](references/handoff.md)

리뷰는 지원되는 환경에서 읽기 전용 `gsp-reviewer`를 사용할 수 있다. 지원되지 않으면 동일한 자료와 지시를 별도의 읽기 전용 리뷰 대화에 전달한다. 설치나 정적 검사는 실제 에이전트 실행의 증거가 아니다. 작업 성격에 맞게 확인하며, 실행하지 않은 검증을 성공으로 기록하지 않는다.
