# REDPAD — Casting Director ও Producer Control Center

শুরু: `b08f1b55e15097eddacce3e5f9caae893becde7e`। অনুমোদিত branch: `feature/video-music-editing-studio`। এই ধাপের কাজ **Casting Director + Director-কেন্দ্রিক dashboard**; নতুন model selection বা creative intelligence optimization নয়।

## বাস্তবায়িত পরিবর্তন

| অংশ | যাচাইকৃত সফটওয়্যার আচরণ |
|---|---|
| Agent registry | আগের ২০ agent অক্ষত; Casting Director যোগ করে মোট **২১**। আলাদা Hair/Makeup agent নেই। |
| Casting orchestration | বর্তমান approved Script, Character Bible ও Director source থেকে নতুন local-generation graph-এ Casting। পুরোনো ১৭-specialist fixture graph অপরিবর্তিত; নতুন graph-এ ১৮ internal specialist। |
| Casting brief | Character psychology, apparent age, appearance, performance range, voice ও chemistry requirements; persistent actor IDs ও exact image/voice reference versions। Model output কেবল proposal। |
| Director inspection | Pending casting-এর exact revision পড়ার সীমিত inspection; সেটি approved production source বলে গণ্য হয় না। বাস্তব configured local model ছাড়া AI response তৈরি হয় না। |
| Casting approval | Casting ও Director inspection-এ independent QC recommendation, Producer reason, প্রতি approved character-এর নির্দিষ্ট candidate selection, actual image ও identity rights/source যাচাই করে lock। Generic বা batch Approve দিয়ে casting lock bypass করা যায় না। |
| Media evidence | Still image দিয়ে acting/chemistry observation রেকর্ড করা যায় না; উপযুক্ত actual clip/audio evidence ও named human reviewer লাগে। Identity lock acting/voice/chemistry acceptance নয়। |
| Rights | শুধু fictional AI identity অথবা owner-attested authorized human likeness/voice। `reference_only` asset দিয়ে identity lock নিষিদ্ধ। Authorization declaration স্বয়ংক্রিয় legal verification নয়। Voice cloning engine যোগ করা হয়নি। |
| Recasting | Versioned immutable lock history; explicit recast confirmation; affected dependent tasks/shot packets stale; আগের outputs মুছে যায় না। |
| Costume/Hair/Makeup | নতুন casting-bound workflow-এ actor ID, hair, makeup, apparent age, chronological order এবং injury/sweat/rain/dirt state আবশ্যক। কারণ ছাড়া look বদল ও ভুল locked actor প্রত্যাখ্যান। |
| Shot handoff | Shot-এ locked actor ID ও exact reference versions। Costume, Storyboard, Performance, Camera ও Motion-এর lock মিলতে হবে। এই metadata lock কোনো video model-এ identity conditioning সফল হওয়ার প্রমাণ নয়। |
| Navigation | Dashboard Home এবং চারটি মূল বিভাগ: **Director Studio, Approval Desk, Channel Manager, Growth & Analytics**। মূল পৃষ্ঠায় ২১-agent management grid নেই। |
| Conversation | Project-persistent Producer instructions, actual Engine-backed Director response, exact raw simulated/local provenance, task status, locked casting ও bounded reference excerpts। Missing model হলে blocker; fabricated AI reply নয়। |
| Director delegation | Approved Director plan থেকে existing Story/Script/review/specialist queue; repeat dispatch idempotent। Long-series Story Bible→arcs→bounded outlines→compilation এবং sequence prerequisite-এর existing bridge ব্যবহার করে। পরের handoff-এ source approval দরকার। |
| Revision | Producer feedback আগে Director-এ যায়; exact task/version থাকে। Approved work বদলাতে explicit authorization; Script scene rewrite, Story episode/stage ও specialist record targets-এর বাইরে পরিবর্তন বন্ধ। Unrelated outputs অক্ষত। নতুন source version হলে পুরোনো review/approval stale। |
| Approval Desk | Evidence, previous versions, associated conversation, Approve/Request Changes/Reject, exact-version atomic milestone batch approval ও configurable grouping। Grouping QC বা source freshness বাদ দেয় না। Rejected version সাধারণ advanced approval দিয়েও bypass করা যায় না। |
| References | Multi-file upload, original file, ID/version, category, notes, source/rights, project, processing status; replace/relabel/archive history। Pinned reference বদলাতে explicit invalidation; file tampering ধরার hash checks। |
| Parsing/preview | UTF-8 TXT; bounded DOCX body text; isolated bounded PDF parser; actual image preview। Audio/video original preview উপলব্ধ হলে দেখানো হয়, semantic understanding দাবি করা হয় না। |
| Limits | ৩২ MiB/file, ২৫৬ MiB/project reference history, image ২০ megapixel, DOCX decompression ceiling, PDF process time/address-space limits। Director context-এ প্রথম ২০ active reference-এর সংক্ষিপ্ত excerpts; এটি পূর্ণ document/movie review নয়। |
| Retained workflows | Channel/database/content inventory, legacy approval/previews, Growth, read-only YouTube Connect, Storyboard/Video/production tools, Model Routes ও recovery অক্ষত। Specialist controls secondary advanced view-তে। |
| Home | Persisted projects, format, latest stage/focus, Director state, actual review/blocker counts, existing local preview counts ও project opening। কাল্পনিক completion percentage নেই। |

## পরীক্ষা ও evidence

**Final regression: ৩৯৩/৩৯৩ tests PASS** (৩৫.১০৫ সেকেন্ড)। `verification/phase1_casting_producer/`-এ final regression log ও source manifest রয়েছে। নতুন পরীক্ষায় অন্তর্ভুক্ত:

- ২১ agent, কোনো আলাদা Hair/Makeup agent নয়;
- raw reference extraction, format rejection, history, pin invalidation ও tamper prevention;
- persistent conversation, unavailable-model blocker ও real Engine delegation;
- no software-echo Director response, no hosted fallback;
- independent QC/Producer separation, atomic batch gate, rejected/stale approval prevention;
- Casting→Director inspection→QC→Producer lock→Costume/Performance→shot references→recast invalidation;
- still portrait দিয়ে acting certification প্রত্যাখ্যান;
- exact scene/episode revision scope ও unrelated approval preservation;
- actual Streamlit navigation, saved conversation, Approval Desk এবং legacy Channel/Storyboard/media workflow accessibility;
- existing ২০-agent/৫৪-output authored fixture compatibility। Historical saved evidence পরিবর্তন বা নতুন model inference করে পুনরায় তৈরি করা হয়নি। Regression tests temporary fixtures ব্যবহার করে compatibility পরীক্ষা করেছে।

**পরীক্ষার synthetic image squares, injected Director replies ও manual screenplay fixtures বাস্তব AI actor, বাস্তব creative improvement বা independent artistic acceptance-এর প্রমাণ নয়।** Test approval events স্পষ্টভাবে fixture/simulation হিসেবে চিহ্নিত।

## সীমা ও অবশিষ্ট prerequisite

1. এই assignment-এ **নতুন model inference/benchmark: ০; নতুন independent artistic review: ০**। Model configuration/availability ছাড়া Director কথোপকথন ও specialist generation blocked থাকবে। আগের দুর্বল model-কে production-ready বলা হয়নি।
2. Casting-এর actual AI actor generation, voice/performance/chemistry judgment এবং video identity conditioning-এর creative ক্ষমতা পরীক্ষিত নয়। উপযুক্ত approved local model/media, বাস্তব samples ও independent expert review দরকার। Phase 1 সেগুলোর workflow ও evidence gate যুক্ত করেছে।
3. Document parsing সীমিত। PDF text parser অনুপস্থিত/ব্যর্থ হলে UI স্পষ্ট limitation দেখায়; OCR, image semantics, full-film analysis বা automatic audio transcription যোগ করা হয়নি। ডিভাইসের বাংলা dictation দিয়ে text input দেওয়া যায়।
4. এই dashboard source ও local/test workflow যাচাই করা হয়েছে। **Render-এ deploy করা হয়নি**; live পুরোনো preview-তে পরিবর্তন নিজে থেকে আসবে না। Existing backup/restore prerequisites বহাল।
5. Human rights/source attestation ও named review record বাস্তব authorization/দক্ষতা যাচাইয়ের বিকল্প নয়। Final artistic/production acceptance owner ও independent specialist-এর দায়িত্ব।
6. বর্তমান uploaded instruction-এর শেষ অংশ সত্যিই কাটা: Section 10 শেষ হয়েছে `- Project-to`-তে। অনুপস্থিত অংশ অনুমান করে নতুন scope যোগ করা হয়নি; দৃশ্যমান দুই assignment বাস্তবায়ন করা হয়েছে।
7. Production data/schema migration নয়: নতুন tables কেবল project-local `agent_control.sqlite3` sidecar-এ additive; preserved legacy database functions বজায় আছে। এখানে production SQLite/media খোলা বা বদলানো হয়নি।

## সংরক্ষণ ও নিরাপত্তা

শুধু feature branch। `main` পরিবর্তন/merge নয়। Read-only যাচাইয়ে তিনটি Render service-এর auto-deploy `no` / trigger `off` ছিল। কোনো deploy, restart, production migration, নতুন model download/GPU/cloud resource, paid API, OAuth scope expansion বা YouTube upload/publish/schedule করা হয়নি।
