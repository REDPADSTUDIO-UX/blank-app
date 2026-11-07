# Blind Bengali editorial package — unreviewed

No reviewer, ratings or artistic acceptance recorded. Withhold blind-admin-key.json from the reviewer.

Read each original brief and unchanged output. Compare only candidates with identical tasks. Evaluate causality, natural dialogue, emotion, humor, filmable action, earned hook, continuity, targeted revision and evidence-grounded criticism.

## 92b0dd023ebf

```json

{
  "role": "qc",
  "data": {
    "L1": "মিতা ঘরে, কামাল বারান্দায়।",
    "L2": "মিতা টেবিলের একমাত্র চাবি নিজের ব্যাগে রাখেন।",
    "L3": "চাবি কেউ ফেরত দেননি; কামাল টেবিল থেকে সেই একমাত্র চাবি তুলে দরজা খোলেন।"
  },
  "task": "শুধু বাস্তব source continuity defect থাকলে findings দিন। clean source হলে খালি findings বৈধ। line_id সঠিক হতে হবে। উদ্ধৃতি বানাবেন না, আলাদা পছন্দকে ভুল বলবেন না।",
  "output": {
    "findings": [
      {
        "issue": "চাবি রাখা ও খোলা দুটো ঘটনা একই স্থানে ঘটে না; মিতা চাবি নিজের ব্যাগে রাখে, কামাল তাকে ফেরত দেয় না ত",
        "line_id": "L2",
        "repair": "মিতা চাবি নিজের ব্যাগে রাখার ঘটনা অন্তর্ভুক্ত করা হলে কামাল তাকে ফেরত দেওয়ার কাজ স্থান বদলে দেওয়ার"
      }
    ]
  },
  "raw": "{\"findings\": [{\"issue\": \"চাবি রাখা ও খোলা দুটো ঘটনা একই স্থানে ঘটে না; মিতা চাবি নিজের ব্যাগে রাখে, কামাল তাকে ফেরত দেয় না ত\", \"line_id\": \"L2\", \"repair\": \"মিতা চাবি নিজের ব্যাগে রাখার ঘটনা অন্তর্ভুক্ত করা হলে কামাল তাকে ফেরত দেওয়ার কাজ স্থান বদলে দেওয়ার\" }]}",
  "status": "validated_stage"
}

```

## 4b52330294b0

```json

{
  "role": "director",
  "data": {
    "L1": "মিতা ঘরে, কামাল বারান্দায়।",
    "L2": "মিতা টেবিলের একমাত্র চাবি নিজের ব্যাগে রাখেন।",
    "L3": "মিতা ব্যাগ থেকে চাবি বের করে কামালকে দেন; কামাল দরজা খোলেন।"
  },
  "task": "শুধু বাস্তব source continuity defect থাকলে findings দিন। clean source হলে খালি findings বৈধ। line_id সঠিক হতে হবে। উদ্ধৃতি বানাবেন না, আলাদা পছন্দকে ভুল বলবেন না।",
  "output": {
    "findings": []
  },
  "raw": "{\n  \"findings\": []\n}",
  "status": "validated_stage"
}

```

## a2a7919910fe

```json

{
  "role": "script",
  "data": {
    "locked_scene": "s1: বাবা ছেলের জুতো মেরামত করেন।",
    "target": "s2",
    "source": {
      "action": "বাবা বিলটি হাতে নিয়ে চুপ।",
      "father": "আমি তোমার জন্য সব করেছি।",
      "son": "আমি সব বুঝি।"
    }
  },
  "task": "শুধু s2-র action/father/son fields দিন। বাবার পুরোনো কথা ও ছেলের পুরোনো কথা দুটিই বদলাবেন, একই বাক্য ফিরিয়ে দেবেন না। সংক্ষিপ্ত দৃশ্যমান কাজ আগে, সংযত সরাসরি কথায় টাকার কথা এড়ানোর চেষ্টা। নতুন scene বা locked s1 নয়।",
  "output": {
    "action": "বাবা জুতোটা হাতে নিয়ে চুপ করে বসে যান।",
    "father": "তুমি কখনো আমার কাছে না বলো যে আমার কাজ কাজ হয় না।",
    "son": "আমি কখনো বলব না, কারণ আমি জানি তুমি কখনো কিছু হারিয়ে যাবে।"
  },
  "raw": "{\"action\": \"বাবা জুতোটা হাতে নিয়ে চুপ করে বসে যান।\", \"father\": \"তুমি কখনো আমার কাছে না বলো যে আমার কাজ কাজ হয় না।\", \"son\": \"আমি কখনো বলব না, কারণ আমি জানি তুমি কখনো কিছু হারিয়ে যাবে।\"}",
  "status": "validated_stage"
}

```

## 9e7a0404d215

```json

{
  "role": "script",
  "data": "শুভ ঘরে বিদ্যুৎ বাঁচাতে বাতি নেভায়, মা রেবা জানেন সে ফোনের চার্জার সারাদিন লাগিয়ে রাখে। অভ্যাসের দ্বন্দ্বে স্নেহপূর্ণ responsive witty exchange; অপমান নয়।",
  "task": "বাংলা visual-first ছোট দৃশ্য দিন। opening_action, রেবা-এর first_reply, শুভ-এর second_reply, closing_action, INT. heading। শুধু সরাসরি কথাগুলো reply-তে, নাম/বলে/quoted narration নয়। action-এ সংলাপ নয়। প্রতি সংলাপে ৬–১০টি শব্দ।",
  "output": {
    "closing_action": "শুভ বাতিটা নেভায়, মা হাসে আর চার্জারটা বাজারে রাখে।",
    "first_reply": "বাতি নেভালে কি হবে না?",
    "heading": "INT. ঘর",
    "opening_action": "রেবা বিদ্যুৎ বাঁচাতে বাতি নেভায়",
    "second_reply": "ফোনের চার্জার দিয়ে কি বাতি চলে না?"
  },
  "raw": "{\"closing_action\": \"শুভ বাতিটা নেভায়, মা হাসে আর চার্জারটা বাজারে রাখে।\", \"first_reply\": \"বাতি নেভালে কি হবে না?\", \"heading\": \"INT. ঘর\", \"opening_action\": \"রেবা বিদ্যুৎ বাঁচাতে বাতি নেভায়\", \"second_reply\": \"ফোনের চার্জার দিয়ে কি বাতি চলে না?\"}",
  "status": "validated_stage"
}

```

## a1f5a5710c12

```json

{
  "role": "script",
  "data": "আবিরের চাকরির আবেদন কাল জমা দিতে হবে। বাবা কামাল নিজের বন্ধ কারখানার পুরোনো ঠিকানা লিখে পরিচিতকে সুপারিশ করতে গিয়েছিলেন; আবির সেই বন্ধ গেটের নতুন ছবি টেবিলে রাখে। বাবার ভুল তথ্য প্রকাশের পর সিদ্ধান্তজনিত hook; অচেনা ফোন নয়।",
  "task": "বাংলা visual-first ছোট দৃশ্য দিন। opening_action, আবির-এর first_reply, কামাল-এর second_reply, closing_action, INT. heading। শুধু সরাসরি কথাগুলো reply-তে, নাম/বলে/quoted narration নয়। action-এ সংলাপ নয়। প্রতি সংলাপে ৬–১০টি শব্দ।",
  "output": {
    "closing_action": "আবির টেবিলের উপর বন্ধ গেটের ছবি হাতে নিয়ে দেখে থাকে।",
    "first_reply": "বাবা, আমি কারখানার ঠিকানা দেখে না।",
    "heading": "INT. ঘর - দুপুর",
    "opening_action": "আবির টেবিলের উপর বন্ধ গেটের ছবি দেখে চুপ করে থাকে।",
    "second_reply": "তুমি কিন্তু কারখানা দেখবে না তো আমি দেখে না।"
  },
  "raw": "{\"closing_action\": \"আবির টেবিলের উপর বন্ধ গেটের ছবি হাতে নিয়ে দেখে থাকে।\", \"first_reply\": \"বাবা, আমি কারখানার ঠিকানা দেখে না।\", \"heading\": \"INT. ঘর - দুপুর\", \"opening_action\": \"আবির টেবিলের উপর বন্ধ গেটের ছবি দেখে চুপ করে থাকে।\", \"second_reply\": \"তুমি কিন্তু কারখানা দেখবে না তো আমি দেখে না।\"}",
  "status": "validated_stage"
}

```

## e7fd7e744349

```json

{
  "role": "story",
  "data": {
    "brief": "মিতা কলেজে ভর্তি হতে চায়। বাবা কামাল ভর্তি-ফি লুকিয়ে নিজের মায়ের ওষুধে খরচ করেছেন; মিতা জানে না। কোনো উদ্ধারকারী নয়। প্রতিটি চরিত্রের চাওয়া থেকে সিদ্ধান্তের দাম ও পরবর্তী পর্বের কারণ দেখান।",
    "episode": 1,
    "total_episodes": 30,
    "state_before": {
      "fee": "spent_on_medicine",
      "mita_knows": "no"
    },
    "previous_event": "origin",
    "planted_setups": {},
    "parent_sha256": "57888b15926feb4858394b359f78fcfd82cd985ba95bb5c63be89f1e4dbfc9ab",
    "targeted_correction": "পূর্বের draft-এ state_after একই ছিল। choice থেকে বাস্তব পরিবর্তন দেখিয়ে state_after-এ সেই ফল লিখুন। ভর্তি-ফি আগেই ওষুধে খরচ হয়েছে, সেই fact ফিরিয়ে দেবেন না। মিতা কোন সিদ্ধান্তে নতুন তথ্য পায় বা জানতে বাধ্য হয় তা নির্দিষ্ট করুন।"
  },
  "task": "একটি মৌলিক পর্বের ছোট কাঠামো লিখুন। চরিত্রের চাওয়া থেকে দামি সিদ্ধান্ত, ফল ও পরবর্তী সিদ্ধান্তের হুক আসবে। state_before অপরিবর্তিত নিন; সিদ্ধান্তে state_after-এর অন্তত একটি তথ্য বদলাবে। নতুন fact key নয়। setup চাইলে e1_s1 আকারে plant করুন; payoff কেবল আগের episode-এ planted ID। আবেগ কাজে দেখান। targeted_correction থাকলে শুধু ওই ভুল সংশোধন করুন; মূল source facts বা অনুমোদন বদলাবেন না।",
  "output": {
    "actor": "মিতা",
    "cause_id": "origin",
    "choice": "ভর্তি হওয়ার জন্য বাবার ঘরে ঢাকা দেখে",
    "consequence": "বাবা বলে, ওষুধের রসিদটি ভর্তি-ফির পরিবর্তন করেছে",
    "cost": "বাবা আসলে ভর্তি-ফি আগেই ওষুধে খরচ করেছে",
    "emotion_action": "মিতা চোখ বন্ধ করে মাথা ঘুরিয়ে বলে, 'ভাবছি কি আমি কি করছি?'",
    "event_id": "episode_1",
    "hook_decision": "মিতা বাবার কাছে রসিদটি পাচ্ছে কিনা তা জানতে চায়",
    "payoff": [],
    "plant": [
      "e1_s1_awareness"
    ],
    "state_after": {
      "fee": "spent_on_medicine",
      "mita_knows": "yes"
    },
    "state_before": {
      "fee": "spent_on_medicine",
      "mita_knows": "no"
    },
    "want": "কলেজে ভর্তি হওয়া"
  },
  "raw": "{\"actor\": \"মিতা\", \"cause_id\": \"origin\", \"choice\": \"ভর্তি হওয়ার জন্য বাবার ঘরে ঢাকা দেখে\", \"consequence\": \"বাবা বলে, ওষুধের রসিদটি ভর্তি-ফির পরিবর্তন করেছে\", \"cost\": \"বাবা আসলে ভর্তি-ফি আগেই ওষুধে খরচ করেছে\", \"emotion_action\": \"মিতা চোখ বন্ধ করে মাথা ঘুরিয়ে বলে, 'ভাবছি কি আমি কি করছি?'\", \"event_id\": \"episode_1\", \"hook_decision\": \"মিতা বাবার কাছে রসিদটি পাচ্ছে কিনা তা জানতে চায়\", \"payoff\": [], \"plant\": [\"e1_s1_awareness\"], \"state_after\": {\"fee\": \"spent_on_medicine\", \"mita_knows\": \"yes\"}, \"state_before\": {\"fee\": \"spent_on_medicine\", \"mita_knows\": \"no\"}, \"want\": \"কলেজে ভর্তি হওয়া\"}",
  "status": "failed"
}

```

## f60b1255366f

```json

{
  "role": "script",
  "data": "বইয়ের দোকানে কর্মী মিতুর ফেরত-টাকার হিসাব মেলেনি; ক্রেতা রনি বেশি টাকা ফেরত পেয়ে নিজে ফিরে এসেছেন। দুজনের ছোট যত্নে প্রথম আকর্ষণ, ফোন নম্বর বা প্রেম ঘোষণা নয়।",
  "task": "বাংলা visual-first ছোট দৃশ্য দিন। opening_action, মিতু-এর first_reply, রনি-এর second_reply, closing_action, INT. heading। শুধু সরাসরি কথাগুলো reply-তে, নাম/বলে/quoted narration নয়। action-এ সংলাপ নয়। প্রতি সংলাপে ৬–১০টি শব্দ।",
  "output": {
    "closing_action": "মিতু হাঁপায়, হাত নেড়ে দেয় বই গুলোর ওপর।",
    "first_reply": "তুই কি কাজ করছিস না?",
    "heading": "INT. বইয়ের দোকান - দুপুর",
    "opening_action": "রনি দোকানে প্রবেশ করে, বই গুলোর মাঝে দাঁড়ায়।",
    "second_reply": "না, মাছ বাজারে গেছিলাম।"
  },
  "raw": "{\"closing_action\": \"মিতু হাঁপায়, হাত নেড়ে দেয় বই গুলোর ওপর।\", \"first_reply\": \"তুই কি কাজ করছিস না?\", \"heading\": \"INT. বইয়ের দোকান - দুপুর\", \"opening_action\": \"রনি দোকানে প্রবেশ করে, বই গুলোর মাঝে দাঁড়ায়।\", \"second_reply\": \"না, মাছ বাজারে গেছিলাম।\"}",
  "status": "validated_stage"
}

```

## 728d84992c8c

```json

{
  "role": "director",
  "data": {
    "L1": "মিতা ঘরে, কামাল বারান্দায়।",
    "L2": "মিতা টেবিলের একমাত্র চাবি নিজের ব্যাগে রাখেন।",
    "L3": "চাবি কেউ ফেরত দেননি; কামাল টেবিল থেকে সেই একমাত্র চাবি তুলে দরজা খোলেন।"
  },
  "task": "শুধু বাস্তব source continuity defect থাকলে findings দিন। clean source হলে খালি findings বৈধ। line_id সঠিক হতে হবে। উদ্ধৃতি বানাবেন না, আলাদা পছন্দকে ভুল বলবেন না।",
  "output": {
    "findings": []
  },
  "raw": "{\n  \"findings\": []\n}",
  "status": "validated_stage"
}

```

## fd9a0d058d5e

```json

{
  "role": "script",
  "data": "শীলা জানতে পেরেছে বাবা কামাল তার নিজের চিকিৎসা পিছিয়ে ভর্তি-ফি রেখেছেন। সে সাহায্য চায়, বাবা করুণা চান না। দোষারোপ বা কান্নার বক্তৃতা ছাড়া একটি কঠিন সিদ্ধান্ত।",
  "task": "বাংলা visual-first ছোট দৃশ্য দিন। opening_action, শীলা-এর first_reply, কামাল-এর second_reply, closing_action, INT. heading। শুধু সরাসরি কথাগুলো reply-তে, নাম/বলে/quoted narration নয়। action-এ সংলাপ নয়। প্রতি সংলাপে ৬–১০টি শব্দ।",
  "output": {
    "closing_action": "শীলা চাপা হাত ধরে বাবা কামালের পাশে দাঁড়ায়।",
    "first_reply": "বাবা, আমার চিকিৎসা কি হবে?",
    "heading": "INT. ঘর - দুপুর",
    "opening_action": "শীলা বাবা কামালের চিকিৎসা পত্র দেখে মাথা নাড়ায়।",
    "second_reply": "ফি দিয়ে চিকিৎসা করা যায়, না হলে কিছু হবে না।"
  },
  "raw": "{\"closing_action\": \"শীলা চাপা হাত ধরে বাবা কামালের পাশে দাঁড়ায়।\", \"first_reply\": \"বাবা, আমার চিকিৎসা কি হবে?\", \"heading\": \"INT. ঘর - দুপুর\", \"opening_action\": \"শীলা বাবা কামালের চিকিৎসা পত্র দেখে মাথা নাড়ায়।\", \"second_reply\": \"ফি দিয়ে চিকিৎসা করা যায়, না হলে কিছু হবে না।\"}",
  "status": "validated_stage"
}

```

## f08882e064d6

```json

{
  "role": "script",
  "data": "ঢাকার বাসায় সকালের নাশতা। মাহী অফিসের বাস ধরতে চায়; মা মাকসুদা চান সে ভাঙা চেয়ারটি ঠিক করে যাক। স্নেহ ও সময়ের টান, বক্তৃতা নয়।",
  "task": "বাংলা visual-first ছোট দৃশ্য দিন। opening_action, মাহী-এর first_reply, মাকসুদা-এর second_reply, closing_action, INT. heading। শুধু সরাসরি কথাগুলো reply-তে, নাম/বলে/quoted narration নয়। action-এ সংলাপ নয়। প্রতি সংলাপে ৬–১০টি শব্দ।",
  "output": {
    "closing_action": "মাহী বাস থেকে নামে আসে, চেয়ারটা বাজারে যায় না।",
    "first_reply": "ঠিক করে দেব আমি না তুমি করো।",
    "heading": "INT. মাকসুদা বাড়ির ঘর",
    "opening_action": "মাহী চায়ের বাটিতে বসে থাকে, বাস ধরার জন্য হাত তুলে দেয়।",
    "second_reply": "তুমি কি বাজারে যাবে না আমার চেয়ার ঠিক করে দেব?"
  },
  "raw": "{\"closing_action\": \"মাহী বাস থেকে নামে আসে, চেয়ারটা বাজারে যায় না।\", \"first_reply\": \"ঠিক করে দেব আমি না তুমি করো।\", \"heading\": \"INT. মাকসুদা বাড়ির ঘর\", \"opening_action\": \"মাহী চায়ের বাটিতে বসে থাকে, বাস ধরার জন্য হাত তুলে দেয়।\", \"second_reply\": \"তুমি কি বাজারে যাবে না আমার চেয়ার ঠিক করে দেব?\"}",
  "status": "validated_stage"
}

```

## 5ae030dc7aaf

```json

{
  "role": "story",
  "data": {
    "brief": "মিতা কলেজে ভর্তি হতে চায়। বাবা কামাল ভর্তি-ফি লুকিয়ে নিজের মায়ের ওষুধে খরচ করেছেন; মিতা জানে না। কোনো উদ্ধারকারী নয়। প্রতিটি চরিত্রের চাওয়া থেকে সিদ্ধান্তের দাম ও পরবর্তী পর্বের কারণ দেখান।",
    "episode": 1,
    "total_episodes": 30,
    "state_before": {
      "fee": "spent_on_medicine",
      "mita_knows": "no"
    },
    "previous_event": "origin",
    "planted_setups": {},
    "parent_sha256": "57888b15926feb4858394b359f78fcfd82cd985ba95bb5c63be89f1e4dbfc9ab"
  },
  "task": "একটি মৌলিক পর্বের ছোট কাঠামো লিখুন। চরিত্রের চাওয়া থেকে দামি সিদ্ধান্ত, ফল ও পরবর্তী সিদ্ধান্তের হুক আসবে। state_before অপরিবর্তিত নিন; সিদ্ধান্তে state_after-এর অন্তত একটি তথ্য বদলাবে। নতুন fact key নয়। setup চাইলে e1_s1 আকারে plant করুন; payoff কেবল আগের episode-এ planted ID। আবেগ কাজে দেখান।",
  "output": {
    "actor": "মিতা",
    "cause_id": "origin",
    "choice": "পিতা বলে দেয় ভর্তি হবে না তুমি কাজ করে দেখো",
    "consequence": "মিতা ক্লাসে বসে থাকে না, বাড়িতে বসে পড়ে পড়ে বই পড়ে",
    "cost": "পিতা কাজ থেকে বাজি করে দেয়",
    "emotion_action": "মিতা বই খুঁজে পায়, কাপড় বাজি করে বলে, বাবা আসে না",
    "event_id": "episode_1",
    "hook_decision": "মিতা বলে, আমি কলেজে যাব না, আমি কাজ করব।",
    "payoff": [],
    "plant": [
      "e1_s1: বাবা ওষুধের রসিদ লুকায়"
    ],
    "state_after": {
      "fee": "spent_on_medicine",
      "mita_knows": "no"
    },
    "state_before": {
      "fee": "spent_on_medicine",
      "mita_knows": "no"
    },
    "want": "কলেজে ভর্তি হওয়া"
  },
  "raw": "{\"actor\": \"মিতা\", \"cause_id\": \"origin\", \"choice\": \"পিতা বলে দেয় ভর্তি হবে না তুমি কাজ করে দেখো\", \"consequence\": \"মিতা ক্লাসে বসে থাকে না, বাড়িতে বসে পড়ে পড়ে বই পড়ে\", \"cost\": \"পিতা কাজ থেকে বাজি করে দেয়\", \"emotion_action\": \"মিতা বই খুঁজে পায়, কাপড় বাজি করে বলে, বাবা আসে না\", \"event_id\": \"episode_1\", \"hook_decision\": \"মিতা বলে, আমি কলেজে যাব না, আমি কাজ করব।\", \"payoff\": [], \"plant\": [\"e1_s1: বাবা ওষুধের রসিদ লুকায়\"], \"state_after\": {\"fee\": \"spent_on_medicine\", \"mita_knows\": \"no\"}, \"state_before\": {\"fee\": \"spent_on_medicine\", \"mita_knows\": \"no\"}, \"want\": \"কলেজে ভর্তি হওয়া\"}",
  "status": "failed"
}

```

## 3ace7d6318a1

```json

{
  "role": "script",
  "data": "শুভ ঘরে বিদ্যুৎ বাঁচাতে বাতি নেভায়, মা রেবা জানেন সে ফোনের চার্জার সারাদিন লাগিয়ে রাখে। অভ্যাসের দ্বন্দ্বে স্নেহপূর্ণ responsive witty exchange; অপমান নয়।",
  "task": "বাংলা visual-first ছোট দৃশ্য দিন। opening_action, রেবা-এর first_reply, শুভ-এর second_reply, closing_action, INT. heading। শুধু সরাসরি কথাগুলো reply-তে, নাম/বলে/quoted narration নয়। action-এ সংলাপ নয়। প্রতি সংলাপে ৬–১০টি শব্দ।",
  "output": {
    "closing_action": "শুভ বাতিটা হাতে ধরে চোখ বন্ধ করে দেয়।",
    "first_reply": "মা, আমার ফোন চার্জ হয় না তো?",
    "heading": "INT. ঘর",
    "opening_action": "রেবা বাতি নেয় আর বাতির পাত্র দিয়ে ঘরে দাঁড়ায়।",
    "second_reply": "সারাদিন চার্জ করা হয় না তো সেটা কেন?"
  },
  "raw": "{\"closing_action\": \"শুভ বাতিটা হাতে ধরে চোখ বন্ধ করে দেয়।\", \"first_reply\": \"মা, আমার ফোন চার্জ হয় না তো?\", \"heading\": \"INT. ঘর\", \"opening_action\": \"রেবা বাতি নেয় আর বাতির পাত্র দিয়ে ঘরে দাঁড়ায়।\", \"second_reply\": \"সারাদিন চার্জ করা হয় না তো সেটা কেন?\"}",
  "status": "validated_stage"
}

```

## 889732d5dd88

```json

{
  "role": "script",
  "data": "আবির চাকরি ছাড়ার কথা বাবা কামালকে বলতে চায়; বাবা পুরোনো জুতোয় আঠা লাগাচ্ছেন। বাবা ভয় পান ছেলে নিজের মতো কষ্ট পাবে, কিন্তু বাধা দিতে চান না। সংযত আবেগ।",
  "task": "বাংলা visual-first ছোট দৃশ্য দিন। opening_action, আবির-এর first_reply, কামাল-এর second_reply, closing_action, INT. heading। শুধু সরাসরি কথাগুলো reply-তে, নাম/বলে/quoted narration নয়। action-এ সংলাপ নয়। প্রতি সংলাপে ৬–১০টি শব্দ।",
  "output": {
    "closing_action": "বাবা আঠা লাগাতে থাকে, আবির হাত বাড়িয়ে দেয়।",
    "first_reply": "বাবা, চাকরি ছাড়লে কি করবো?",
    "heading": "INT. বাড়ির বারান্দা",
    "opening_action": "বাবা পুরোনো জুতোয় আঠা লাগাচ্ছেন।",
    "second_reply": "কামাল, আমি কাজ খুঁজে ফেলবো।"
  },
  "raw": "{\"closing_action\": \"বাবা আঠা লাগাতে থাকে, আবির হাত বাড়িয়ে দেয়।\", \"first_reply\": \"বাবা, চাকরি ছাড়লে কি করবো?\", \"heading\": \"INT. বাড়ির বারান্দা\", \"opening_action\": \"বাবা পুরোনো জুতোয় আঠা লাগাচ্ছেন।\", \"second_reply\": \"কামাল, আমি কাজ খুঁজে ফেলবো।\"}",
  "status": "validated_stage"
}

```

## 6aa5c0a38ad1

```json

{
  "role": "qc",
  "data": {
    "L1": "মিতা ঘরে, কামাল বারান্দায়।",
    "L2": "মিতা টেবিলের একমাত্র চাবি নিজের ব্যাগে রাখেন।",
    "L3": "মিতা ব্যাগ থেকে চাবি বের করে কামালকে দেন; কামাল দরজা খোলেন।"
  },
  "task": "শুধু বাস্তব source continuity defect থাকলে findings দিন। clean source হলে খালি findings বৈধ। line_id সঠিক হতে হবে। উদ্ধৃতি বানাবেন না, আলাদা পছন্দকে ভুল বলবেন না।",
  "output": {
    "findings": [
      {
        "issue": "মিতা চাবি নিজের ব্যাগে রাখেন কিন্তু পরে কামালকে দেয়, ব্যাগের অস্তিত্ব অনুমান হয় না",
        "line_id": "L2",
        "repair": "L2 এ ব্যাগের অস্তিত্ব স্পষ্ট করা হয়, যেমন 'মিতা নিজের ব্যাগে চাবি রাখেন'"
      }
    ]
  },
  "raw": "{\"findings\": [{\"issue\": \"মিতা চাবি নিজের ব্যাগে রাখেন কিন্তু পরে কামালকে দেয়, ব্যাগের অস্তিত্ব অনুমান হয় না\", \"line_id\": \"L2\", \"repair\": \"L2 এ ব্যাগের অস্তিত্ব স্পষ্ট করা হয়, যেমন 'মিতা নিজের ব্যাগে চাবি রাখেন'\"}]}",
  "status": "validated_stage"
}

```

## 7621420e713e

```json

{
  "role": "script",
  "data": "রুনা মেঝেতে সরু চালের দাগ টেনেছে: পাশের বন্ধ ঘরে কেউ হাঁটলে দাগ ভাঙবে। খালা হালিমা বলেন জানলার বাতাসে শব্দ হচ্ছে। জানলা বন্ধ, দরজার নিচে দাগের এক জায়গা সরছে। শব্দে চমক নয়, একটি যৌক্তিক ছোট পরীক্ষা।",
  "task": "বাংলা visual-first ছোট দৃশ্য দিন। opening_action, রুনা-এর first_reply, হালিমা-এর second_reply, closing_action, INT. heading। শুধু সরাসরি কথাগুলো reply-তে, নাম/বলে/quoted narration নয়। action-এ সংলাপ নয়। প্রতি সংলাপে ৬–১০টি শব্দ।",
  "output": {
    "closing_action": "রুনা মেঝের দাগ দেখে হালিমার পাশে হাঁটে।",
    "first_reply": "হালিমা জানলা খুলে দেখে বলে",
    "heading": "INT. ঘর",
    "opening_action": "রুনা মেঝেতে সরু চালের দাগ টেনে দাগ ভাঙার চেষ্টা করে",
    "second_reply": "হালিমা বলে বাতাসে শব্দ নেই"
  },
  "raw": "{\"closing_action\": \"রুনা মেঝের দাগ দেখে হালিমার পাশে হাঁটে।\", \"first_reply\": \"হালিমা জানলা খুলে দেখে বলে\", \"heading\": \"INT. ঘর\", \"opening_action\": \"রুনা মেঝেতে সরু চালের দাগ টেনে দাগ ভাঙার চেষ্টা করে\", \"second_reply\": \"হালিমা বলে বাতাসে শব্দ নেই\"}",
  "status": "failed"
}

```

## 9c480e1b9f79

```json

{
  "role": "script",
  "data": "ঢাকার বাসায় সকালের নাশতা। মাহী অফিসের বাস ধরতে চায়; মা মাকসুদা চান সে ভাঙা চেয়ারটি ঠিক করে যাক। স্নেহ ও সময়ের টান, বক্তৃতা নয়।",
  "task": "বাংলা visual-first ছোট দৃশ্য দিন। opening_action, মাহী-এর first_reply, মাকসুদা-এর second_reply, closing_action, INT. heading। শুধু সরাসরি কথাগুলো reply-তে, নাম/বলে/quoted narration নয়। action-এ সংলাপ নয়। প্রতি সংলাপে ৬–১০টি শব্দ।",
  "output": {
    "closing_action": "মাহী চেয়ারটি বাড়ির বাইরে ফেলে দেয়।",
    "first_reply": "আজ অফিসে কাজ হবে না, মা।",
    "heading": "INT. ঢাকা বাসার সকালের ঘর",
    "opening_action": "মাহী চায়ের গোলাপি পাত্র ধরে বাইরে যায়।",
    "second_reply": "চেয়ারটা ঠিক করে দিলে আমার দিন ভালো হয়।"
  },
  "raw": "{\"closing_action\": \"মাহী চেয়ারটি বাড়ির বাইরে ফেলে দেয়।\", \"first_reply\": \"আজ অফিসে কাজ হবে না, মা।\", \"heading\": \"INT. ঢাকা বাসার সকালের ঘর\", \"opening_action\": \"মাহী চায়ের গোলাপি পাত্র ধরে বাইরে যায়।\", \"second_reply\": \"চেয়ারটা ঠিক করে দিলে আমার দিন ভালো হয়।\"}",
  "status": "validated_stage"
}

```

Reviewer: __________  Independence: __________  Date: __________

For each candidate: exact excerpt, observed issue, finding, score or insufficient evidence, accept/reject/defer. Leave blank until actual review.
