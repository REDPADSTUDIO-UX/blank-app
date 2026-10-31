"""Optional local neural animation panel, isolated from paid providers."""
from pathlib import Path
import streamlit as st
from .local_animation import AnimationError, generate, readiness


def show_local_animation(media_dir):
    st.subheader('ছবি → AI অ্যানিমেশন — Local SVD-XT')
    st.caption('Local neural inference; no paid API. Each clip is about 3.6 seconds, landscape, without audio. Review before editing into a story.')
    ready, reason = readiness()
    if ready:
        st.success(reason)
    else:
        st.info(reason)
    st.caption('Requires a configured GPU host and locally provisioned SVD-XT weights under their applicable license. No model is downloaded automatically.')
    image = st.file_uploader('Animation source image', type=['png', 'jpg', 'jpeg'], key='local_i2v_image')
    seed = st.number_input('Animation seed', min_value=0, max_value=4294967295, value=42, key='local_i2v_seed')
    motion = st.slider('Motion intensity', 1, 255, 127, key='local_i2v_motion')
    if st.button('Generate local AI animation', disabled=not ready or image is None, key='local_i2v_generate'):
        try:
            with st.spinner('Generating 25 neural animation frames…'):
                output, metadata = generate(image.getvalue(), media_dir, seed=int(seed), motion=int(motion))
            st.session_state['local_i2v_output'] = (str(output), metadata)
        except AnimationError as exc:
            st.error(str(exc))
    result = st.session_state.get('local_i2v_output')
    if result:
        output, metadata = result
        path = Path(output)
        if path.is_file():
            st.video(path.read_bytes())
            st.download_button('Download AI animation MP4', path.read_bytes(), file_name=path.name, mime='video/mp4')
            st.caption(f"{metadata['frames']} generated frames · {metadata['fps']} fps · review required")
