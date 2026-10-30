#!/usr/bin/env bash
# Local workflow installer. Requires Bash and Linux/WSL coreutils + awk.
set -euo pipefail
start='<!-- GAMJAGOON-SKILLS-PACK:START -->'
end='<!-- GAMJAGOON-SKILLS-PACK:END -->'
dry_run=0 overwrite=0 target_arg= target_set=0
usage() {
    cat <<'HELP'
Usage: bash install.sh [--dry-run] [--overwrite] [TARGET]
Install the AGENTS.md managed block, four skills, and native gsp-reviewer agent locally.
TARGET defaults to the current directory. No downloads or model calls occur.
  --dry-run    Check conflicts and show changes without creating TARGET
  --overwrite  Back up and replace differing content; retire three legacy review skills
  --help       Show this help
Existing text outside the managed block and unrelated files are preserved.
Failed writes trigger best-effort rollback; concurrent edits are left intact.
HELP
}
fail() { printf 'Error: %s\n' "$*" >&2; exit 1; }
while (($#)); do
    case $1 in
        --dry-run) dry_run=1 ;;
        --overwrite) overwrite=1 ;;
        --help|-h) usage; exit 0 ;;
        --) shift; (($# <= 1)) || fail 'Only one TARGET is allowed'; if (($#)); then target_arg=$1; target_set=1; fi; break ;;
        -*) fail "Unknown option: $1" ;;
        *) ((target_set == 0)) || fail 'Only one TARGET is allowed'; target_arg=$1; target_set=1 ;;
    esac
    shift
done
((target_set)) || target_arg=$PWD
[[ -n $target_arg ]] || fail 'TARGET must not be empty'
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
# Inspect each original component before normalizing '..', including dangling links.
no_links() {
    local path=$1 part walk= rest
    [[ $path = /* ]] || path=$PWD/$path
    rest=${path#/}
    while [[ -n $rest ]]; do
        part=${rest%%/*}
        if [[ $rest = */* ]]; then rest=${rest#*/}; else rest=; fi
        [[ -n $part && $part != . ]] || continue
        walk=$walk/$part
        [[ ! -L $walk ]] || fail "Symlink path is not allowed: $walk"
    done
}
no_links "$target_arg"
target=$(realpath -ms -- "$target_arg")
[[ $target != / ]] || fail 'Refusing filesystem root'
for protected in "${HOME:-}" "${HOME:-}/.codex" "${CODEX_HOME:-}"; do
    [[ -n $protected ]] || continue
    [[ $target != "$(realpath -m -- "$protected")" ]] || fail "Refusing global target: $target"
done
[[ ! -e $target || -d $target ]] || fail 'TARGET must be a directory'
rels=(AGENTS.md
    .agents/skills/gsp-grilling/SKILL.md
    .agents/skills/gsp-requirements/SKILL.md
    .agents/skills/gsp-architecture/SKILL.md
    .agents/skills/gsp-development/SKILL.md
    .agents/skills/gsp-development/references/parallel-work.md
    .codex/agents/gsp-reviewer.toml
    .gitignore)
# Only these formerly managed files are retired; sibling files and directories stay.
retired_rels=(.agents/skills/gsp-requirements-review/SKILL.md
    .agents/skills/gsp-architecture-review/SKILL.md
    .agents/skills/gsp-development-review/SKILL.md)
all_rels=("${rels[@]}" "${retired_rels[@]}")
stage=$(mktemp -d)
lock= backup= success=0
changed=() retiring=() applied=() removed=() created_dirs=()
# All temporary replacement files live beside destinations for atomic rename.
replacement=
cleanup() {
    local status=$? i rel dest restore
    trap - EXIT INT TERM
    if ((success == 0 && (${#applied[@]} || ${#removed[@]}))); then
        printf 'Installation failed; attempting rollback of installer writes.\n' >&2
        for ((i=${#applied[@]}-1; i>=0; i--)); do
            rel=${applied[i]}; dest=$target/$rel
            if [[ -f $dest && ! -L $dest ]] && cmp -s -- "$dest" "$stage/new/$rel"; then
                if [[ -f $stage/old/$rel ]]; then
                    restore=$(mktemp -- "$(dirname -- "$dest")/.gsp-restore.XXXXXX") || continue
                    if cp -p -- "$stage/old/$rel" "$restore"; then mv -fT -- "$restore" "$dest" || true; fi
                    rm -f -- "$restore"
                else
                    rm -f -- "$dest" || true
                fi
            else
                printf 'Rollback preserved concurrently changed path: %s\n' "$dest" >&2
            fi
        done
        for ((i=${#removed[@]}-1; i>=0; i--)); do
            rel=${removed[i]}; dest=$target/$rel
            if ! (no_links "$dest") || [[ ! -d $(dirname -- "$dest") ]]; then
                printf 'Rollback preserved concurrently changed parent: %s\n' "$dest" >&2
                continue
            fi
            restore=$(mktemp -- "$(dirname -- "$dest")/.gsp-restore.XXXXXX") || continue
            # ln creates only an absent destination, including under a recreation race.
            if cp -p -- "$stage/old/$rel" "$restore"; then
                if ! ln -T -- "$restore" "$dest"; then
                    printf 'Rollback preserved concurrently recreated path or could not restore: %s\n' "$dest" >&2
                fi
            fi
            rm -f -- "$restore"
        done
    fi
    [[ -z $replacement ]] || rm -f -- "$replacement"
    if ((success == 0)); then
        [[ -z $backup ]] || printf 'Backups retained: %s\n' "$backup" >&2
        for ((i=${#created_dirs[@]}-1; i>=0; i--)); do rmdir -- "${created_dirs[i]}" 2>/dev/null || true; done
    fi
    [[ -z $lock ]] || rmdir -- "$lock" 2>/dev/null || true
    rm -rf -- "$stage"
    exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
mkdir -p -- "$stage/new" "$stage/old"
# Emit exact byte offsets; reject duplicates, reversed, nested, or partial markers.
block_offsets() {
    LC_ALL=C awk -v first="$start" -v last="$end" '
    BEGIN { pos=0 }
    { n=length($0)+1
      if (index($0,"GAMJAGOON-SKILLS-PACK:")) {
        if ($0==first && state==0) { begin=pos; state=1 }
        else if ($0==last && state==1) { finish=pos+n; state=2 }
        else bad=1
      }
      pos+=n
    }
    END { if (bad || state==1) exit 1; if(state==2) print begin,finish; else print "none" }
    ' "$1"
}
[[ -f $source_dir/AGENTS.md ]] || fail 'Bundled AGENTS.md is missing'
source_offsets=$(block_offsets "$source_dir/AGENTS.md") || fail 'Invalid bundled AGENTS markers'
[[ $source_offsets != none ]] || fail 'Bundled AGENTS managed block is missing'
read -r begin finish <<< "$source_offsets"
head -c "$finish" -- "$source_dir/AGENTS.md" | tail -c "+$((begin+1))" > "$stage/block"
# Validate all destination parents and types, including reserved backup location.
check_path() {
    local path=$1 walk part rest
    no_links "$path"
    walk=$path
    while [[ $walk != / ]]; do
        if [[ -e $walk ]]; then
            if [[ $walk = "$path" ]]; then
                [[ -f $walk ]] || fail "Expected regular file: $walk"
            else
                [[ -d $walk ]] || fail "Expected directory: $walk"
            fi
        fi
        walk=$(dirname -- "$walk")
    done
}
no_links "$target/.gsp-backups"
[[ ! -e $target/.gsp-backups || -d $target/.gsp-backups ]] || fail 'Backup path must be a directory'
for rel in "${rels[@]}"; do
    dest=$target/$rel
    check_path "$dest"
    # Explicitly guard global hardlink aliases; replacements use rename as well.
    for protected in "${HOME:-}/.codex/AGENTS.md" "${HOME:-}/.codex/config.toml" "${CODEX_HOME:-}/AGENTS.md" "${CODEX_HOME:-}/config.toml"; do
        [[ ! -e $dest || ! -e $protected || ! $dest -ef $protected ]] || fail "Destination aliases global configuration: $dest"
    done
    mkdir -p -- "$stage/new/$(dirname -- "$rel")" "$stage/old/$(dirname -- "$rel")"
    [[ ! -f $dest ]] || cp -p -- "$dest" "$stage/old/$rel"
    if [[ $rel = AGENTS.md ]]; then
        offsets=none
        [[ ! -f $dest ]] || offsets=$(block_offsets "$dest") || fail 'Malformed or duplicate target AGENTS markers'
        if [[ $offsets = none ]]; then
            if [[ -f $dest ]]; then
                cat -- "$dest" > "$stage/new/$rel"
                if [[ -s $dest ]]; then printf '\n\n' >> "$stage/new/$rel"; fi
            fi
            cat -- "$stage/block" >> "$stage/new/$rel"
        else
            read -r begin finish <<< "$offsets"
            size=$(wc -c < "$dest")
            ((finish <= size)) || finish=$size
            head -c "$finish" -- "$dest" | tail -c "+$((begin+1))" > "$stage/existing-block"
            if ! cmp -s -- "$stage/existing-block" "$stage/block" && ((overwrite == 0)); then
                fail 'Managed AGENTS block differs; use --overwrite to back up and replace it'
            fi
            { head -c "$begin" -- "$dest"; cat -- "$stage/block"; tail -c "+$((finish+1))" -- "$dest"; } > "$stage/new/$rel"
        fi
    elif [[ $rel = .gitignore ]]; then
        [[ ! -f $dest ]] || cat -- "$dest" > "$stage/new/$rel"
        if [[ ! -f $dest ]] || ! awk 'END {exit ($0!=".gsp-backups/")}' "$dest"; then
            if [[ -s $dest ]]; then printf '\n' >> "$stage/new/$rel"; fi
            printf '.gsp-backups/\n' >> "$stage/new/$rel"
        fi
    else
        [[ -f $source_dir/$rel && ! -L $source_dir/$rel ]] || fail "Missing bundled file: $rel"
        cp -- "$source_dir/$rel" "$stage/new/$rel"
        if [[ -f $dest ]] && ! cmp -s -- "$dest" "$stage/new/$rel" && ((overwrite == 0)); then
            fail "Managed file differs: $rel (use --overwrite to back up and replace it)"
        fi
    fi
    if [[ ! -f $dest ]] || ! cmp -s -- "$dest" "$stage/new/$rel"; then changed+=("$rel"); fi
done
for rel in "${retired_rels[@]}"; do
    dest=$target/$rel
    check_path "$dest"
    for protected in "${HOME:-}/.codex/AGENTS.md" "${HOME:-}/.codex/config.toml" "${CODEX_HOME:-}/AGENTS.md" "${CODEX_HOME:-}/config.toml"; do
        [[ ! -e $dest || ! -e $protected || ! $dest -ef $protected ]] || fail "Destination aliases global configuration: $dest"
    done
    if [[ -f $dest ]]; then
        ((overwrite)) || fail "Legacy review skill exists: $rel (use --overwrite to back up and retire it)"
        mkdir -p -- "$stage/old/$(dirname -- "$rel")"
        cp -p -- "$dest" "$stage/old/$rel"
        retiring+=("$rel")
    fi
done
for rel in "${changed[@]}"; do printf '%s %s\n' "$( ((dry_run)) && printf 'Would install' || printf 'Install')" "$target/$rel"; done
for rel in "${retiring[@]}"; do printf '%s %s\n' "$( ((dry_run)) && printf 'Would retire' || printf 'Retire')" "$target/$rel"; done
if ((dry_run)); then printf 'Dry run complete; no target files changed.\n'; success=1; exit 0; fi
if ((${#changed[@]} == 0 && ${#retiring[@]} == 0)); then printf 'Already installed; no changes.\n'; success=1; exit 0; fi
# Serialize cooperating installers even when TARGET does not yet exist.
lock_name=$(printf '%s' "$target" | cksum)
lock_candidate=/tmp/.gsp-install-${UID}-${lock_name%% *}.lock
mkdir -- "$lock_candidate" 2>/dev/null || fail "Installer lock exists: $lock_candidate (check for an active installer before removing it)"
lock=$lock_candidate
# Check every snapshot again under the lock before making any target changes.
for rel in "${all_rels[@]}"; do
    check_path "$target/$rel"
    if [[ -f $stage/old/$rel ]]; then
        [[ -f $target/$rel ]] && cmp -s -- "$stage/old/$rel" "$target/$rel" || fail "Concurrent change detected: $rel"
    else
        [[ ! -e $target/$rel ]] || fail "Concurrent creation detected: $rel"
    fi
done
no_links "$target/.gsp-backups"
ensure_dir() {
    local dir=$1
    [[ -d $dir ]] && return
    [[ ! -e $dir && ! -L $dir ]] || fail "Invalid directory: $dir"
    ensure_dir "$(dirname -- "$dir")"
    mkdir -- "$dir"
    created_dirs+=("$dir")
}
ensure_dir "$target"
# Back up every replacement and retirement before any managed file is changed.
for rel in "${changed[@]}" "${retiring[@]}"; do
    if [[ -f $stage/old/$rel ]]; then
        if [[ -z $backup ]]; then
            ensure_dir "$target/.gsp-backups"
            backup=$(mktemp -d -- "$target/.gsp-backups/install.XXXXXXXX")
        fi
        mkdir -p -- "$backup/$(dirname -- "$rel")"
        cp -p -- "$stage/old/$rel" "$backup/$rel"
    fi
done
for rel in "${retiring[@]}"; do
    dest=$target/$rel
    check_path "$dest"
    [[ -f $dest ]] && cmp -s -- "$stage/old/$rel" "$dest" || fail "Concurrent change detected: $rel"
    # Record intent before unlink so signal cleanup also covers that operation.
    # If unlink fails, the no-clobber restore leaves the existing path intact.
    removed+=("$rel")
    rm -- "$dest"
done
for rel in "${changed[@]}"; do
    dest=$target/$rel
    check_path "$dest"
    if [[ -f $stage/old/$rel ]]; then
        [[ -f $dest ]] && cmp -s -- "$stage/old/$rel" "$dest" || fail "Concurrent change detected: $rel"
    else
        [[ ! -e $dest ]] || fail "Concurrent creation detected: $rel"
    fi
    ensure_dir "$(dirname -- "$dest")"
    replacement=$(mktemp -- "$(dirname -- "$dest")/.gsp-write.XXXXXX")
    cat -- "$stage/new/$rel" > "$replacement"
    if [[ -f $stage/old/$rel ]]; then chmod --reference="$stage/old/$rel" -- "$replacement"; else chmod 644 -- "$replacement"; fi
    mv -fT -- "$replacement" "$dest"
    replacement=
    applied+=("$rel")
done
success=1
[[ -z $backup ]] || printf 'Backups: %s\n' "$backup"
printf 'Installed four skills, the native gsp-reviewer agent, and the managed AGENTS block.\n'
