# Story AI — next free GPU providers, 2026-11-15

Scope: only the already-authorized Qwen3.5-9B GGUF Story benchmark. Existing Colab mount-denial evidence preserved; failed isolation test and GPU/RAM probes not repeated.

## Ordered live browser observations

| Provider | Observed blocker | Secure worker isolation |
|---|---|---|
| Kaggle | /code initially loaded in signed-out state (Login/Sign Up). New Notebook interaction encountered an image reCAPTCHA requiring motorcycle selection. No challenge solved or bypassed; no executable notebook reached. | Not tested; no runtime access |
| Lightning AI | Homepage: “Coming soon”; “Lightning hasn't expanded to your area yet.” | Not tested; no runtime access |
| Hugging Face | Signed-in account reached New Space form. Gradio and Docker radio controls disabled and labelled Paid. Page: “Gradio and Docker Spaces require a paid plan” and “Static Spaces stay free for everyone. To create a Space that runs on compute, subscribe to PRO.” No Space created or subscription activated. | Not tested; no eligible free compute exposed to this account |
| Amazon SageMaker Studio Lab | Homepage offers Sign in, no authenticated runtime. Notice: “Amazon SageMaker Studio Lab is no longer be open to new customers.” Existing Studio Lab account eligibility unknown. | Not tested; no runtime access |

These are current browser observations, not a claim that every provider universally prohibits namespaces or that all free GPU platforms were exhausted. No accessible eligible free runtime demonstrated the required bubblewrap user/PID/network/mount isolation with fresh /proc. Arbitrary public model demos were not substituted for the exact approved worker/model.

New model downloads: 0. New inference calls: 0. Complete new story: absent. Fifteen-criterion evaluation on new output: not performed. Human review: pending. Benchmark NOT COMPLETED.

Smallest next requirement: complete Kaggle's human verification and sign-in using the user's account, then test only the required isolation before any model installation. A successful login does not prove free GPU allocation or isolation support. If an existing Studio Lab account is available, authenticated access would likewise be required before verification. No paid alternative is authorized.

No other agent tests, security weakening, main changes, deployment, publishing, new hosted compute resources or terms acceptance occurred. Only this evidence is committed on feature/video-music-editing-studio.
