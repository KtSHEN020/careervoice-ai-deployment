# Upstream Component Versions

This document records the exact original repository commits used to create the deployment package snapshots.
These identifiers document historical import provenance; they do not assert that
current integrated copies are identical to those commits.

| Component | Original repository | Imported commit | Status |
|---|---|---|---|
| Career profile extraction | voice-career-profile-extractor | `322402d` | Imported |
| Job recommendation | preference-aware-job-recommender | `c04006f` | Imported |
| Job collection | job-listing-collector | `176f213` | Imported |
| Workflow coordination | careervoice-ai-orchestrator | `06211a6` | Imported |
| Web application | careervoice-ai-web-app | `80e3136` | Imported |

## Historical import policy

Package snapshots were exported from committed Git versions.

The imported deployment copies excluded:

- Git histories;
- local environment files;
- virtual environments;
- package-specific lockfiles;
- caches;
- generated outputs;
- runtime user data.

## Current integrated development

The original repositories remain separate development and portfolio projects.
Integrated package copies under `packages/` may have diverged since import.
The current checked-out deployment source, tests, migrations, lockfiles, and
workflows govern behavior in this application.

Cross-repository synchronization is never automatic and requires explicit
authorization. Do not overwrite integrated changes merely to match an imported
commit or a standalone repository. See the [root README](../README.md#repository-role-and-status)
for the current repository role.
