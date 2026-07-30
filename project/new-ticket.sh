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

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Initialize preprompt.md from template if present, or write technical directives
if [ -f "template/files/preprompt.template.md" ]; then
  sed "s/{TICKET_ID}/$TICKET_ID/g; s/{SHORT_TITLE}/$TITLE/g; s/{TIMESTAMP}/$TIMESTAMP/g" template/files/preprompt.template.md > "$TICKET_DIR/preprompt.md"
elif [ ! -f "$TICKET_DIR/preprompt.md" ]; then
  cat <<EOF > "$TICKET_DIR/preprompt.md"
# Preprompt & Wytyczne Techniczne ($TICKET_ID)

- **Tytuł Zadania**: $TITLE
- **Utworzono**: $TIMESTAMP

## Wymagania i Ograniczenia Techniczne
- Zaimplementuj wymagania zgodnie z opisaną architekturą projektu.
- Przestrzegaj odizolowanego środowiska Docker oraz zasad automatyzacji narzędzi deweloperskich (\`./project.sh\` / \`project.bat\`).

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Specyfikacja modułu: {Wpisz odnośnik do dokumentacji technicznej lub pliku}

## Dyrektywy Wykonawcze dla Agenta AI
- Odczytaj niniejsze wytyczne techniczne oraz notatki z \`user-{github_username}.md\`.
- Na tej podstawie zbuduj specyfikację wykonawczą w pliku \`ai-{PROVIDER}.md\` (rozumienie intencji, zakres prac, koncepcja, Kryteria Odbioru).
- Przed pisaniem kodu przedstaw plan w \`ai-{PROVIDER}.md\` oraz w \`TODO.md\` do weryfikacji człowieka (\`P-CORE-008\`).
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
