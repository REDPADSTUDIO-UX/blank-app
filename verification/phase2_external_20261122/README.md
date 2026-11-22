# Evidence scope

Review date, 2026-11-22 in Dhaka. The public evidence receipt records exact URLs, HTTP outcomes and available response SHA-256. Excerpts, AST extraction and metadata fields are summaries. An HTTP 200 means the requested public resource was accessible. HTTP 401 on pinned source was classified as gated where the public repository metadata independently confirms it.

To reproduce a GET receipt, use the recorded URL with `curl --fail --silent --show-error --max-time 25 -o /tmp/redpad-public-response URL` and `sha256sum /tmp/redpad-public-response`. For the checkpoint receipt, use `curl --silent --show-error --head --max-time 25 URL` on the recorded resolve URL without following redirects or fetching the body. For the two Wan classes and native default, parse the recorded Python source with `ast.parse` and inspect top-level class definitions and function defaults. Public branch and PR endpoints are time-sensitive. Immutable source links allow comparison to the observed revision.

Requests were anonymous, with redirects disabled, and GETs restricted to public source, documentation, dependency or manifest JSON. The Qwen index is a text manifest for shard names and tensor keys. No checkpoint bytes, gated source, production code, dependency lock, model registry or acceptance criteria were changed.
