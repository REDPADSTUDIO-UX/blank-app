"""Streamed scene editing with real FFmpeg, shaped Bengali captions, and ducked audio."""
import math
import re
import subprocess
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, features
from redpad_video_studio import ffmpeg_binary, create_ambient_wav
from .models import ProductionError

FONT = Path(__file__).resolve().parents[1] / 'assets/fonts/NotoSansBengali.ttf'


def ff(args, timeout=240):
    binary = ffmpeg_binary()
    if not binary:
        raise ProductionError('FFmpeg is unavailable. Install imageio-ffmpeg.')
    safe_args = []
    for arg in map(str, args):
        if arg == '-i':
            safe_args.extend(['-protocol_whitelist', 'file,pipe'])
        safe_args.append(arg)
    try:
        result = subprocess.run([binary, '-hide_banner', '-loglevel', 'error', '-y', *safe_args],
                                capture_output=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        raise ProductionError('The media operation timed out or could not start; resume the job.') from None
    if result.returncode:
        # stderr may contain signed provider URLs or user file paths: never show it.
        raise ProductionError('Media processing failed. Check codecs, disk space, font and uploaded media.')


def duration(path):
    try:
        result = subprocess.run([ffmpeg_binary(), '-hide_banner', '-protocol_whitelist', 'file,pipe', '-i', str(path)],
                                capture_output=True, text=True, timeout=20)
        match = re.search(r'Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)', result.stderr)
        if match:
            hours, minutes, seconds = match.groups()
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    except (OSError, subprocess.TimeoutExpired, TypeError):
        pass
    raise ProductionError('Unable to inspect generated media duration.')


def shaped_font(size):
    if not FONT.is_file() or not features.check('raqm'):
        raise ProductionError('Bengali subtitle rendering requires the bundled Noto font and Pillow RAQM.')
    return ImageFont.truetype(str(FONT), size=size, layout_engine=ImageFont.Layout.RAQM)


def wrap(draw, text, font, width):
    lines, current = [], ''
    for word in text.split():
        attempt = (current + ' ' + word).strip()
        if draw.textlength(attempt, font=font) > width and current:
            lines.append(current)
            current = word
        else:
            current = attempt
    if current:
        lines.append(current)
    return lines


def caption(scene, path, width, height, mock=False):
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    size = max(16, width // 23)
    # Fit the two-language caption into a predictable bottom safe area.
    while size >= 12:
        bnfont, enfont = shaped_font(size), shaped_font(max(11, int(size * .82)))
        bn = wrap(draw, scene['bn'], bnfont, width - 40)
        en = wrap(draw, scene['en'], enfont, width - 40)
        lineheight = int(size * 1.7)
        blockheight = (len(bn) + len(en)) * lineheight + 26
        if blockheight < height * .42:
            break
        size -= 1
    if blockheight >= height * .42:
        raise ProductionError('Subtitle text is too long to fit safely; shorten this scene.')
    top = height - blockheight - 28
    draw.rounded_rectangle((10, top, width - 10, height - 20), radius=12, fill=(0, 0, 0, 205))
    y = top + 10
    for lines, font, color in ((bn, bnfont, 'white'), (en, enfont, '#c5dcff')):
        for line in lines:
            x = (width - draw.textlength(line, font=font)) / 2
            draw.text((x, y), line, font=font, fill=color, stroke_width=0)
            y += lineheight
    if mock:
        draw.rectangle((0, 0, width, 50), fill=(125, 22, 22, 235))
        draw.text((12, 12), 'MOCK: synthetic motion + test tone', font=shaped_font(max(12, width // 28)), fill='white')
    image.save(path)


def effect(path, seconds, kind):
    rate = 24000
    frames = bytearray()
    for i in range(int(seconds * rate)):
        t = i / rate
        if kind == 'none' or t > .7:
            sample = 0
        else:
            frequency = {'whoosh': 130 + 1400 * t, 'impact': 75, 'chime': 880}[kind]
            envelope = math.exp(-t * (7 if kind != 'chime' else 4)) * min(1, t * 40)
            sample = int(math.sin(2 * math.pi * frequency * t) * envelope * 5000)
        frames.extend(sample.to_bytes(2, 'little', signed=True))
    with wave.open(str(path), 'wb') as out:
        out.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
        out.writeframes(frames)


def edit_scene(scene, source, voice, destination, ratio, mock=False, music=None):
    seconds = scene['seconds']
    width, height = ((360, 640) if ratio == '720:1280' else (640, 360)) if mock else tuple(map(int, ratio.split(':')))
    work = destination.parent
    overlay = work / 'captions.png'
    caption(scene, overlay, width, height, mock)
    bed = work / 'bed.wav'
    if music is None:
        create_ambient_wav(bed, seconds, 'Suspense / Horror')
    else:
        bed = Path(music)
    sfx = work / 'sfx.wav'
    effect(sfx, seconds, scene['sfx'])
    actual = duration(voice)
    if actual <= 0 or actual / seconds > 1.5:
        raise ProductionError('Narration does not fit this scene. Shorten it rather than truncating speech.')
    pace = max(1.0, actual / (seconds - .15))
    filters = (
        f'[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},'
        f'fps=24,trim=duration={seconds},setpts=PTS-STARTPTS[v];'
        '[v][1:v]overlay=0:0:format=auto,format=yuv420p[outv];'
        f'[2:a]aresample=48000,atempo={pace:.6f},apad,atrim=duration={seconds},'
        'asetpts=PTS-STARTPTS,asplit=2[voice][side];'
        f'[3:a]aresample=48000,volume=0.35,atrim=duration={seconds},'
        f'afade=t=out:st={max(0, seconds-.5)}:d=0.5[bed];'
        '[bed][side]sidechaincompress=threshold=0.025:ratio=8:attack=15:release=300[duck];'
        '[4:a]aresample=48000,volume=0.25[fx];'
        '[voice][duck][fx]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.95[outa]')
    ff(['-protocol_whitelist', 'file,pipe', '-i', source, '-loop', '1', '-i', overlay,
        '-i', voice, '-stream_loop', '-1', '-i', bed, '-i', sfx,
        '-filter_complex', filters, '-map', '[outv]', '-map', '[outa]', '-t', seconds,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '22', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', destination])


def timestamp(seconds):
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    secs, ms = divmod(remainder, 1000)
    return f'{hours:02}:{minutes:02}:{secs:02},{ms:03}'


def subtitles(plan, root):
    paths = []
    for language in ('bn', 'en'):
        text, cursor = [], 0
        for i, scene in enumerate(plan['scenes'], 1):
            text.append(f'{i}\n{timestamp(cursor)} --> {timestamp(cursor + scene["seconds"])}\n{scene[language]}\n')
            cursor += scene['seconds']
        path = root / f'subtitles.{language}.srt'
        path.write_text('\n'.join(text), encoding='utf-8')
        paths.append(path)
    return paths


def assemble(plan, clips, root):
    # All normalized clips have identical video/audio parameters; concatenate on disk.
    playlist = root / 'concat.txt'
    playlist.write_text(''.join(f"file 'scene_{i:03d}/edited.mp4'\n" for i in range(len(clips))))
    bn, en = subtitles(plan, root)
    temporary = root / 'final.partial.mp4'
    destination = root / 'final.mp4'
    ff(['-f', 'concat', '-safe', '1', '-i', playlist, '-i', bn, '-i', en,
        '-map', '0:v:0', '-map', '0:a:0', '-map', '1:0', '-map', '2:0',
        '-c:v', 'copy', '-c:a', 'copy', '-c:s', 'mov_text',
        '-metadata:s:s:0', 'language=ben', '-metadata:s:s:1', 'language=eng',
        '-movflags', '+faststart', temporary], timeout=300)
    if abs(duration(temporary) - plan['seconds']) > .5:
        raise ProductionError('Final video duration failed validation.')
    temporary.replace(destination)
    return destination


class MockGateway:
    """Offline codec fixture: moving test pattern and tone, never billed or called AI footage."""
    mode = 'mock'

    def voice(self, text, voice, path):
        ff(['-f', 'lavfi', '-i', 'sine=frequency=250:sample_rate=24000:duration=3', path])

    def submit_video(self, scene, ratio):
        return 'mock-task'

    def video_status(self, task_id, path):
        temporary = path.with_name('source.partial.mp4')
        ff(['-f', 'lavfi', '-i', 'testsrc2=size=360x640:rate=24:duration=10',
            '-an', '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p', temporary])
        temporary.replace(path)
        return True
