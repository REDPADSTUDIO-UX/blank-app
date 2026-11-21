# REDPAD AI Studio — Phase 2 lifecycle ও runtime verification

**Phase 2 BLOCKED। GPU purchase NOT APPROVED।** নিশ্চিত lifecycle ত্রুটি সংশোধন ও যাচাই হয়েছে। পূর্ণ runtime startup ও secure binding-এর প্রমাণ **১৮টির মধ্যে ১১টির** জন্য আছে। সাতটি প্রোফাইলে পূর্ণ startup প্রমাণ বাকি। Phase 3 শুরু হয়নি।

## সংশোধন ও পরীক্ষা

- Engineering commit 7050a9319cafe4ff6e7325dde7d5d6a01ae9d40a-তে device list job claim-এর আগে পরীক্ষা হয়। আগে nested list-এর membership check-এ TypeError startup handler এড়িয়ে যেত। এখন malformed request-এ FAILED receipt হয় এবং concurrent cancellation হলে CANCELLED বহাল থাকে। Claim-এর পরে startup exception-এ process group cleanup ও terminal receipt হয়। PID registration ব্যর্থ হলে বাস্তব CPU dummy process বন্ধ হয়েছে।
- একই commit-এ আগে থেকে থাকা LTX integrity patch সংরক্ষিত ও যাচাইকৃত। Official SHA-256 অনুপস্থিত থাকলে gate বন্ধ। Pin পাওয়া গেলে exact artifact size ও SHA-256 দুটিই বাধ্যতামূলক।
- নতুন focused run **৪৯ pass**। Full deduplicated CPU run **৭০৭ distinct IDs, ৭০৬ pass, ১ local kernel skip, ০ failure/error**। দুই run-এর coverage overlap করে।
- আলাদা Ubuntu 22.04 kernel run-এ native ও shared worker উভয়ের A–F পাস এবং exit 0। ২১-agent matrix যাচাই পাস।

## ১৮-profile matrix

পুরোনো ১১টি row অপরিবর্তিত রেখে সাতটির পর্যবেক্ষণ হালনাগাদ হয়েছে। [পূর্ণ matrix](final-18-profile-matrix.json)

| প্রোফাইল | নতুন প্রমাণ ও অবশিষ্ট শর্ত |
|---|---|
| Qwen 3.5 MoE | CPU synthetic packed expert FP8 conversion, meta shape ও routed dequantized reference forward পাস। Exact recipe অনুমোদন ও বাস্তব GPU quantized kernel বাকি। |
| Wan Animate 2 | Publisher source tree ও handler signature যাচাই হয়েছে। সম্পূর্ণ reviewed CPU import closure, binding ও CUDA 12.6 stack বাকি। |
| Wan Animate 2 Distilled | **BLOCKED**। Publisher model index-এর WanAnimate2Pipeline বর্তমান Diffusers 0.43.0 export করে না। Exact publisher-supported pipeline বাকি। |
| LTX 2.5 | ১২টি CPU support import, TorchVision NMS, TorchAudio resample ও PyAV PCM roundtrip পাস। পূর্ণ pinned pipeline startup ও binding বাকি। OpenImageIO shutdown-এ nanobind reference-leak warning তদন্ত বাকি। |
| Indic-Speak | **BLOCKED**। Gated publisher source-এ অনুমোদিত access এবং reviewed SNAC/Vocos closure বাকি। |
| IndicF5 | **BLOCKED**। Exact source access এবং commercially eligible codec route বাকি। Vocos-এর Encodec 0.1.1 pin CC BY-NC 4.0। |
| ACE-Step 1.5 | Publisher source tree ও handler interface যাচাই হয়েছে। সম্পূর্ণ reviewed CPU closure ও binding বাকি। Production Torch/TorchAudio 2.10.0+cu128 GPU-তে যাচাই করতে হবে। |

LTX spatial upscaler **995,778,752 bytes**। Exact publisher metadata-তে LFS OID masked এবং HEAD HTTP 401। Official SHA-256 এখনও পাওয়া যায়নি। Model loading, CUDA device binding ও inference বাকি। ২১-agent routes সংরক্ষিত।

[Kernel run](https://github.com/REDPADSTUDIO-UX/blank-app/actions/runs/44931884961) · [CPU receipt](regression-receipt.json) · [Commands](COMMANDS.md)
