# Codex CLI 줄바꿈 프로필

## 프로젝트에 적용

```bash
gsp keyboard /path/to/project --dry-run
gsp keyboard /path/to/project
```

- Enter / Ctrl+J: 줄바꿈
- Alt+Enter: 전송
- Ctrl+Enter: 터미널이 별도 키로 전달하는 경우 전송
- 기존 Ctrl+S 기록 검색 등 다른 단축키는 그대로 유지

설정 파일은 프로젝트의 `.codex/config.toml`이다. 현재 작업 중인 Codex CLI를 종료하고
해당 프로젝트에서 다시 실행한다. 프로젝트 신뢰 여부를 묻는 경우 실제 작업 폴더를
확인한다. 이 설치기는 신뢰 상태나 글로벌 설정을 변경하지 않는다.

처음에는 짧은 두 줄을 입력하고 Enter가 줄바꿈하는지 확인한다. 그다음 Alt+Enter의
전송을 확인한다. Ctrl+Enter를 일반 Enter와 구분하지 못하는 터미널에서는 Ctrl+Enter도
줄바꿈으로 전달될 수 있으므로 Alt+Enter를 사용한다. 웹 터미널이 Alt+Enter까지 가로채면
설정만으로 키 전달을 보장할 수 없다. 실제 환경에서 확인 가능한 입력 방식을 사용한다.

## 수동 설정

Codex CLI 0.165.0에서 확인한 형식이다. 기존 섹션이 있으면 해당 항목을 수정하며,
같은 TOML 섹션을 중복 추가하지 않는다.

```toml
[tui.keymap.composer]
submit = ["alt-enter", "ctrl-enter"]

[tui.keymap.editor]
insert_newline = ["enter", "ctrl-j", "shift-enter"]
```

`insert_newline`은 `composer`가 아닌 `editor` 섹션에 속한다. Ctrl+S는 기본 기록 검색의
다음 항목 키와 겹치므로 전송 키로 재사용하지 않는다. 변경한 항목의 키 목록은 해당
동작의 기본 목록을 대체한다. 승인 메뉴 등 다른 문맥의 Enter 동작까지 변경하는 설정은 아니다.

Enter 전송 방식으로 바꾸려면 다음 프로필을 적용할 수 있다. 이 명령은 이전 설정의
완전한 복원이 아니라 Enter 전송·별도 키 줄바꿈 프로필 적용이다.

```bash
gsp keyboard /path/to/project --enter submit
```

## 기존 설정 보존과 검증 범위

일반적인 TOML 섹션과 배열 표기에서는 입력 키만 수정하고, 수정 전후의 파싱 결과를
비교해 다른 설정 값이 달라지면 중단한다. 비표준적인 표기가 아니라도 inline table이나
quoted/dotted key 등 자동 편집기가 안전하게 다루지 못하는 표기는 그대로 보존하고
수동 설정을 안내할 수 있다. 모델·권한·MCP와 그 밖의 값은 재작성하지 않는다.

기존 파일의 백업은 `.gamjagoon-skills-pack/backups/` 아래에 남으며, 해당 로컬 상태
폴더는 `.gitignore`에 추가한다. 기본 init과 별개로 동작한다.

단위 검사와 실제 CLI의 설정 파싱은 실제 웹 터미널에서의 키 입력 검증과 다르다.
이 패키지는 IDE 확장 입력창이나 데스크톱 앱의 Enter 설정을 변경하지 않는다.

출처:

- [공식 TUI keymap 안내](https://learn.chatgpt.com/docs/config-file/config-basic#tui-keymap)
- [0.165.0 설정 schema](https://github.com/openai/codex/blob/rust-v0.165.0/codex-rs/core/config.schema.json)
- [0.165.0 keymap resolver와 기본 키](https://github.com/openai/codex/blob/rust-v0.165.0/codex-rs/tui/src/keymap.rs)
