# How we work

The repository follows a team workflow on GitHub. Roles are in `README.md`: the AI agent is Product owner / analyst and developer; the human is QA.

## Branches

`main` holds only reviewed work. Every change goes through a pull request.

| Prefix | Who | Example |
|---|---|---|
| `spec/` | PO | `spec/F-UI-001-v0.4` |
| `feat/` | dev | `feat/ui-shell-layout` |
| `fix/` | dev | `fix/drawer-focus` |
| `qa/` | QA | `qa/tc-ui-health-check` |
| `chore/` | anyone | `chore/ci-spec-checks` |

## Pull request flow

1. Author opens a PR from a branch, fills in the template and links issues (`Closes #12`).
2. CI runs `spec-checks` (req-review scripts and their unit tests). Red CI blocks the merge.
3. QA reviews: line comments for findings (where / type + severity / problem / impact / suggestion), then a label:
   - `qa-changes-requested` — open High or blocking remarks;
   - `qa-approved` — ready to merge.
4. Author answers each comment in its thread and pushes fixes to the same branch. New commits remove `qa-approved` automatically, so QA reviews again.
5. Merge with **Squash and merge** when `spec-checks` and `qa-gate` are green. The branch is deleted after merge.

The repository runs on one GitHub account, so GitHub's own Approve / Request changes buttons are not available on PRs: the labels and the `qa-gate` check replace them. A QA comment is resolved only by QA.

## Issues

| Label | Meaning |
|---|---|
| `clarification` | A question or edit the PO must resolve in a spec (CL-xx) |
| `blocking` | Must be resolved before development starts |
| `defect` | Behaviour does not match the spec |
| `severity:high` / `severity:medium` / `severity:low` | QA severity |
| `qa-approved` / `qa-changes-requested` | QA verdict on a PR |

## Commits

Short imperative subject in English, with the spec or issue ID: `F-UI-001: resolve CL-05 (60 s counted from last check)`.

## Language

Chat with QA — Russian. Specs, PRs, issues, review reports and commit messages — English.
