"""No-code writing desk. Screenplays never enter the narration voice path."""
import json
import os
from pathlib import Path
from uuid import uuid4
import streamlit as st
from .screenwriter import WritingError, build_prompt, curriculum, generate, render


def show(media_dir):
    st.subheader('চিত্রনাট্য লেখার ডেস্ক')
    st.caption('হুকের বিকল্প → দৃশ্য পরিকল্পনা → খসড়া → সম্পাদনা → পুনর্লেখা')
    with st.expander('এজেন্টের পাঠ্য ও উদাহরণ'):
        data = curriculum()
        st.write('পাঠ:', len(data['lessons']), '· বাংলা উদাহরণ:', len(data['examples']))
        for source in data['sources']:
            st.markdown(f"[{source['title']}]({source['url']})")
        st.caption('Sintel-এর প্রথম দুই দৃশ্য অন্তর্ভুক্ত। এটি সব স্ক্রিপ্টের সংগ্রহ বা মডেলের weight training নয়।')
    brief = st.text_area('গল্প, চরিত্র, বাজেট ও সংশোধনের নির্দেশ', key='writer_brief')
    genre = st.selectbox('ধরন', ['horror / হরর', 'family drama / পারিবারিক নাটক', 'romance / প্রেম'], key='writer_genre')
    seconds = st.number_input('লক্ষ্য দৈর্ঘ্য (সেকেন্ড)', min_value=15, max_value=600, value=300, key='writer_seconds')
    continuity = st.text_area('আগের দৃশ্য, চরিত্র ও ধারাবাহিকতার তথ্য', key='writer_continuity')
    if brief.strip():
        try:
            prompt = build_prompt(brief, genre, seconds, continuity)
            st.download_button('সম্পূর্ণ লেখার নির্দেশনা ডাউনলোড', prompt, file_name='redpad_screenwriter_prompt.txt', key='writer_prompt')
        except WritingError as exc:
            st.error(str(exc)); return
    configured = bool(os.environ.get('REDPAD_LOCAL_WRITER_MODEL'))
    if not configured:
        st.info('বিনামূল্যের স্থানীয় লেখার মডেল এই সার্ভারে যুক্ত নেই। নির্দেশনা প্রস্তুত আছে; স্বয়ংক্রিয় লেখা এখন বন্ধ।')
    if st.button('চিত্রনাট্য তৈরি ও পুনর্লেখা', disabled=not configured or not brief.strip(), key='writer_generate'):
        try:
            with st.spinner('দৃশ্য পরিকল্পনা, লেখা ও সম্পাদনা চলছে…'):
                result = generate(brief, genre, seconds, continuity)
            folder = Path(media_dir) / 'screenplay_drafts'
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / (uuid4().hex + '.json')
            path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            st.session_state['writer_result'] = result
            st.success('নতুন খসড়া সংরক্ষিত; সম্পাদকীয় মূল্যায়ন বাকি।')
        except (WritingError, OSError) as exc:
            st.error(str(exc))
    folder = Path(media_dir) / 'screenplay_drafts'
    saved = sorted(folder.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True) if folder.exists() else []
    if saved:
        choice = st.selectbox('সংরক্ষিত লেখার কাজ', saved, format_func=lambda p:p.stem, key='writer_saved')
        if st.button('সংরক্ষিত খসড়া খুলুন', key='writer_load'):
            try: st.session_state['writer_result'] = json.loads(choice.read_text(encoding='utf-8'))
            except (ValueError, OSError): st.error('সংরক্ষিত ফাইল পড়া যায়নি।')
    result = st.session_state.get('writer_result')
    if result:
        if result['structural_issues']:
            st.warning('খসড়ায় সংশোধন দরকার।'); st.write(result['structural_issues'])
        else:
            st.markdown(render(result['screenplay']))
            st.download_button('চিত্রনাট্য ডাউনলোড', render(result['screenplay']), file_name='screenplay.md', key='writer_download')
        with st.expander('পরিকল্পনা ও সম্পাদকের নোট'): st.json(result)
        st.caption('কাঠামোর পরীক্ষা সাহিত্যমানের নিশ্চয়তা নয়। এটি স্বয়ংক্রিয়ভাবে অনুমোদিত বা প্রকাশিত হয়নি।')
