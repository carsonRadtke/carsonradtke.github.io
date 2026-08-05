#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

export BUNDLE_USER_HOME="${BUNDLE_USER_HOME:-$PWD/.bundle}"
export BUNDLE_PATH="${BUNDLE_PATH:-$BUNDLE_USER_HOME/bundle}"
export BUNDLE_WITHOUT="${BUNDLE_WITHOUT:-}"

if ! bundle check >/dev/null 2>&1; then
  bundle install
fi

exec bundle exec jekyll serve --host 0.0.0.0 --livereload --drafts
