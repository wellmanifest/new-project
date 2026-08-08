# Preprompt & technical directives (ticket-043)

- Publish only ticket-042's merged behavior as immutable patch v0.13.2.
- Keep the tag annotated and previously absent; never move or overwrite it.
- Validate metadata agreement, full Linux, protected Windows and a clean
  detached merge checkout before tagging.
- Create a non-draft, non-prerelease GitHub Release bound to the exact commit.
- Keep downstream changes in todo2code ticket-050.
- Do not create or edit human-owned `user-*.md` files.
