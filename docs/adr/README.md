# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for significant design choices.

An ADR is a short document that captures:
- The **context** that prompted a decision
- The **decision** that was made
- The **consequences** that follow

ADRs make it easier for new team members and your future self to understand why the system looks the way it does.

## Format

Each ADR is numbered sequentially and uses the format:

```
NNNN-short-title.md
```

Status values: Proposed, Accepted, Deprecated, Superseded by NNNN.

## Index

- [0001 - Use SigLIP as the Default Embedding Model](0001-use-siglip-as-default-embedding.md)

## When to Write an ADR

Write an ADR when you make a decision that:
- Affects the system architecture
- Has consequences that will outlive the person who made it
- Is hard to reverse later
- A future maintainer would reasonably ask "why?"

Do not write an ADR for routine implementation choices, naming conventions, or quick fixes.
