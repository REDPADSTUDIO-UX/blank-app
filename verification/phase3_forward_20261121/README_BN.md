# আগের অনুমোদিত benchmark-এর প্রকৃত evidence সংরক্ষণ

এই outputs বর্তমান 21-agent synchronization অনুরোধের **আগের** অনুমোদিত Phase 3 forward-execution কাজের। Synchronization task-এ নতুন inference, GPU execution বা download করা হয়নি। Notebook থেকে আগে সম্পন্ন output পড়ে সংরক্ষণ করা হয়েছে; কোনো request পুনরায় submit করা হয়নি।

- Source checkpoint: `e39752502f7de12777ff44e461cfd07ab0419f19`।
- `actual_export.json`: exact request, raw HTTP responses, prompt/output hashes, timing, independent call reservations, tokenizer preflight, runtime checks and server shutdown evidence। SHA256: `91d11ab921d1b976ac2f9ea21ef33ba01e63d048e72134c74ca4369ded234265`।
- `cpu_validation.json`: original pure parser/validator দিয়ে নতুন outputs-এর CPU-only validation। পুরোনো test suite পুনরায় চালানো হয়নি।
- Act 2 exact-template preflight: 2473 prompt + 1536 reserved output = 4009/4096 tokens; margin 87। এটি generation নয়; Act 2 retry submit করা হয়নি। Story ledger অপরিবর্তিত: 9/11 consumed, 2 remaining।
- Original standalone GGUF benchmark arm: Director delegation response technical PASS; 874 output tokens, 26.27 seconds। Script emotional-confrontation response `length` termination, invalid/truncated JSON, technical FAIL; 1024 output tokens, 33.17 seconds।
- Independent new model calls: 2; Story calls: 0। Romantic-chemistry case submit করা হয়নি। Owned servers stopped।
- Selected YouTube NF4 benchmark-এর পরিবর্তে GGUF benchmark-কে গণনা করা হয়নি। Music/Voice media generation হয়নি।

Director-এর schema pass পেশাগত নির্দেশনার মান প্রমাণ করে না। Script response-এ পুনরাবৃত্তি ও অস্বাভাবিক বাংলা রয়েছে; truncated output মেরামত করা হয়নি। Independent human review এবং owner artistic acceptance **PENDING**। কোনো model production-ready ঘোষণা করা হয়নি।
