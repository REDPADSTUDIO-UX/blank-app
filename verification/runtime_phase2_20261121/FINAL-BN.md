# REDPAD AI STUDIO — PHASE 2 FINAL MODEL RUNTIME READINESS REPORT

২১ নভেম্বর ২০২৬, ঢাকা। শুরুতে remote feature HEAD `3a3fc98a09a7c8924d78b1dbc0f16154f97b5c09`। Phase 1 evidence, ২১-agent registry ও নির্বাচিত model revisions সংরক্ষিত।

**Phase 2 — PARTIAL।** তিনটি পৃথক CPU runtime lock ও ১৮টি বর্তমান model profile-এর evidence matrix তৈরি হয়েছে। ৮টি profile-এর পূর্ণ runtime এখনও অবরুদ্ধ। [Model–runtime matrix](runtime-matrix.json)

| স্তর | ফল |
|---|---|
| Runtime engineering | Lock, interpreter, ABI, source ও model revision binding যাচাই হয়েছে। অপরীক্ষিত profile-গুলোর reviewed dependency closure প্রয়োজন। |
| Model-free startup | Ubuntu 22.04 production sandbox-এ তিনটি lock-এর **৩১টি model-free import/symbol check** পাস। ১০টি profile-এর binding গ্রহণ করেছে। Media stack-এর bundled FFmpeg synthetic H.264 encode ও decode করেছে। |
| Real model ও GPU compatibility | মডেল লোড, driver/device ও acceleration পরীক্ষা বাকি। |
| Production readiness | Exact model bundle, production acceptance ও স্বাধীন creative review বাকি। |
| Phase 3 | পূর্ণ Phase 2 gate খোলা হয়নি। Phase 3 শুরু করা হয়নি। |

## ২১ এজেন্টের primary route

| এজেন্ট | Primary profile ও model-free প্রমাণ |
|---|---|
| Director, QC, Story, Script, Character, Performance, Cinematographer, Continuity, Editing & VFX, Growth, Casting Director | `qwen35_27` · modern |
| Art Director, Location, Costume Designer, Storyboard | `flux2_klein4` · modern |
| Production Manager | `qwen36_27` · modern |
| YouTube | `qwen35_9` · modern |
| Video Generation | `wan22_5` · media |
| Motion & Physics | `wan_animate2` · reviewed native source ও dependency closure বাকি |
| Voice & Dialogue | `indic_speak` · exact source, SNAC/Vocos/SoundFile ও matched Torch stack বাকি। Indic Parler-এর পরীক্ষিত stack আলাদা fallback candidate। |
| Music & SFX | `ace15` · reviewed ACE-Step 1.5 source ও exact audio closure বাকি। |

Registry-এর primary ও alternate routes, repository, immutable revision, adapter, lock hash ও profile status পৃথকভাবে matrix-এ আছে। Qwen3.5 MoE ও Wan Animate distilled-এর exact execution contract বাকি। LTX 2.5-এর native lock এবং official spatial-upscaler SHA-256 বাকি। IndicF5 ও Stable Audio-এর reviewed source/lock ও CPU startup বাকি। Legacy eligible alternatives matrix-এ static evidence সহ আছে।

## বাস্তব CPU ফল ও সংশোধন

| Isolated lock | Python | Torch ও মূল library |
|---|---|---|
| Modern | 3.11 সিরিজ | Torch 2.7.1+cpu, Transformers 5.22.2, Diffusers 0.43.0, Accelerate 1.15.0, bitsandbytes 0.50.2 |
| Media | 3.11 সিরিজ | Torch 2.7.1+cpu, Transformers 4.57.1, Diffusers 0.36.0, Accelerate 1.11.0 |
| Speech | 3.11 সিরিজ | Torch ও TorchAudio 2.5.1+cpu, Transformers 4.46.1, Parler TTS 0.2.3, SoundFile 0.14.0 |

Host Python 3.11.18 দিয়ে **৩১টি import/symbol probe** সফল। CPU tensor operation, dependency compatibility checks এবং actual FFmpeg/FFprobe দিয়ে synthetic H.264/AAC encode ও inspect সফল। তিনটি materialized host prefix-এর exact package, file, source ও ABI receipt যাচাই হয়েছে। চূড়ান্ত **১২২টি স্বতন্ত্র software contract test (১৪৩টি invocation)** সফল। GitHub-এর kernel startup প্রমাণ আলাদা।

- TorchAudio 2.11.0 original speech stack-এ CUDA 13 library খুঁজে ব্যর্থ হয়েছিল। Torch 2.5.1-এর সঙ্গে TorchAudio 2.5.1 pin করার পর TorchAudio ও Parler import সফল।
- বাস্তব wheels-এ শূন্য-বাইট package files পাওয়া গেছে। Runtime manifest এখন ওই ফাইলের exact size ও hash মেলায়। Native model bundle-এ empty component rejection বহাল।
- Vendored metadata পুরো file manifest-এর অধীনে থাকে। Installed distribution lock এখন top-level site metadata দেখে এবং সেখানে duplicate প্রত্যাখ্যান করে।
- Prefix seal করার আগে wheel-এর bytecode বাদ দেওয়া হয়েছে। Linux ABI resolution copied prefix থেকেই করা হয়। Qwen 3.6 config-এর registry Git blob hash মিলে গেছে এবং config-এ worker-এর ব্যবহৃত `Qwen3_5ForConditionalGeneration` class-ই নির্ধারিত।

## GPU ও বাকি কাজ

CPU wheels-এর CUDA build metadata ছিল `null`। ভবিষ্যৎ approved GPU stack-এ exact Torch/TorchAudio CUDA wheel pair, driver range, CUDA visibility, compute capability, NF4 native kernels ও BF16 operation যাচাই প্রয়োজন। CUDA build metadata-র পরে device startup, reviewed local loaders, host RAM/VRAM peak, CPU offload, decoder/encoder compatibility এবং unload মাপতে হবে। FlashAttention অনুপস্থিত হলে প্রতিটি selected adapter-এর অনুমোদিত attention path যাচাই করতে হবে। LTX auxiliary hash, reviewed source এবং অসম্পূর্ণ native dependency closure-গুলো CPU পর্যায়েই সমাধানযোগ্য বা বাহ্যিক evidence-এর অপেক্ষায়।

[PyTorch-এর প্রকাশিত wheel matrix](https://pytorch.org/get-started/previous-versions/) · [NVIDIA CUDA driver compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/) · [bitsandbytes hardware support](https://huggingface.co/docs/bitsandbytes/main/en/installation)

GPU inference, model-weight download, license acceptance ও deployment এই কাজের বাইরে ছিল। [Commands ও পুনরুৎপাদন](COMMANDS.md)

[সফল GitHub Actions runtime run](https://github.com/REDPADSTUDIO-UX/blank-app/actions/runs/44922713868) · [স্বতন্ত্র software contract IDs](contract-test-ids.json)
