"""Explicit Google Translate Bengali speech, isolated from billed Cloud APIs."""
from io import BytesIO
from pathlib import Path
from uuid import uuid4
import hashlib
import json

class VoiceError(RuntimeError):
    pass


def generate_google_bangla(text, media_dir):
    if not isinstance(text, str) or not 1 <= len(text.strip()) <= 5000:
        raise VoiceError('Enter 1–5000 characters of spoken Bengali, excluding stage directions.')
    try:
        from gtts import gTTS
        from gtts.tts import gTTSError
    except ImportError:
        raise VoiceError('Optional gTTS dependency is not installed on this Studio host.') from None
    data = BytesIO()
    try:
        # Consumer Translate TTS, not Cloud TTS/Gemini, no API key or billing.
        # Default TLS verification remains enabled. No retries or provider fallback.
        gTTS(text=text.strip(), lang='bn', lang_check=False, timeout=(10, 30)).write_to_fp(data)
    except gTTSError as exc:
        response = getattr(exc, 'rsp', None)
        code = getattr(response, 'status_code', None)
        if code == 429:
            raise VoiceError('Google Translate rate limit (429). No voice was saved. Try later; no automatic retry or alternative voice was used.') from None
        raise VoiceError('Google speech request failed. No voice was saved or substituted.') from None
    except Exception:
        raise VoiceError('Google speech connection failed. No voice was saved or substituted.') from None
    raw = data.getvalue()
    if len(raw) < 1000:
        raise VoiceError('Google returned empty or incomplete audio. Nothing was saved.')
    root = Path(media_dir) / 'google_voice' / uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    try:
        out = root / 'bangla.mp3'
        out.write_bytes(raw)
        (root / 'provenance.json').write_text(json.dumps(dict(
            provider='google-translate-consumer-tts', language='bn',
            text_sha256=hashlib.sha256(text.strip().encode()).hexdigest(),
            audio_sha256=hashlib.sha256(raw).hexdigest(),
            stage='voice-only', review_required=True,
            note='Not Gemini expressive speech; not a finished video.'), indent=2))
        return out
    except Exception:
        import shutil
        shutil.rmtree(root, ignore_errors=True)
        raise VoiceError('Voice could not be saved to Studio storage.') from None


def show_free_voice(media_dir):
    import streamlit as st
    st.subheader('Google বাংলা ভয়েস — Translate')
    st.caption('Consumer Translate TTS via gTTS. No billed API. This is not Gemini acting/expressive speech. Availability is not guaranteed.')
    spoken = st.text_area('Spoken Bengali only — no stage directions', max_chars=5000, key='google_bn_spoken')
    if st.button('Create Google Bengali voice', disabled=not spoken.strip(), key='google_bn_generate'):
        try:
            with st.spinner('Requesting Google Bengali speech…'):
                out = generate_google_bangla(spoken, media_dir)
            st.session_state['google_bn_output'] = str(out)
        except VoiceError as exc:
            st.session_state.pop('google_bn_output', None)
            st.error(str(exc))
    saved = st.session_state.get('google_bn_output')
    if saved and Path(saved).is_file():
        raw = Path(saved).read_bytes()
        st.audio(raw, format='audio/mp3')
        st.download_button('Download Google Bengali voice', raw, file_name='bangla.mp3', mime='audio/mpeg')
        st.caption('Voice stage complete only. Import this audio into Storyboard Studio to assemble the reviewed image animatic; no video job has been generated here.')
