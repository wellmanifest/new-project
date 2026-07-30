#!/usr/bin/env bash
# Universal ticket scaffolder for System X repositories
# Part of the Governance & Onboarding Hub solution.

set -e

TITLE=""
USERS=""
AGENT="antigravity"

while [[ $# -gt 0 ]]; do
  case $1 in
    -t|--title)
      TITLE="$2"
      shift 2
      ;;
    -u|--users)
      USERS="$2"
      shift 2
      ;;
    -a|--agent)
      AGENT="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

if [ -z "$TITLE" ]; then
  TITLE="New Task Ticket"
fi

# Detect highest ticket number
HIGHEST=0
if [ -d "project" ]; then
  for dir in project/ticket-*; do
    if [ -d "$dir" ]; then
      NUM=$(echo "$dir" | sed -E 's/.*ticket-0*([0-9]+)$/\1/' || echo "0")
      if [[ "$NUM" =~ ^[0-9]+$ ]] && [ "$NUM" -gt "$HIGHEST" ]; then
        HIGHEST=$NUM
      fi
    fi
  done
fi

NEXT_NUM=$((HIGHEST + 1))
TICKET_ID=$(printf "ticket-%03d" "$NEXT_NUM")
TICKET_DIR="project/$TICKET_ID"

mkdir -p "$TICKET_DIR"

# Initialize preprompt.md if missing
if [ ! -f "$TICKET_DIR/preprompt.md" ]; then
  cat <<EOF > "$TICKET_DIR/preprompt.md"
# Preprompt & Technical Directives ($TICKET_ID)

- **Title**: $TITLE
- **Created**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

## Technical Requirements & Constraints
- Implement requirements according to project architecture.
- Follow Docker & Dev Tools rules.

## Linked Resources
- Documentation: https://github.com/wellmanifest/new-project
EOF
fi

# Initialize changelog.md if missing
if [ ! -f "$TICKET_DIR/changelog.md" ]; then
  cat <<EOF > "$TICKET_DIR/changelog.md"
# Ticket Changelog ($TICKET_ID)

## [0.1.0] - $(date -u +"%Y-%m-%d")
- Initial ticket scaffolding created.
EOF
fi

# Automatically update master menu index
if [ -f "project/readme.sh" ]; then
  bash ./project/readme.sh
fi

echo "Successfully scaffolded $TICKET_DIR for title '$TITLE'."
