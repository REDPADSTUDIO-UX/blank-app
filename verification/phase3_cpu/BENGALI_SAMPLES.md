# Actual Qwen CPU Bengali samples
Original model output, including defects. Experimental only; no owner/independent human approval. No manual rewriting of these samples.

## cpu_smoke
```json
{
  "dialogue": [
    {
      "speaker": "মা",
      "text": "আজ কে বাড়িতে আসবে তুমি বলো, বাবা আজ বাড়ি ফেরে না।"
    },
    {
      "speaker": "ছেলে",
      "text": "হ্যাঁ, আমি আসব না, কারণ আমি বাবার চোখে দেখি না।"
    }
  ]
}
```

## trial_dialogue_revision
```json
{
  "dialogue": [
    {
      "speaker": "মা",
      "text": "ছেলে, আজ কে বাড়িতে আসবে তুমি বলো, বাবা আজ বাড়ি ফেরে না।"
    },
    {
      "speaker": "ছেলে",
      "text": "হ্যাঁ, আমি আসব না, কারণ মা ছেলেকে আরেকটা পরোটা দিতে চাইছেন; আমি অফিসে দেরি হচ্ছে বলে মা এর বাড়তি যত্ন নি uninterrupted আদরভরা হালকা রসিকতা করে।"
    }
  ]
}
```

## trial_dialogue_nfc
```json
{
  "dialogue": [
    {
      "speaker": "মা",
      "text": "ছেলে, আজ কে বাড়িতে আসবে তুমি বলো, বাবা আজ বাড়ি ফেরে না।"
    },
    {
      "speaker": "ছেলে",
      "text": "হ্যাঁ, আমি আসব না, কারণ আমি বাবার চোখে দেখি না।"
    }
  ]
}
```

## trial_story_nfc
```json
{
  "title": "একটা ছাতা",
  "premise": "ঢাকার বৃষ্টির সকাল। রাশে ও তানিয়া বিবাহিত। তানিয়ার চাকরির সাক্ষাৎকার, রাশেদের অফিসে জরুরি উপস্থিতি; একটি ছাতা আর সীমিত বাসভাড়া।",
  "characters": [
    {
      "name": "রাশেদ",
      "want": "অফিসে পৌঁছার জন্য নিজেকে আগে থাকা।"
    },
    {
      "name": "তানিয়া",
      "want": "চাকরির সাক্ষাৎকারে সাফল্য পাওয়া।"
    }
  ],
  "beats": [
    {
      "id": "b1",
      "action": "তানিয়া ছাতা দিয়ে বাইরে যায়।",
      "cause": "চাকরির সাক্ষাৎকারের সময় আসে।",
      "consequence": "রাশেদ বাসে থাকে এবং ছাতা দেখে হাসে।"
    },
    {
      "id": "b2",
      "action": "রাশেদ অফিসে পৌঁছায় এবং কাজের কাজ শুরু করে।",
      "cause": "বৃষ্টি আরও বেড়ে যায়।",
      "consequence": "তানিয়া বাসে থাকে এবং ছাতা নেয় না।"
    },
    {
      "id": "b3",
      "action": "রাশেদ বাড়ি ফিরে আসে এবং ছাতা দেখে বলে।",
      "cause": "তানিয়া ছাতা বাজারে কিনেছে কিনা জানে না।",
      "consequence": "তানিয়া ছাতা না দেখে বলে যে তার বাড়ি ছাতা নেই।"
    }
  ],
  "hook": "রাশেদ ছাতা দেখে হাসে, তানিয়া কিনেছে কিনা জানে না।",
  "cliffhanger": "তানিয়া বলে যে তার ছাতা নেই, কিন্তু রাশেদ ছাতা দেখে আছে যা তার বাড়িতে নেই।"
}
```

## trial_script_nfc
```json
{
  "title": "একটা ছাতা",
  "hook": {
    "image": "রাশেদ ছাতা দেখে হাসছে, তানিয়া বাড়িতে আছে কিন্তু ছাতা দেখছে না",
    "question": "তানিয়া কিনেছে ছাতা কিনা?",
    "payoff": "রাশেদ ছাতা দেখে হাসে, তানিয়া বলে যে তার ছাতা নেই"
  },
  "characters": [
    {
      "name": "রাশেদ",
      "want": "অফিসে পৌঁছার জন্য নিজেকে আগে থাকা",
      "voice": "সুস্পষ্ট, সামান্য হাসি দেখায়"
    },
    {
      "name": "তানিয়া",
      "want": "চাকরির সাক্ষাৎকারে সাফল্য পাওয়া",
      "voice": "সামান্য চাপ দেখায়, কিছু কম কথা বলে"
    }
  ],
  "scenes": [
    {
      "id": "s1",
      "heading": "INT. বাড়ির খাদি ঘর - সকাল",
      "seconds": 30,
      "objective": "তানিয়া বাইরে যাবে",
      "obstacle": "বৃষ্টি তীব্র হয়ে যাচ্ছে",
      "turn": "তানিয়া ছাতা দিয়ে বাইরে যায়",
      "consequence": "রাশেদ ছাতা দেখে হাসে",
      "beats": [
        {
          "type": "action",
          "text": "বৃষ্টি আসছে। প্লাটফর্মে ছাতা দেখা যাচ্ছে।"
        },
        {
          "type": "dialogue",
          "speaker": "তানিয়া",
          "text": "আজ কাজে পারবো না, বাইরে যাচ্ছি।"
        },
        {
          "type": "action",
          "text": "তানিয়া ছাতা দিয়ে বাইরে যায়।"
        }
      ],
      "sound": {
        "music": "সাদা পানির শব্দ",
        "sfx": "বৃষ্টির শব্দ, ছাতা কাটা"
      }
    },
    {
      "id": "s2",
      "heading": "EXT. বাড়ির সামনের দরজা - সকাল",
      "seconds": 30,
      "objective": "রাশেদ বাড়ি ফিরে আসে",
      "obstacle": "তানিয়া ছাতা না দেখে",
      "turn": "রাশেদ ছাতা দেখে বলে",
      "consequence": "তানিয়া বলে যে তার ছাতা নেই",
      "beats": [
        {
          "type": "action",
          "text": "রাশেদ বাড়ি ফিরে আসে, ছাতা দেখে।"
        },
        {
          "type": "dialogue",
          "speaker": "রাশেদ",
          "text": "এটা কি তোমার ছাতা?"
        },
        {
          "type": "dialogue",
          "speaker": "তানিয়া",
          "text": "আমার ছাতা নেই, বাড়িতে নেই।"
        }
      ],
      "sound": {
        "music": "সাদা পানির শব্দ",
        "sfx": "দরজা খুলে যায়, বৃষ্টির শব্দ"
      }
    }
  ]
}
```

## trial_director_compact
```json
{
  "strengths": [
    "Natural Bangladeshi Bengali dialogue in everyday speech patterns",
    "Clear emotional subtext through character actions without exposition",
    "Consistent use of domestic setting to ground family dynamics"
  ],
  "findings": [
    {
      "criterion": "natural Bengali dialogue",
      "quote": "ওই ছাতা আগে কখন দেখেছিলি?",
      "issue": "The phrase 'কখন দেখেছিলি' is grammatically correct but lacks the colloquial rhythm of natural Bangladeshi speech. In daily conversation, people would more likely say 'কখন দেখেছিলি আমি?' or 'কখন দেখেছিলি তুমি?' to show ownership and personal inquiry.",
      "instruction": "Replace with 'কখন দেখেছিলি তুমি?' to reflect authentic, conversational Bengali tone and avoid impersonal phrasing."
    },
    {
      "criterion": "emotion",
      "quote": "তানিiflowerা ছাতা দেখে মুখে হাসি দেয়",
      "issue": "The emotional response is stated directly and lacks subtlety. In real-life family interactions, such reactions are not expressed through a single, explicit action like 'হাসি দেয়'. A more natural reaction would be a slight pause, a frown, or a quiet look of confusion before any smile, especially when the object is not personally significant.",
      "instruction": "Rewrite to: 'তানিiflowerা ছাতা দেখে মুখে হাসি দেয় না, তার চোখে একটা সামান্য অদৃশ্য মুহূর্ত থাকে' to preserve emotional ambiguity and realism."
    },
    {
      "criterion": "logic",
      "quote": "রাশেদ তুমি ছাতা দেখে না, আমি তো দেখেছি।",
      "issue": "The statement contradicts the earlier scene where রাশেদ says 'আজ পরে হাতে আসল' — implying the hat appeared only after a specific time. Yet in the second scene, রাশেদ claims তানিiflowerা didn’t see it, while the screen shows it. This creates a logical inconsistency: if the hat appeared after midnight, and তানিiflowerা saw it in the morning, then the claim that she didn’t see it is false. The timeline is not internally consistent.",
      "instruction": "Adjust the dialogue to: 'তুমি ছাতা দেখে না, আমি তো দেখেছি' — but only if the hat is shown in the morning. Otherwise, revise the timeline: রাশেদ should say 'আমি দেখেছি, তুমি দেখেছিলে না' to align with the scene's reality and avoid contradiction."
    }
  ]
}
```
