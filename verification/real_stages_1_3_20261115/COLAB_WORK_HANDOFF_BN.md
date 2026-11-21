# ChatGPT Work handoff — existing free Colab only

এই সেশনে genuine inference **০**। Attached host-এ GPU নেই। Local browser extension
control tool প্রকাশিত হয়নি; cloud browser navigation ও native browser control নির্দিষ্ট
tool error দিয়েছে। এটি Colab account-এর sign-in অবস্থা বা owner cache সম্পর্কে দাবি নয়।
`access/runtime_access.json`-এ পর্যবেক্ষণ আছে।

১. Working browser connection-সহ ChatGPT Work-এ owner-এর **বিদ্যমান** free Colab notebook
খুলুন। আগের source-এ owner notebook URL আছে, কিন্তু পুরোনো connected T4-কে live runtime
ভাববেন না। Google login বা CAPTCHA লাগলে owner নিজে official UI-তে করবেন; credentials
চ্যাটে নয়। Paid runtime, billing বা নতুন cloud resource নয়।

২. `STAGES_1_3_CACHED_MODELS_ONLY.ipynb` ordinary notebook UI-তে খুলুন। Source setup cell
শুধু owner GitHub repository-এর exact feature commit `877a475f344d85e19ea45338f3dff8d421a888e5`
নেয়; model weights বা components নয়। Notebook-এর saved execution count/output খালি।
Python/model dependencies পাল্টানো হয় না; incompatible/missing dependency হলে blocker
সংরক্ষণ করে থামুন। Source setup-এর lightweight download-কে weight approval মনে করবেন না।

৩. UI-তে actual free runtime, GPU, memory ও availability যাচাই করুন; platform না জানালে
quota unknown রাখুন। এরপরই `FREE_RUNTIME_VERIFIED=True` করুন। User-এর bounded testing
authorization বিদ্যমান; আলাদা weight download বা license acceptance অনুমোদন নেই।

৪. `/content/redpad_stages_1_3` কেবল marked research workspace। Exact cached model bundles
ও পূর্বের owner-approved research install receipts existing Studio controls দিয়ে ব্যবহার
করতে হবে। Production database অনুলিপি/খোলা নয়; model cache আছে ভেবে নতুন receipt বানানো
নয়। Receipt/bundle অনুপস্থিত থাকলে pinned repo/revision/component list দেখে **শুধু প্রয়োজনীয়
আলাদা download/license approval** চাইবেন। এই সেশনে owner runtime-এর cache দেখা যায়নি,
তাই অজানা cache-এর জন্য blind download approval চাওয়া হয়নি।

৫. Stage order: Qwen NF4 YouTube → ACE instrumental → Indic-Speak synthetic presets।
প্রতি stage-এ আগে canary A, technical checks ভালো হলে remaining samples। A পুনরায়
তৈরি নয়। YouTube সর্বোচ্চ ২ calls (B-তে adversarial request), ACE ৪×৮-second alternatives,
Indic-Speak ৬টি original short utterance। সব raw failures-সহ existing research ledger-এ
থাকে। কোনো failed/interrupted reservation automatic retry হবে না।

৬. Native Music/Voice-এর existing kernel network isolation বজায় রাখুন। Colab-এ `bwrap`
বা namespace capability unavailable হলে **ISOLATION BLOCKED**। Alternative direct worker,
hosted API, public endpoint, reverse tunnel বা isolation bypass নয়। অন্য independent stage
শুধু নিজস্ব gates পূরণ হলে এগোবে।

৭. Worker subprocess exit এবং GPU process/memory inventory যাচাই করে পরের model।
`empty_cache()`-কে একমাত্র release evidence বলা যাবে না। Existing conservative RAM/VRAM
gates অনুমতি ছাড়া কমাবেন না; 12 GiB planning value measured minimum নয়।

৮. Notebook-এর review cell genuine audio hash যাচাই করে actual playback দেখায়। Human
package খোলার সময় file না থাকলে preservation blocker; GitHub-এর template-এ audio নেই।
Music input plan ও Voice dialogue original authored text; এগুলো model-generated text
sample নয়। ACE instrumental ফলকে SFX validation বলা যাবে না। ProfessionalLab-এর
text/modality minimum বাকি থাকলে full suite complete/accepted বলা যাবে না।

৯. Runtime শেষ হওয়ার আগে notebook-এর private export cell দিয়ে actual generated media,
hashes, states ও safe worker logs owner device-এ download করুন। Download সত্যি শেষ হয়েছে
যাচাই করুন। Model/cache files বা production data archive-এ নয়। অন্য private destination
লাগলে আগে তার authorization যাচাই করুন। কোনো sharing change বা permanent Drive mount
এই notebook করে না। GitHub-এ শুধু content-reviewed lightweight manifests, safe text ও hashes।

১০. তিনজন উপযুক্ত independent reviewer-এর জন্য পৃথক package দিন; actual feedback না
পাওয়া পর্যন্ত scores/decisions ফাঁকা। Composer/Sound Designer এবং Bengali voice reviewer
শুনবেন; YouTube operations/rights reviewer generated text ও approvals দেখবেন। Owner
acceptance আলাদা। Software metric বা canary success professional pass নয়।

Raw audio unavailable অবস্থায় listening package usable দাবি করা যাবে না। Background
completion বা ভবিষ্যৎ free GPU quota পাওয়ার নিশ্চয়তা নেই।
