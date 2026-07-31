#!/usr/bin/env bash
# Universal ticket index generator for project/README.md
# Part of the Governance & Onboarding Hub solution.

set -e

README_FILE="project/README.md"
mkdir -p project

if [ ! -f "$README_FILE" ]; then
  cat <<EOF > "$README_FILE"
# Indeks Ticketów i Menu Projektu (\`project/\`)

- **Dokumentacja Zarządcza Hub**: [Governance Hub (\`wellmanifest/new-project\`)](https://github.com/wellmanifest/new-project)
- **Status Projektu**: AKTYWNY

## Opis Katalogu

Katalog \`project/\` służy do zarządzania cyklem życia ticketów i procedurami zarządczymi w repozytorium docelowym.

---

## Indeks Ticketów i Uczestników

<!-- AUTO:TICKET_INDEX:START -->
<!-- AUTO:TICKET_INDEX:END -->

---

## Instrukcja Obsługi

- **Tworzenie nowego ticketu**:
  \`\`\`bash
  ./project/new-ticket.sh --title "Nazwa Zadania"
  \`\`\`
- **Aktualizacja indeksu**:
  \`\`\`bash
  ./project/readme.sh
  \`\`\`
EOF
fi

TABLE_HEADER="| Ticket ID | Wytyczne (preprompt.md) | Uczestnicy Ludzcy (user-*.md) | Mózg AI (ai-*.md) | Logi CLI | Changelog |\n| :--- | :--- | :--- | :--- | :--- | :--- |"
TABLE_ROWS=""

for dir in project/ticket-*; do
  if [ -d "$dir" ]; then
    TICKET_NAME=$(basename "$dir")

    PREPROMPT_LINK="-"
    if [ -f "$dir/preprompt.md" ]; then
      PREPROMPT_LINK="[\`preprompt.md\`](./$TICKET_NAME/preprompt.md)"
    fi

    CHANGELOG_LINK="-"
    if [ -f "$dir/changelog.md" ]; then
      CHANGELOG_LINK="[\`changelog.md\`](./$TICKET_NAME/changelog.md)"
    fi

    USERS_LINKS=""
    for ufile in "$dir"/user-*.md; do
      if [ -f "$ufile" ]; then
        UNAME=$(basename "$ufile")
        USERS_LINKS="$USERS_LINKS [\`$UNAME\`](./$TICKET_NAME/$UNAME)"
      fi
    done
    [ -z "$USERS_LINKS" ] && USERS_LINKS="-"

    AI_LINKS=""
    for afile in "$dir"/ai-*.md; do
      if [ -f "$afile" ]; then
        ANAME=$(basename "$afile")
        AI_LINKS="$AI_LINKS [\`$ANAME\`](./$TICKET_NAME/$ANAME)"
      fi
    done
    [ -z "$AI_LINKS" ] && AI_LINKS="-"

    LOG_LINKS=""
    for lfile in "$dir"/ai-*-logs.txt; do
      if [ -f "$lfile" ]; then
        LNAME=$(basename "$lfile")
        LOG_LINKS="$LOG_LINKS [\`$LNAME\`](./$TICKET_NAME/$LNAME)"
      fi
    done
    [ -z "$LOG_LINKS" ] && LOG_LINKS="-"

    TABLE_ROWS="${TABLE_ROWS}\n| **$TICKET_NAME** | $PREPROMPT_LINK | $USERS_LINKS | $AI_LINKS | $LOG_LINKS | $CHANGELOG_LINK |"
  fi
done

INDEX_CONTENT="${TABLE_HEADER}${TABLE_ROWS}"

python3 -c "
import re
readme = open('$README_FILE').read()
replacement = '<!-- AUTO:TICKET_INDEX:START -->\n' + '''$INDEX_CONTENT''' + '\n<!-- AUTO:TICKET_INDEX:END -->'
new_readme = re.sub(r'<!-- AUTO:TICKET_INDEX:START -->.*?<!-- AUTO:TICKET_INDEX:END -->', replacement, readme, flags=re.DOTALL)
open('$README_FILE', 'w').write(new_readme)
" 2>/dev/null || true

echo "Updated $README_FILE ticket index successfully."
