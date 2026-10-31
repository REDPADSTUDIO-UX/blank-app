from pathlib import Path
import json
import streamlit as st
from .remote_gpu import GPUError,connection_status,generate,SPACE


def show_remote_gpu(media_dir):
    st.subheader('ছবি → AI ভিডিও — Free shared GPU')
    st.caption('Wan 2.2 image-to-video on Hugging Face ZeroGPU. Render itself has no GPU. Each clip is about 3.5 seconds, without narration.')
    st.info('Anonymous free quota only. Queue or quota errors can stop generation. No account token, credits, paid fallback or automatic retry is used.')
    st.caption('Selected image and motion prompt are sent to the public third-party Space: '+SPACE+'. Use images you intend to process there.')
    if st.button('Check free GPU connection',key='remote_gpu_check'):
        ready,reason=connection_status();(st.success if ready else st.warning)(reason)
    image=st.file_uploader('Free GPU source image',type=['png','jpg','jpeg'],key='remote_gpu_image')
    prompt=st.text_area('Motion prompt (English)',value='The light flickers softly, curtains move gently in a breeze. Slow cinematic camera motion. Preserve the scene and character.',max_chars=1500,key='remote_gpu_prompt')
    if st.button('Generate image-to-video on free GPU',disabled=image is None or not prompt.strip(),key='remote_gpu_submit'):
        try:
            with st.spinner('Generating one free GPU clip; queue wait may take several minutes…'):
                generate(image.getvalue(),prompt,media_dir)
            st.success('Actual model-generated clip received. Review it below.')
        except GPUError as exc:st.error(str(exc))
    root=Path(media_dir)/'remote_gpu'
    completed=sorted(root.glob('*/animation.mp4'),key=lambda p:p.stat().st_mtime,reverse=True)
    if completed:
        choice=st.selectbox('Saved generated GPU clips',[str(p) for p in completed],format_func=lambda p:Path(p).parent.name[:12])
        raw=Path(choice).read_bytes();st.video(raw)
        st.download_button('Download generated GPU video',raw,file_name='ai_animation.mp4',mime='video/mp4')
    failed=0
    for state in root.glob('*/job.json'):
        try: failed+=json.loads(state.read_text()).get('stage')!='complete'
        except (ValueError,OSError):pass
    if failed: st.warning(f'{failed} job(s) are incomplete or uncertain. They are not successful clips and were not automatically retried.')
    st.caption('Server-local previews can disappear on restart; download clips you need to keep. A short GPU clip does not yet prove a complete narrated episode pipeline.')
