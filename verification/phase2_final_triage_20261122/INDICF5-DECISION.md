# IndicF5 owner decision

**BLOCKED.** Scope the decision to `ai4bharat/IndicF5@fb652a96e508091045890dae5bb99fe511facbcf`. Authorize source-only review of the exact gated entrypoint, config and F5-TTS source separately. The model card's MIT tag does not establish rights for the complete codec stack.

- **Internal commercial production.** Commercial use requires rights for the exact code, codec package and codec weights. The reviewed Vocos pin requires Encodec 0.1.1, whose package metadata states CC BY-NC 4.0. A different codec requires separate owner approval and pinned mel, decoder, sample-rate and waveform contract evidence.
- **Hosted third-party inference.** Review the publisher's gated terms and rights to serve the full stack to third parties, including any distribution and service terms. Keep reference recording and transcript use within documented speaker consent. Internal approval does not establish hosted rights.
- After authorized access, review exact source and licenses before testing any candidate codec. BigVGAN compatibility remains unverified.

[Publisher metadata](https://huggingface.co/api/models/ai4bharat/IndicF5/revision/fb652a96e508091045890dae5bb99fe511facbcf) · [Exact Encodec package metadata](https://pypi.org/pypi/encodec/0.1.1/json)
