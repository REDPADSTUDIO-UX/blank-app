# Phase 2 সীমিত অনুমোদনের ফল

ভিত্তি `815cacfa26dd370039e7e11c01889d8b7174fc83`। Production route, runtime registry এবং পূর্বের ১৩টি PASS অক্ষত। নতুন ২১টি CPU check সফল, যার মধ্যে ১৩টি Qwen preflight test এবং ৮টি Wan sandbox fixture check। পূর্ণ profile PASS যোগ হয়নি। [১৮-প্রোফাইল ম্যাট্রিক্স](updated-18-profile-matrix.json)

## Qwen · PARTIAL

প্রকাশকের exact FP8 revision-এ ১৪টি shard, মোট 37,463,724,680 bytes এবং প্রত্যেক shard-এর প্রকাশ্য LFS SHA-256 manifest-এ মেলে। এটি publisher metadata review। Exact BF16 base SHA থেকে derivative conversion provenance অপ্রতিষ্ঠিত। Linux x86-64 candidate হলো Transformers 5.22.2, Torch 2.10.0-এর PyPI CUDA 12.8 dependency set, Triton 3.6.0, Accelerate 1.13.0, kernels 0.17.2, Hub 1.31.0 এবং Safetensors 0.8.0। Pinned kernel revision-এর CUDA build metadata রেকর্ড আছে। সম্পূর্ণ hashed CUDA transitive closure, installed toolkit/driver ABI, grouped kernel execution এবং real FP8 memory/precision এখনও অযাচাইকৃত। কোনো CUDA package এই প্রোফাইলের জন্য ইনস্টল হয়নি। [Manifest](qwen-public-manifest.json) · [Dependency metadata](qwen-dependency-research.json)

প্রস্তাবিত preflight selected CUDA devices-এর capability, তিনটি callable FP8 kernel entry point, quantizer input state এবং actual backend validation-এর পর dequantize state চেক করে। Mocked multiple devices-এ একটি unsupported GPU, missing/noncallable grouped kernel, invalid state, fallback এবং validation failure প্রত্যাখ্যাত হয়েছে। Exact Transformers guard-এ mocked SM 8.6 BF16 fallback ঘটিয়েছে এবং fixture সেটি প্রত্যাখ্যান করেছে। SM 8.9-এর positive mock পাস। Launch integration-এর আগে immutable local kernel bundle, device-map এবং guard receipt একই execution context-এ bind করতে হবে। Production activation বা artifact download-এর জন্য আলাদা অনুমোদন লাগবে। [১১টি policy test](qwen-preflight.log) · [২টি backend test](qwen-backend.log)

## Wan Distilled · PARTIAL

Publisher-linked PR #14412, fork commit `14f482c30c91021cc0e363a0a17a115b44972aee`। Read-only, unprivileged, loopback-only Docker test-এ exact pipeline ও transformer import হয়েছে। Unlisted synthetic file অনুপস্থিত ছিল এবং source write প্রত্যাখ্যাত হয়েছে। Actual constructor synthetic FlowMatch scheduler গ্রহণ করেছে। Source-এর exact scheduler selection fragment দিয়ে Euler ও DPM উভয় CPU schedule ১০টি timestep দিয়েছে। Guidance 1.0-তে CFG বন্ধ, 1.01-তে চালু। Publisher Distilled recipe Euler ও guidance 1.0 নির্দেশ করে। Synthetic check-এ pinned model index-এর `image_processor` field এবং constructor parameters-এর পার্থক্য রেকর্ড হয়েছে। Actual pinned component loader, checkpoint compatibility, পূর্ণ hashed dependency closure ও production supervisor binding এখনও যাচাই বাকি। Source এখনও unmerged। Production ব্যবহার বা pin পরিবর্তনের সিদ্ধান্ত আলাদা। [Source review](wan-source-review.json) · [Sandbox log](wan-sandbox.log)

## LTX · BLOCKED

এই runtime-এ পূর্ব-অনুমোদিত Hugging Face credential পাওয়া যায়নি। Authentication request, terms acceptance ও checkpoint download করা হয়নি। Exact revision/path-এর public size 995,778,752 bytes এবং authoritative SHA-256 অজানা। Gate CLOSED। পরবর্তী প্রয়োজন exact repository-এ আগেই access পাওয়া read-capable account credential অনুমোদিত credential channel-এ উপলভ্য করা, অথবা প্রকাশকের কাছ থেকে exact revision/path/size-এর authoritative SHA-256 পাওয়া। [Redacted receipt](ltx-redacted.json)

## অবশিষ্ট মালিকের সিদ্ধান্ত

Indic-Speak ও IndicF5-এর exact gated source এবং commercial terms-এর আগের সিদ্ধান্ত বহাল। Commercial codec substitution এবং production Qwen/Wan routing-এর জন্য পৃথক review ও অনুমোদন দরকার। LTX scope অনুমোদিত আছে। Account access বা publisher checksum এখনও প্রয়োজন। Native Wan-এর pinned import এবং Qwen-এর real FP8 kernel সহ GPU acceptance checks বাকি। **PHASE 2 BLOCKED। GPU PURCHASE NOT APPROVED। Phase 3 শুরু হয়নি।** [আগের অনুমোদন প্যাকেজ](../phase2_external_20261122/APPROVAL-BN.md)
