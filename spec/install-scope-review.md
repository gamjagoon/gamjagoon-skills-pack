# 설치 파일 범위 확인

> 이 기록은 gsp-adopt 포함 전 10파일 기준의 검증이다. 이후 사용자 요청으로 6스킬·11파일로 확장했으며, 현재 변경과 검증은 [gsp-adopt 팩 포함](bundle-gsp-adopt.md)에 기록한다.

- 현재 단계: 실제 설치 검증 및 독립 표적 리뷰 PASS. 확인 완료.
- 요청: “설치할 때 gsp관련 것만 설치되어여 하는데 여기의 필요없는 파일까지 포함 안되는지 확인해줘”.
- 결과: 현재 `install.sh`는 명시된 10개 경로만 설치한다. 불필요한 파일 유입은 재현되지 않았다. 소스 수정 없음.
- 범위: 현재 로컬 checkout의 installer와 설치 결과. 원격 배포본·다른 OS·Codex의 실제 agent 로딩은 이번 확인 범위 밖이다.
- 사용자 결정·확정 결함: 없음.

## 목차

- [설치되는 파일](#설치되는-파일)
- [복사되지 않는 자료와 예외](#복사되지-않는-자료와-예외)
- [실행 검증](#실행-검증)
- [독립 리뷰](#독립-리뷰)

## 설치되는 파일

| 구성 | 실제 경로 | 수 |
| --- | --- | --- |
| 프로젝트 지침 | `AGENTS.md`의 `GAMJAGOON-SKILLS-PACK` 관리 블록 | 1 |
| GSP 스킬 | `.agents/skills/gsp-{grilling,requirements,architecture,tasks,development}/SKILL.md` | 5 |
| 병렬 작업·세션 기록 지침 | `.agents/skills/gsp-development/references/{parallel-work,session-work}.md` | 2 |
| 리뷰 agent | `.codex/agents/gsp-reviewer.toml` | 1 |
| 로컬 상태 제외 규칙 | `.gitignore`에 `.gsp-backups/`, `.gsp-work/` 추가 | 1 |
| 합계 | 새 프로젝트 기준 일반 파일 | **10** |

[install.sh](../install.sh)의 `rels` 목록이 설치 대상을 한정한다. 디렉터리를 통째로 복사하거나 이름이 `gsp-`로 시작하는 모든 파일을 자동 수집하지 않는다. `AGENTS.md`는 관리 블록만 추출하고 `.gitignore`는 필요한 두 규칙만 구성하므로 원본 전체를 복사하지 않는다.

## 복사되지 않는 자료와 예외

- 소스의 `README.md`, `LICENSE`, `install.sh`, `spec/`, `tests/`, HTML, `.env`, `.git/`, `.serena/`, CodeGraph 인덱스, `.gsp-work/`, `.gsp-backups/`는 설치 payload가 아니다.
- 소스의 `.codex/config.toml`, 다른 agent·skill, 관리 스킬 폴더 안의 추가 파일도 복사되지 않는다.
- 대상 프로젝트에 원래 존재한 문서·설정·다른 스킬·세션 기록은 보존된다. “설치하지 않음”은 기존 파일을 지운다는 뜻이 아니다.
- 기존 파일을 교체하는 경우 `.gsp-backups/install.*/`에 **대상 프로젝트의 이전 파일**이 추가로 보존될 수 있다. 이것은 소스 저장소의 작업 자료가 유입된 것이 아니다. 새 빈 프로젝트에는 백업이 생성되지 않았다.
- 직전에 만든 [개인 gsp-adopt 스킬](/home/minjae/.codex/skills/gsp-adopt/SKILL.md)은 현재 팩의 설치 목록에 없다. 이번 확인 요청으로 배포 범위를 변경하지 않았다.

## 실행 검증

기준 HEAD는 `bd656b1eed3d7800b7162ce97ea4dec0e5081540`이며 기존 dirty 변경을 포함한 현재 파일을 검증했다. 원본을 수정하지 않고 `/tmp/gsp-install-scope-um0yucra`에 대상과 허용된 입력 파일만 복사한 시험용 소스를 분리했다. 별도의 새 제품 설계가 필요 없는 기존 기능 확인이므로 요구사항·설계·Task 문서를 새로 만들지 않았다.

| ID | 검사 | 실제 결과 | 증거 종류 |
| --- | --- | --- | --- |
| S1 | 현재 checkout에서 dry-run → 새 프로젝트 설치 | dry-run은 대상 생성 없음; 설치 후 정확히 10파일 | 실제 Bash CLI |
| S1 | AGENTS 관리 영역·gitignore·나머지 payload 내용 비교 | 관리 영역만 일치, 제외 규칙 2줄, 나머지 8파일 byte 일치 | 실제 파일 대조 |
| S1 | 시험용 소스에 불필요한 19개 경로와 관리 영역 밖 문자열 추가 후 설치 | 정확히 10파일; 추가 자료·문자열 유입 없음 | 합성 입력 + 실제 설치 |
| S2 | 재설치와 변경 없는 overwrite | 파일 집합·내용·mode 동일 | 실제 CLI 및 해시 대조 |
| S2 | 기존 자료 7종과 사용자 AGENTS/gitignore가 있는 대상에 설치 | 기존 7종 보존, 사용자 내용 유지, 교체한 두 파일만 백업 | 실제 CLI 및 해시 대조 |
| S2 | 대상 개발 스킬을 수정한 뒤 overwrite | 해당 파일 복구, 사용자 수정본 하나만 추가 백업, 다른 파일 보존 | 실제 CLI 및 해시 대조 |
| S3 | 현재 설치 목록과 개인 스킬 위치 대조 | gsp-adopt는 팩 미포함 | 정적 확인 |

총 설치 명령 9회가 exit 0으로 종료했다. 위 명령은 실제 설치 스크립트를 실행하며 실패 주입이나 installer mock을 사용하지 않는다. 불필요한 시험용 파일만 합성 자료다. 실제 사용자의 프로젝트에는 설치하지 않았다.

재현 스크립트: [verify_scope.py](../.gsp-work/sessions/session-install-scope-fqpe1538/verify_scope.py). 명령·출력·정확한 파일 집합: [result.json](../.gsp-work/sessions/session-install-scope-fqpe1538/result.json).

```bash
python3 .gsp-work/sessions/session-install-scope-fqpe1538/verify_scope.py \
  --source /home/minjae/ws/gamjagoon-skills-pack \
  --output /tmp/gsp-install-scope-result.json
```

## 독립 리뷰

native `gsp-reviewer`(`gpt-6.1-sol / medium`), mode `development`의 S1–S3 표적 리뷰는 **PASS**다. 확정 결함·필수 미검증·사용자 결정은 없다. 이전 legacy-removal PASS는 재사용하지 않았다.

리뷰어는 설치 목록 및 모든 쓰기 경로를 검토하고 허용된 입력만 새 임시 소스에 복사해 `verify_scope.py`를 독립 실행했다. 9개 설치 명령이 모두 exit 0, 새 파일 정확히 10개와 symlink 없음, 합성 잡파일 19개 미유입, 기존 자료 7종 보존 및 예상한 파일만 백업됨을 확인했다. 독립 fixture `/tmp/gsp-install-scope-9r5vikev`는 검증 후 제거했으며 저자 fixture·원본·보고서·세션은 변경하지 않았다.

제공한 소스 13개와 추가 검토 자료 5개의 실행 전후 해시를 확인했다. 검토 당시 보고서 해시는 `a69226a12471a1263720deb09410a75e8ed14642161d85228d42a30f1e81c9b8`, 검증 스크립트 해시는 `6de19866e3f8d75f1fe512ce927d2aec9ac1f32aae7f157b94a81c4aaf20c952`다. 이 단락은 이후 lead가 결과를 반영한 것이다.

Lead comment: 판정을 수용한다. 이번 확인으로 installer 변경은 필요하지 않다. 현재 로컬 설치본의 파일 범위 검증이며 원격 배포본·다른 OS·실사용 프로젝트 설치·Codex agent 로딩까지 검증했다는 의미는 아니다.

[세션 기록](../.gsp-work/sessions/session-install-scope-fqpe1538/work.md)과 연결된 검증 자료는 로컬 Git 제외 경로이며 다른 checkout에서는 unavailable일 수 있다.
