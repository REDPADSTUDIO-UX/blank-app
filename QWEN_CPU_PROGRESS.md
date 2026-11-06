# Qwen CPU real-inference checkpoint

Continue after Phase 3 commit 21574648dac4f9b8006020dd693c3d61444ce98b.
Owner explicitly authorized the local Ollama runtime and only Qwen3-4B-Instruct-2507 Q4_K_M.

Installed Ollama 0.40.15 in the ignored development model directory, verifying the official release
archive SHA256. Installed the exact 2.497 GB Q4_K_M model with manifest digest
0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0.
No system service or cloud account was created; no other model was downloaded.

First genuine CPU inference completed: 127 output tokens, 23.697 seconds wall time including
load/prefill, approximately 13.7 decoded tokens/second. Ollama reported size_vram=0.
Original output, model identity, options and metrics are in verification/phase3_cpu/cpu_smoke.json.
The Bengali dialogue is semantically weak; runtime success is not creative quality success.

Command contexts isolate loopback. The installed runtime and client therefore run inside an owned
local_cpu_session context. It does not download weights or modify a system service, and stops only
its own process on exit. UI controls can explicitly opt into this installed development runtime.

CPU research candidates consume unapproved experimental sources only in a separate research ledger.
They never mark production sources Approved or bypass the existing task QC/owner gates. The same
existing creative validators are reused. Story/Script/Director trials and bounded revision are next;
no independent human review or cinematic production approval has occurred.

Fixed a real transport/contract mismatch: a targeted scene rewrite may return a JSON array; the
local adapter now accepts structured object/array JSON while department validators enforce shape.
Added a bounded CPU timeout option (30–600 seconds; default remains 180). CPU trials use 420 seconds.
Focused verification: 22 tests passed. Full regression will be rerun after the creative experiments.

No Render deployment, main change, paid API, GPU rental, new cloud resource or YouTube write.
