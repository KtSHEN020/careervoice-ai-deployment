# Upstream Component Versions

This document records the exact original repository commits used to create the deployment package snapshots.

| Component | Original repository | Imported commit | Status |
|---|---|---|---|
| Career profile extraction | voice-career-profile-extractor | `2e64718` | Imported |
| Job recommendation | preference-aware-job-recommender | Not imported | Pending |
| Job collection | job-listing-collector | Not imported | Pending |
| Workflow coordination | careervoice-ai-orchestrator | Not imported | Pending |
| Web application | careervoice-ai-web-app | Not imported | Pending |

## Import policy

Package snapshots are exported from committed Git versions.

The deployment copies exclude:

- Git histories;
- local environment files;
- virtual environments;
- package-specific lockfiles;
- caches;
- generated outputs;
- runtime user data.

The original repositories remain the sources of truth.