#!/usr/bin/env bash
# gfch.skill 一键安装脚本
# 用法:
#   curl -fsSL https://raw.githubusercontent.com/ZMKC404/gfch.skill/main/install.sh | bash          # 装 gefei + chuhai 两个 skill
#   curl -fsSL https://raw.githubusercontent.com/ZMKC404/gfch.skill/main/install.sh | bash -s -- gefei   # 只装 gefei
#   curl -fsSL https://raw.githubusercontent.com/ZMKC404/gfch.skill/main/install.sh | bash -s -- chuhai  # 只装 chuhai
# 效果: 把选定 skill 装到本机已存在的 Agent skills 目录（zcode / claude / codex）
set -euo pipefail

REPO_RAW="${GFCH_REPO_RAW:-}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# 下载源列表：raw 直连失败时逐文件自动换镜像（jsdelivr fastly → ghproxy）
BASES=(
  "https://raw.githubusercontent.com/ZMKC404/gfch.skill/main"
  "https://fastly.jsdelivr.net/gh/ZMKC404/gfch.skill@main"
  "https://ghproxy.net/https://raw.githubusercontent.com/ZMKC404/gfch.skill/main"
)
[ -n "$REPO_RAW" ] && BASES=("$REPO_RAW")

# fetch <repo相对路径> <本地目标文件>：逐源重试，全失败返回 1
fetch() {
  local rel="$1" dest="$2" base
  for base in "${BASES[@]}"; do
    if curl -fsSL --retry 2 --max-time 20 "$base/$rel" -o "$dest" 2>/dev/null; then
      return 0
    fi
  done
  echo "❌ 下载失败: $rel（所有源均不可达，可设 GFCH_REPO_RAW 指定镜像）"
  return 1
}

SELECT="${1:-all}"
case "$SELECT" in
  gefei|chuhai|all) ;;
  *) echo "用法: install.sh [gefei|chuhai|all]（默认 all）"; exit 1 ;;
esac

install_skill() {
  local name="$1"; shift
  local refs=("$@")
  echo "⬇️  下载 $name ..."
  mkdir -p "$TMP/$name/references" "$TMP/$name/assets"
  fetch "skills/$name/SKILL.md" "$TMP/$name/SKILL.md" || exit 1
  for f in "${refs[@]}"; do
    fetch "skills/$name/references/$f.md" "$TMP/$name/references/$f.md" || exit 1
  done
  fetch "skills/$name/assets/style-checklist.md" "$TMP/$name/assets/style-checklist.md" || exit 1
  if ! grep -q "^name: $name" "$TMP/$name/SKILL.md" 2>/dev/null; then
    echo "❌ $name/SKILL.md 校验失败，安装中止"; exit 1
  fi

  local targets=()
  [ -d "$HOME/.zcode" ]  && targets+=("$HOME/.zcode/skills/$name")
  [ -d "$HOME/.claude" ] && targets+=("$HOME/.claude/skills/$name")
  [ -d "$HOME/.codex" ]  && targets+=("$HOME/.codex/skills/$name")
  if [ ${#targets[@]} -eq 0 ]; then
    targets=("$HOME/.claude/skills/$name")
  fi
  for t in "${targets[@]}"; do
    mkdir -p "$(dirname "$t")"
    rm -rf "$t"
    cp -R "$TMP/$name" "$t"
    echo "✅ 已安装: $t"
  done
}

GEFEI_REFS=(titles voice-and-structure tech-writing data-discipline community-cta anti-ai-flavor)
CHUHAI_REFS=(skeleton headlines emphasis-and-data voice action-lists anti-ai-flavor)

if [ "$SELECT" = "gefei" ] || [ "$SELECT" = "all" ]; then
  install_skill gefei "${GEFEI_REFS[@]}"
fi
if [ "$SELECT" = "chuhai" ] || [ "$SELECT" = "all" ]; then
  install_skill chuhai "${CHUHAI_REFS[@]}"
fi

echo ""
echo "完成。新开会话后直接说人话即可触发，例如："
echo '  gefei：「按哥飞的口吻写一篇我网站被收录的复盘」「帮我评一下这个站的 SEO」'
echo '  chuhai：「把这份播客笔记拆解成一篇出海创业指南体的文章」'
