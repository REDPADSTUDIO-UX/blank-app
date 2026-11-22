# Phase 2 final CPU blocker triage

ভিত্তি `5426803b36091707d72b65159f9ec937022d3483`। ১৩/১৮ model-free runtime PASS বহাল। আগের ২১টি approved check এবং ৭টি Wan diagnostic পুনরায় চালানো হয়নি। নতুন ৩টি Wan modular diagnostic check ও ১টি Qwen signature check সফল। নতুন profile PASS নেই। [১৮-প্রোফাইল ম্যাট্রিক্স](updated-18-profile-matrix.json)

| শ্রেণি | যাচাই ও অবশিষ্ট কাজ |
|---|---|
| VERIFIED COMPLETE | ১৮-profile baseline, ১৩টি actual CPU startup ও binding receipt, পূর্বের supervisor/security evidence, Qwen-এর ৭৯টি wheel pin, ১০টি kernel digest ও নতুন Sigstore verification। |
| CPU-FIXABLE | Exact Qwen offline wheelhouse staging ও install receipt, immutable kernel resolution binding, এবং publisher manifest এলে Wan loader fixture ও production binding validation। বর্তমানে staged verified wheelhouse নেই এবং production integration অনুমোদিত নয়। বর্তমান উৎস ও অনুমোদনের মধ্যে আর কোনো স্বতন্ত্র critical CPU defect পাওয়া যায়নি। |
| OWNER APPROVAL REQUIRED | Qwen-এর alternative artifact ও ভবিষ্যৎ activation, Wan candidate production binding, দুই voice profile-এর source-only access ও পৃথক usage/codec rights review। LTX metadata scope অনুমোদিত, credential access এখনও অনুপলব্ধ। |
| PUBLISHER DEPENDENCY | Wan-এর normative processor contract, exact supported loader ও immutable component mapping। LTX-এর exact authoritative SHA-256। Voice gated source ও প্রয়োজনীয় publisher rights বা লিখিত hosting approval। |
| GPU-DEPENDENT | Native Wan pinned import। Qwen driver/ABI, v4 grouped kernel, actual expert precision ও model load। প্রযোজ্য profiles-এ exact model/device load, memory, cancellation, cleanup ও output acceptance। |

**Wan Distilled — BLOCKED।** Monolithic loader-এর কাছে `image_processor` কার্যত unused, constructor-এর supported optional component নয়। Default CLIP path একটি synthetic fixture-এ pinned output মিলিয়েছে। এই omission ইচ্ছাকৃত কি না প্রকাশকের নিশ্চিতকরণ বাকি। Published modular index-এ আরও একটি reproducible structural mismatch আছে। Exact PR source-এ index-এর Distilled pipeline/blocks exports অনুপস্থিত। Local offline modular load requested class-এ ব্যর্থ। Modular index processor বাদ দিয়েছে এবং scheduler ও transformer-এর জন্য mutable PR ref দেয়। ওই ref-এর দুই config byte-for-byte মিললেও component identity বা weight compatibility প্রতিষ্ঠিত হয় না। [Publisher issue draft](WAN-PUBLISHER-ISSUE.md) · [Modular log](wan-modular.log)

**Qwen FP8 — PARTIAL।** Public v4 CUDA bundle-এর publisher signature CPU-তে verified। পূর্বের hashes ও lock বহাল। Wheelhouse installation ও production integration বাকি। Actual grouped execution, dtype এবং CUDA ABI hardware-নির্ভর। [Exact handoff](QWEN-GPU-HANDOFF.md)

**LTX — AUTHENTICATION REQUIRED।** Existing access অনুপলব্ধ। Installation blocked। [Publisher checksum request ও metadata procedure](LTX-PUBLISHER-REQUEST.md)

**Voice — BLOCKED।** Source-only access, internal commercial production ও third-party hosting-এর আলাদা সিদ্ধান্ত দরকার। [Indic-Speak](INDIC-SPEAK-DECISION.md) · [IndicF5](INDICF5-DECISION.md)

বিদ্যমান acceptance criteria বহাল। Actual model-free startup ও production-bound receipts, exact source/dependency integrity এবং pending hardware validation আলাদাভাবে নথিভুক্ত থাকতে হবে। **PHASE 2 BLOCKED। Phase 3 শুরু হয়নি।** [Baseline sign-off criteria and evidence](../phase2_signoff_20261122/FINAL-BN.md)
