# 병렬 작업 안내

설치된 워크플로의 [병렬 작업 참조 원본](../src/gamjagoon_skills_pack/assets/workflow/references/parallel-work.md)이 격리와 통합의 기준입니다. 프로젝트에서는 `.agents/skills/timeboxed-workflow/references/parallel-work.md`로 설치됩니다. 역할과 모델은 함께 설치되는 [모델 라우팅 참조](../src/gamjagoon_skills_pack/assets/workflow/references/model-routing.md)를 따릅니다.

읽기 전용 탐색·리뷰는 공유 저장소에서 수행할 수 있습니다. 쓰기 실험은 유효한 Git HEAD가 있으면 별도 worktree를 사용하고, dirty baseline은 검토한 경로별 패치와 명시적 파일 복사로 전달합니다. 비 Git/HEAD 없는 프로젝트는 허용 목록 복사본을 사용합니다. 원본의 현재 변경을 자동 commit/stash하거나 미추적 파일·비밀정보를 일괄 복사하지 않습니다.

각 할당에 목표·근거·소유 파일·실제 cwd·완료 기준을 명시합니다. 출력·환경·캐시·포트도 분리하고, 부모만 결과를 검토·통합한 뒤 최종 검증을 실행합니다. worktree는 보안 경계가 아니며 도구가 자동으로 해당 cwd를 사용하는 것도 아닙니다. 컨테이너는 기본 요구사항이 아닙니다.

실행 가능한 worktree·patch·허용 목록 복사 명령과 안전한 정리 절차는 참조 원본에 있습니다. 실패 근거를 보존하고 본인 소유 경로만 정리합니다. 설치 검사는 실제 서브에이전트 실행이나 통합 성공을 입증하지 않습니다.
