# REDPAD AI STUDIO — Phase 2 অবশিষ্ট আটটি profile

**ফল PARTIAL। নতুন ১টি model-free runtime যাচাই হয়েছে। আগের ১০টিসহ ১৮টির মধ্যে ১১টি যাচাইকৃত।**

| Profile | আজকের ফল | প্রমাণ ও বাকি কাজ |
|---|---|---|
| Stable Audio Small | **PASS · model-free CPU এবং secure binding** | Python 3.10, Torch/TorchAudio 2.7.1+cpu, TorchVision 0.22.1+cpu ও stable-audio-tools 0.0.20। Ubuntu 22.04 production sandbox-এ আটটি import/symbol probe এবং synthetic 48 kHz stereo PCM16 WAV পাস। |
| Qwen 3.5 MoE | **BLOCKED · অনুমোদিত route** | Exact MoE class import হয়েছে। Actual meta-device expert test-এ existing NF4 converter একটি Linear control রূপান্তর করলেও packed gate/up এবং down tensors রূপান্তর করেনি। Expert-compatible quantization recipe যাচাই প্রয়োজন। |
| Wan Animate 2 | **PARTIAL · source** | Exact revision-এর চারটি reviewed source file-এর hash মিলেছে। WanAnimate2MPIPipeline-এর সম্পূর্ণ reviewed source ও CPU dependency closure বাকি। Publisher lock Linux-এ CUDA 12.6 Torch stack চায়। |
| Wan Animate 2 Distilled | **BLOCKED · exact pipeline** | Exact model index-এ WanAnimate2Pipeline চাওয়া হয়েছে। পরীক্ষিত Diffusers 0.43.0 ওই class export করে না। Transformer class import হয়েছে। স্বতন্ত্র publisher-supported adapter/source প্রয়োজন। |
| LTX 2.5 | **PARTIAL · source, BLOCKED · checkpoint** | পাঁচটি reviewed source hash মিলেছে। Exact LTX pipeline 1.6.2 ও linked core closure এখনও চালানো হয়নি। Upscaler **995,778,752 bytes**। Public LFS OID masked, pinned HEAD-এ hash পাওয়া যায়নি। Installation gate বন্ধ। |
| Indic-Speak | **PARTIAL · support imports** | SNAC, SoundFile, Torch/TorchAudio ও Llama symbol পাস। Pinned gated source HTTP 401। অনুমোদিত exact source ও Vocos/codec closure বাকি। |
| IndicF5 | **PARTIAL · support imports** | Matching Torch/TorchAudio ও SoundFile পাস। Exact F5 source HTTP 401 এবং Vocos চালু হতে Encodec 0.1.1 প্রয়োজন। Source access, codec rights ও সম্পূর্ণ closure বাকি। Consent gate বহাল। |
| ACE-Step 1.5 | **PARTIAL · source** | সাতটি reviewed source hash মিলেছে। Diffusers-এর VAE symbol আলাদা stack-এ পাওয়া গেছে। Exact ACE handler CPU closure চালানো হয়নি। Publisher Linux x86-64 lock Torch/TorchAudio 2.10.0+cu128 চায়। |

Stable Audio native dispatcher `audio_worker.run` খুঁজত, কিন্তু module-এ শুধু `main` ছিল। একই payload entrypoint যুক্ত ও regression-tested হয়েছে। সরাসরি ব্যবহৃত audio/voice/ACE dependencies এখন receipt gate-এ বাধ্যতামূলক। Stable Audio 0.0.20-এর জন্য Python 3.11-এর local imports চললেও publisher metadata সেটি অনুমোদন করে না এবং CI installation প্রত্যাখ্যান করে। Python 3.10-এর নতুন CPU lock-এ installer, receipt, kernel-isolated child এবং imports পাস করেছে।

**১২৩টি স্বতন্ত্র targeted regression test পাস**, failure/error/skip শূন্য। আগের Phase 1 ও ১০-profile receipts পুনরায় গণনা করা হয়নি। Voice resolution-এর অস্থায়ী পরীক্ষায় Encodec 0.1.1 তৈরি ও install হয়েছিল। প্রকাশকের CC BY-NC 4.0 দেখে package সরানো হয়েছে। চূড়ান্ত probe ও lock-এ এটি ব্যবহৃত হয়নি এবং commercial route অনুমোদিত হয়নি।

**Gate।** সাতটির exact route বা runtime closure এখনও বাকি। GPU capability, model loading, generation এবং production approval পৃথক যাচাই। Phase 3 শুরু হয়নি। ২১-agent routes বা registry বদলানো হয়নি।

[১৮-profile final matrix](final-18-profile-matrix.json) · [Stable runtime CI](https://github.com/REDPADSTUDIO-UX/blank-app/actions/runs/44924150354) · [Runtime receipt](stable-sandbox-receipt.json)
