# Ticket 255: Allocate canonical Worktrees v5 ticket checkouts

- **ID**: ticket-255
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-19

## Goal and scope

Make the file-backed ticket allocator create every new ticket inside its
canonical relative linked worktree and establish the matching local lease.
The allocator must leave primary checkout ticket carriers untouched.

## Acceptance criteria

- [x] AC-01: A file-backed allocation produces the prescribed branch,
  relative linked worktree and lease, without writing `project/ticket-NNN` in
  the primary checkout.
- [x] AC-02: Allocation preserves a recoverable reservation when a later
  materialization step fails, and the managed governance gate passes.

## Risks and notes

This ticket is the explicitly authorized one-off bootstrap needed to repair
the allocator's self-hosting deadlock. It neither recovers foreign work nor
grants publication or merge authority.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
