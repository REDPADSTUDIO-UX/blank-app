"""Offline image-to-video inference. No API clients or automatic downloads."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from uuid import uuid4
from PIL import Image, ImageOps


class AnimationError(RuntimeError):
    pass


def readiness():
    """Cheap preflight; importing this module never loads model weights."""
    checkpoint = Path(os.environ.get('REDPAD_SVD_CHECKPOINT', '')).expanduser()
    if not os.environ.get('REDPAD_SVD_CHECKPOINT') or not (checkpoint / 'model_index.json').is_file():
        return False, 'Local SVD-XT checkpoint is not configured. No download or API request was made.'
    for name in ('torch', 'diffusers', 'transformers', 'accelerate', 'imageio', 'imageio_ffmpeg'):
        if importlib.util.find_spec(name) is None:
            return False, f'Optional GPU dependency missing: {name}.'
    import torch
    if not torch.cuda.is_available():
        return False, 'CUDA GPU unavailable. Local AI animation cannot run on this host.'
    return True, 'Local model and CUDA available. This is a preflight, not a successful generation test.'


def generate(image_bytes, media_dir, *, seed=42, motion=127):
    if not isinstance(seed, int) or not 0 <= seed < 2**32:
        raise AnimationError('Seed must be an integer from 0 to 4294967295.')
    if not isinstance(motion, int) or not 1 <= motion <= 255:
        raise AnimationError('Motion must be between 1 and 255.')
    if not image_bytes or len(image_bytes) > 10 * 1024 * 1024:
        raise AnimationError('Select a JPEG or PNG of at most 10 MB.')
    from io import BytesIO
    try:
        with Image.open(BytesIO(image_bytes)) as source:
            if source.format not in ('JPEG', 'PNG') or source.width * source.height > 20_000_000:
                raise AnimationError('Use a JPEG or PNG of at most 20 megapixels.')
            image = ImageOps.fit(ImageOps.exif_transpose(source).convert('RGB'), (1024, 576))
    except AnimationError:
        raise
    except Exception:
        raise AnimationError('The selected image could not be decoded.') from None
    ready, reason = readiness()
    if not ready:
        raise AnimationError(reason)
    import torch
    from diffusers import StableVideoDiffusionPipeline
    from diffusers.utils import export_to_video
    root = Path(media_dir) / 'local_animation' / uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    output = root / 'animation.mp4'
    pipe = None
    try:
        # Local path + local_files_only prevent hosted inference and weight downloads.
        pipe = StableVideoDiffusionPipeline.from_pretrained(
            os.environ['REDPAD_SVD_CHECKPOINT'], torch_dtype=torch.float16,
            local_files_only=True)
        pipe.enable_model_cpu_offload()
        pipe.unet.enable_forward_chunking()
        frames = pipe(image, num_frames=25, num_inference_steps=25,
                      decode_chunk_size=2, motion_bucket_id=motion,
                      noise_aug_strength=0.02,
                      generator=torch.Generator(device='cpu').manual_seed(seed)).frames[0]
        if len(frames) != 25:
            raise AnimationError('The model returned an incomplete clip.')
        export_to_video(frames, str(output), fps=7)
        if not output.is_file() or output.stat().st_size < 1000:
            raise AnimationError('MP4 encoding failed.')
        metadata = dict(engine='local-svd-xt', frames=25, fps=7, seconds=25/7,
                        seed=seed, motion=motion, audio=False, review_required=True,
                        input_sha256=hashlib.sha256(image_bytes).hexdigest())
        (root / 'provenance.json').write_text(json.dumps(metadata, indent=2))
        return output, metadata
    except Exception:
        for file in root.iterdir():
            file.unlink()
        root.rmdir()
        raise AnimationError('Local animation failed. No clip was registered; check GPU memory and checkpoint compatibility.') from None
    finally:
        del pipe
        torch.cuda.empty_cache()
