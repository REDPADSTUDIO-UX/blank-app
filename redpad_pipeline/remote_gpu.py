"""Anonymous ZeroGPU via the supported Gradio client; never uses paid APIs."""
import hashlib,json,shutil,os
from io import BytesIO
from pathlib import Path
from uuid import uuid4
import requests
from PIL import Image

SPACE='zerogpu-aoti/wan2-2-fp8da-aoti-faster'
BASE='https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space'
class GPUError(RuntimeError): pass


def _verify_free_account(token):
    try:
        r=requests.get('https://huggingface.co/api/whoami-v2',
            headers={'Authorization':'Bearer '+token},timeout=(10,20))
        r.raise_for_status();profile=r.json()
    except (requests.RequestException,ValueError):
        raise GPUError('Hugging Face account verification failed. No GPU job was submitted.') from None
    if profile.get('type')!='user' or profile.get('isPro') is not False:
        raise GPUError('A free personal account could not be verified. GPU submission is blocked to avoid paid quota use.')
    return True


def free_account_token():
    token=os.environ.get('REDPAD_HF_FREE_TOKEN','').strip()
    if not token:return False
    _verify_free_account(token)
    return token


def test_image():
    # Deterministic geometric test fixture, not story artwork or AI output.
    from PIL import ImageDraw
    image=Image.new('RGB',(832,480),(60,71,83));d=ImageDraw.Draw(image)
    d.rectangle((0,280,832,480),fill=(151,155,156))
    for x in range(-300,1200,100):d.line((416,280,x,480),fill=(104,109,114),width=2)
    for y in [310,355,415]:d.line((0,y,832,y),fill=(104,109,114),width=2)
    d.ellipse((248,337,392,369),fill=(80,85,89))
    d.ellipse((270,240,370,340),fill=(199,39,40),outline=(100,20,25),width=3)
    d.ellipse((287,252,315,271),fill=(244,129,119))
    b=BytesIO();image.save(b,format='PNG');return b.getvalue()


def connection_status():
    try:
        authenticated=bool(free_account_token())
        r=requests.get(BASE+'/gradio_api/info',timeout=(10,20));r.raise_for_status()
        if '/generate_video' not in r.json().get('named_endpoints',{}):
            return False,'Free GPU API changed; generation needs review.'
        return True,('Free personal account verified; GPU endpoint reachable. Generation still depends on quota/queue.' if authenticated else 'Anonymous shared GPU endpoint reachable; personal free account is not connected.')
    except GPUError as exc:
        return False,str(exc)
    except (requests.RequestException,ValueError):
        return False,'Free GPU service is unreachable from this host. No paid request was made.'


def generate(image_bytes,prompt,media_dir):
    if not image_bytes or len(image_bytes)>10*1024*1024:
        raise GPUError('Use a PNG/JPEG of at most 10 MB.')
    if not isinstance(prompt,str) or not 1<=len(prompt.strip())<=1500:
        raise GPUError('Write a motion prompt of 1–1500 characters.')
    try:
        with Image.open(BytesIO(image_bytes)) as im:
            if im.format not in ('PNG','JPEG') or im.width*im.height>20_000_000:raise GPUError('Image exceeds supported format or pixel count.')
            im.verify()
    except GPUError:raise
    except Exception:raise GPUError('The image could not be decoded.') from None
    token=free_account_token()
    from gradio_client import Client,handle_file
    root=(Path(media_dir)/'remote_gpu'/uuid4().hex).resolve();root.mkdir(parents=True)
    source=root/'source.png';source.write_bytes(image_bytes)
    state=dict(space=SPACE,mode='authenticated-free-zerogpu' if token else 'anonymous-zerogpu',stage='preparing',paid_fallback=False,
        input_sha256=hashlib.sha256(image_bytes).hexdigest(),prompt=prompt.strip(),review_required=True)
    def save(): (root/'job.json').write_text(json.dumps(state,ensure_ascii=False,indent=2))
    save()
    try:
        client=Client(SPACE,hf_token=token,verbose=False,analytics_enabled=False,
                      httpx_kwargs={'timeout':60},download_files=str(root/'download'))
        state['stage']='submission-uncertain';save()
        job=client.submit(handle_file(str(source)),prompt.strip(),6,
            'blur, deformation, text, watermark',3.5,1,1,117,False,api_name='/generate_video')
        state['stage']='running';save()
        result=job.result(timeout=240)
        if not isinstance(result,(list,tuple)) or not result:raise GPUError('GPU returned an unrecognized result.')
        downloaded=Path(result[0]).resolve()
        if not downloaded.is_relative_to(root) or not downloaded.is_file() or downloaded.stat().st_size>80*1024*1024:
            raise GPUError('The generated video file could not be accepted.')
        from .media import duration
        seconds=duration(downloaded)
        if not 0.4<=seconds<=6:raise GPUError('Generated video duration is invalid.')
        output=root/'animation.mp4';shutil.copyfile(downloaded,output)
        state.update(stage='complete',seconds=seconds,seed=result[1] if len(result)>1 else 117,
            output_sha256=hashlib.sha256(output.read_bytes()).hexdigest());save()
        return output
    except Exception as exc:
        state['stage']='failed-or-unknown';save()
        if isinstance(exc,GPUError):raise
        text=str(exc).lower()
        if any(s in text for s in ('quota','exceeded','sign in','logged','authenticate')):
            raise GPUError('Free GPU quota/sign-in limit reached. No paid fallback or automatic retry was used.') from None
        raise GPUError('Free GPU job failed or its status is unknown. No video was substituted. Do not resubmit an uncertain job blindly.') from None
