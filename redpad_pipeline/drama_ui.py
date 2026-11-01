"""Read actual isolated drama project artifacts, never fabricate completion."""
import json,hashlib
from pathlib import Path

def show(media_dir):
 import streamlit as st
 st.subheader('🎬 Drama Production — ঘর ১:১৭')
 project=Path(__file__).resolve().parents[1]/'productions'/'ghor_117'
 root=Path(media_dir)/'drama'/'ghor117_ep01'
 plan=json.loads((project/'plan.json').read_text())
 st.caption('Original Bangladeshi fiction · Episode 1 · 2D animated drama · No paid generation')
 video=root/'Ghor_117_EP01_Animated_Drama.mp4'
 qa=root/'qa_report.json'
 if video.exists() and qa.exists() and json.loads(qa.read_text()).get('passed'):
  st.warning('Archived 2D prototype — media integrity passed; rejected as a realistic-drama result')
  st.video(str(video))
  with video.open('rb') as f:st.download_button('Download Episode 1 MP4',f,file_name=video.name,mime='video/mp4',key='drama_episode_download')
  st.caption('Stylized procedural 2D character animation. Synthetic Bengali dialogue. See QA for model-footage inclusion and limits.')
  st.json(json.loads(qa.read_text()),expanded=False)
 else:st.info('Production checkpoint: final video has not yet passed validation on this host.')
 for title,name in [('Screenplay','screenplay.md'),('Character and location bible','production_bible.md'),('30-episode season','season_outline.md')]:
  with st.expander(title):st.markdown((project/name).read_text())
 st.dataframe([dict(shot=s['id'],start=s['start'],seconds=s['seconds'],character=s['speaker'],dialogue=s['text'],action=s['action']) for s in plan['shots']],hide_index=True)
 st.caption('Isolated project media. An empty/new host does not imply that the original Render database has been restored or updated.')
