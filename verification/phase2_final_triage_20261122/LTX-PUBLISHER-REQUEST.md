# Request for exact LTX 2.5 upscaler SHA-256

**Draft for Lightricks or the Hugging Face repository maintainer.**

Could you confirm the authoritative SHA-256 of the original bytes for this artifact?

| Field | Value |
|---|---|
| Repository | Lightricks/LTX-2.5 |
| Immutable commit | 49b093a39c19169a8a81721dcc541e07e945232f |
| Path | latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors |
| Expected byte size | 995,778,752 |

A publisher-authenticated manifest or confirmation of the Git LFS SHA-256 OID and byte size for this exact commit and path is sufficient. Please include a verification reference if one is available. [Exact artifact](https://huggingface.co/Lightricks/LTX-2.5/blob/49b093a39c19169a8a81721dcc541e07e945232f/latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors)

## Approved metadata-only procedure when existing access is available

1. Use the existing authorized read credential through the environment's secret provider. Limit authorization headers to TLS requests to `huggingface.co`. Disable credential and header logging.
2. Query the authenticated tree metadata for the pinned commit and exact parent directory. Select exactly one matching file. Require size and LFS byte size of 995,778,752 and an unmasked 64-hex SHA-256 LFS OID.
3. Issue HEAD against the same pinned resolve URL with redirect following disabled. When first-party linked headers are available, compare `X-Repo-Commit`, `X-Linked-Size` and `X-Linked-ETag` to the exact tuple. Use the linked ETag only when consistent with the explicit LFS OID. A Git blob OID, masked value, or unrelated Xet identifier is insufficient.
4. Retain a redacted tuple, UTC timestamp, endpoint type, HTTP status, digest provenance and consistency result. Discard request headers, cookies and redirect locations. On 401, 403, a terms prompt, no authoritative digest or inconsistency, stop and keep the installation gate closed. An authoritative publisher attestation for the same tuple can also support review.
5. A future separately authorized install must independently verify actual downloaded byte count and SHA-256 before activation.

Current status **AUTHENTICATION REQUIRED**. No LTX request was issued in this triage. [Previous redacted receipt](../phase2_cpu_gaps_20261122/ltx-auth-status.json)
