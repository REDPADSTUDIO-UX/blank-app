# REDPAD YouTube Connect and publishing review — dry-run release

Existing channel: **নিশিকথা (Nishikotha)**, `UCtbHkj0GwJxjXZWbItDAyuQ`.
https://www.youtube.com/channel/UCtbHkj0GwJxjXZWbItDAyuQ

Work stays on `feature/video-music-editing-studio`, PR #2, task #3.
This module does not create any remote channel, upload videos, publish videos,
call paid generation APIs, or change the original studio tables on startup.

## Delivered behavior

The additive **YouTube Connect** tab distinguishes the existing remote channel,
its optional local Channel Manager profile, real read-only Google connection,
and a separately labelled MOCK connection. Registering Nishikotha only adds an
internal SQLite profile, idempotently; it never calls YouTube channel creation.

`redpad_pipeline/youtube.py` provides:

- Google Web OAuth authorization-code flow with offline access, PKCE S256,
  10-minute random state, browser-cookie binding, owner-login binding,
  transactional one-time callback consumption and exact expected channel ID.
- Read-only `youtube.readonly` scope. Upload scope is deliberately not requested.
  The Google account must select the intended Nishikotha Brand Account.
- Google channel identity retrieval, encrypted refresh/access token vault,
  expiration refresh, revoke/disconnect and explicit local forget if revocation
  cannot be reached. No provider response bodies or credentials enter UI errors.
- External PostgreSQL required for live OAuth, mandatory TLS, Fernet encryption
  with a separate server-held key, compare-and-swap record revisions. Tokens
  are not stored in SQLite, Streamlit session state, repository or downloads.
- Multi-channel records keyed by real YouTube ID, with an internal channel
  mapping. Each channel requires its own authorization and identity check.
- Publishing requests bound to file SHA-256, script hash, draft revision,
  internal/remote channel, metadata, visibility, audience, synthetic-media
  disclosure and exact UTC publication timestamp.
- Existing Approval Dashboard approval is required before a request can be
  prepared. A second, separate upload-plan approval is required. Scheduling
  also requires explicit publication approval. Changing any bound input needs
  a new request; stale/missing files, changed scripts, revoked approvals,
  disconnected/mismatched channels, duplicates and cancelled requests fail.
- Asia/Dhaka date/time conversion to future UTC `status.publishAt`, with
  `privacyStatus=private`. Past timestamps are rejected rather than risking
  immediate publication. Dry-run scheduler simulates a due transition and
  revalidates current draft/file/connection before marking it due.
- Isolated local mock records, dry-run history and cancellation. All dry-run
  results state zero network calls and have no remote video ID.

**Live video writes are hard-locked in this release.** `execute_live` refuses
unconditionally and the UI button is disabled. There is no hidden environment
switch to enable uploads. Dry-run success does not prove a real upload,
scheduled publication or Google connection. MOCK approval simulates an owner
decision; real OAuth controls additionally require the private owner login.

## Secure server configuration — developer handoff

No Google password is requested by REDPAD. Google OAuth setup and any Google
permission/security prompts must be completed by the owner in Google's UI.

Required private server variables (empty tracked examples are provided):

| Variable | Purpose |
| --- | --- |
| `GOOGLE_OAUTH_CLIENT_ID` | Owner's Google Cloud Web OAuth client |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Private client secret |
| `GOOGLE_OAUTH_REDIRECT_URI` | Exact registered HTTPS dashboard root URL, no query |
| `REDPAD_YOUTUBE_DATABASE_URL` | External durable PostgreSQL vault URL |
| `REDPAD_YOUTUBE_TOKEN_KEY` | Server-only Fernet key, retained across deploys |
| `REDPAD_REQUIRE_PREVIEW_LOGIN` | Must be `true` for real OAuth |
| `REDPAD_DASHBOARD_PASSWORD` | Existing private dashboard owner gate |

For the current service the intended callback is
`https://redpad-ai-studio-private-preview.onrender.com/`.
No Google client/project or redirect registration is invented by this code.
The YouTube Data API must be enabled on the owner's Google project. Consent
screen/test users and Google verification requirements depend on that project.
The app fails closed without complete configuration or a healthy vault.

The callback returns to the existing Streamlit app, retaining its XSRF browser
cookie across redirects. If the owner session was restarted, the private
dashboard login is required again before callback handling. Only the hash of
the normalized random cookie token is saved inside encrypted OAuth state.
Both current `_streamlit_xsrf` and legacy `_xsrf` cookie names are supported;
unfamiliar/missing cookie formats fail closed. Authorization query parameters
are removed before callback result rendering. Cookie/redirect behavior against
the actual Google project remains a live-integration verification item.

## Render deployment and data preservation

The existing port/start command and private-preview guard are retained.
`requirements.txt`, `pyproject.toml` and `uv.lock` include the vault dependencies.
No paid service, database, worker, disk or provider is provisioned by this change.

The current Render free service uses an ephemeral source SQLite database and
local media. A deploy replaces that filesystem. Back up/migrate existing
profiles, drafts and media before redeploying the original service. Do not
interpret the external connection vault as migration of the original studio
database/media: they are separate concerns. Test records are also ephemeral.

This release does not run an always-on scheduler. The dry-run tick simulates
due records. A future live implementation should use YouTube's approved
private-video `publishAt` scheduling, plus durable dispatch/reconciliation,
instead of depending on a timer in a sleeping Render free web process.

## Tests and remaining release gates

### Current environment observation — 28 October 2026

- Google Cloud Console displayed **Google Cloud access blocked**, requiring the
  owner to enable 2-Step Verification/MFA. No security settings were changed,
  no OAuth client was created, and no Google permission was accepted.
- The original Render service `redpad-ai-studio-private-preview` was live on
  `06915ba`, with auto-deploy off. Its dashboard showed one local channel and
  one awaiting-review draft. It was not redeployed because preserving those
  existing ephemeral records/media requires a backup/migration first.
- Python 3.12 and locked Python 3.14 environments passed the new authorization
  and widget tests. The local Chromium process could not start due to the
  execution environment's socket restriction; the real-browser check is also
  wired into GitHub CI, where its final result must be inspected separately.

`tests/test_youtube.py`: offline HTTP contracts, encrypted credentials,
state/PKCE/browser/owner checks, denial/expiry/replay, wrong channel, scope and
refresh failures, revocation, CAS conflicts, duplicate/cancel/stale approval,
cross-channel isolation, UTC conversion and due scheduling. HTTP is mocked.

`tests/test_youtube_ui.py`: isolated real Streamlit app, Nishikotha local profile,
separate mock connection, real FFmpeg MP4, private dry-run approval and execution,
locked real connection/write buttons without configuration. External requests
are forbidden. Existing production/UI/renderer regressions are retained.

`tests/browser_smoke.py`: real Chromium dashboard, production render/download,
new YouTube tab, clearly separate Google/mock statuses and disabled writes;
captures `youtube-connect-mock.png` in CI artifacts. No Google login occurs.

Still required before claiming production publishing:

1. Owner-approved Google Cloud OAuth project/client/consent configuration and
   durable PostgreSQL provisioning, then real read-only connection to Nishikotha.
   PostgreSQL integration and Google redirect round trip are not verified by
   mocked HTTP or a memory vault.
2. Back up/migrate existing Render source records and media; deploy and verify
   the new tab in the intended environment without data loss.
3. Implement and audit the live resumable video-write transport and protected
   durable dispatch queue, ambiguous-upload reconciliation, quota/backoff,
   approval-bound restart recovery and duplicate protection across crashes.
   Explicit upload scope consent and a separately approved real-video test are
   required; none is authorized in this task.
4. Confirm the Google project's verification/audit restrictions and real
   scheduled-publication behavior before enabling any production writes.

Primary references:
- https://developers.google.com/youtube/data/guides/auth/server-side-web-apps
- https://developers.google.com/identity/protocols/oauth2/resources/best-practices
- https://developers.google.com/youtube/data/reference/rest/v3/videos
- https://developers.google.com/youtube/v3/revision_history
- https://render.com/docs/deploys
