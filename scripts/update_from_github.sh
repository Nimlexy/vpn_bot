#!/usr/bin/env bash
set -euo pipefail

# Simple updater: clones/updates a GitHub repo to SRC_DIR, syncs to DEST_DIR (keeps .env), rebuilds Docker

usage() {
  cat <<USAGE
Usage:
  $0 --repo REPO_URL [--branch BRANCH] [--src /opt/vpn_bot_src] [--dest /opt/vpn_bot]

Environment variables:
  GIT_TOKEN   Optional. Personal Access Token for private repos (https). Example: ghp_...  
              If provided and REPO_URL is https://github.com/..., the URL will be rewritten to include the token.

Examples:
  $0 --repo https://github.com/yourname/vpn_bot.git --branch main
  GIT_TOKEN=xxxxx $0 --repo https://github.com/yourname/vpn_bot.git --branch main
USAGE
}

REPO_URL=""
BRANCH="main"
SRC_DIR="/opt/vpn_bot_src"
DEST_DIR="/opt/vpn_bot"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO_URL="$2"; shift 2 ;;
    --branch)
      BRANCH="$2"; shift 2 ;;
    --src)
      SRC_DIR="$2"; shift 2 ;;
    --dest)
      DEST_DIR="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown arg: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$REPO_URL" ]]; then
  echo "--repo is required" >&2
  usage
  exit 1
fi

echo "[+] Checking dependencies (git, docker compose)"
if ! command -v git >/dev/null 2>&1; then
  echo "Installing git..."
  apt-get update -y && apt-get install -y git
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "docker compose is required. Install compose plugin." >&2
  exit 1
fi

AUTH_REPO_URL="$REPO_URL"
if [[ -n "${GIT_TOKEN:-}" ]] && [[ "$REPO_URL" =~ ^https://github.com/ ]]; then
  AUTH_REPO_URL="https://${GIT_TOKEN}@github.com/${REPO_URL#https://github.com/}"
fi

mkdir -p "$SRC_DIR"
if [[ -d "$SRC_DIR/.git" ]]; then
  echo "[+] Updating source repo in $SRC_DIR"
  cd "$SRC_DIR"
  # Ensure remote is set to original REPO_URL (without token) for display
  if ! git remote get-url origin >/dev/null 2>&1; then
    git remote add origin "$REPO_URL"
  fi
  git remote set-url origin "$REPO_URL"
  # Fetch via AUTH_REPO_URL (may include token)
  git remote set-url --push origin "$AUTH_REPO_URL"
  git fetch --all --prune
  git checkout "$BRANCH" || git checkout -b "$BRANCH"
  git reset --hard "origin/$BRANCH"
else
  echo "[+] Cloning $REPO_URL into $SRC_DIR (branch $BRANCH)"
  rm -rf "$SRC_DIR"
  git clone --branch "$BRANCH" "$AUTH_REPO_URL" "$SRC_DIR"
fi

echo "[+] Syncing to destination $DEST_DIR (preserving .env)"
mkdir -p "$DEST_DIR"
rsync -a --delete \
  --exclude ".git" \
  --exclude ".github" \
  --exclude ".env" \
  --exclude "pgdata" \
  --exclude "__pycache__" \
  --exclude "*.pyc" \
  "$SRC_DIR/" "$DEST_DIR/"

echo "[+] Rebuilding and restarting containers"
cd "$DEST_DIR"
docker compose up -d --build

echo "[+] Done. Recent bot logs:"
docker compose logs -n 50 bot | cat || true


