"""Build a handoff notebook, not a model result. No network/inference on build."""
import json
from pathlib import Path

CODE_COMMIT='877a475f344d85e19ea45338f3dff8d421a888e5'


def build():
    cells=[]
    def md(text):cells.append({'cell_type':'markdown','metadata':{},'source':text.splitlines(True)})
    def code(text):cells.append({'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':text.splitlines(True)})
    md('''# REDPAD — Stages 1–3: cached exact models only

এই notebook **execution handoff**, benchmark result নয়। Current Codex host had no GPU
and no controllable owner Colab session. All three stages are BLOCKED; zero inference.

ChatGPT Work: use the owner's **existing free Colab runtime**, ordinary notebook UI only.
Verify the actual free tier and GPU before setting the free-runtime flag. Do not buy
compute, accept licenses, download weights, add hosted inference endpoints, or bypass
authentication, quotas or native network isolation. No YouTube write or Render action.
The setup fetches only this source repository at an exact feature-branch commit.
It does not install/change model dependencies or acquire any model component.

Keep the isolated research directory and already approved installation receipts private.
Do not point at a production database. If exact cached bundles, receipts, compatible
libraries or isolation are missing, STOP that stage and retain its blocker.
''')
    code(f'''import os, sys, json, io, zipfile, urllib.request
from pathlib import Path
CODE_COMMIT = {CODE_COMMIT!r}
SOURCE = Path('/content/redpad_source_' + CODE_COMMIT[:12])
for key in ('HF_HUB_OFFLINE','TRANSFORMERS_OFFLINE','HF_DATASETS_OFFLINE','HF_HUB_DISABLE_TELEMETRY'):
    os.environ[key] = '1'
if SOURCE.exists():
    assert (SOURCE/'REDPAD_CODE_COMMIT').read_text().strip() == CODE_COMMIT, 'Existing source differs; preserve it.'
else:
    url = 'https://github.com/REDPADSTUDIO-UX/blank-app/archive/' + CODE_COMMIT + '.zip'
    with urllib.request.urlopen(url, timeout=60) as response:
        raw = response.read(64*1024*1024+1)
    assert len(raw) <= 64*1024*1024, 'Source archive exceeds safe setup limit.'
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        top = None
        for member in archive.infolist():
            parts = Path(member.filename).parts
            assert parts and '..' not in parts and not Path(member.filename).is_absolute()
            assert ((member.external_attr >> 16) & 0o170000) != 0o120000, 'No archive symlinks.'
            assert Path(member.filename).suffix.lower() not in ('.gguf','.safetensors','.pt','.pth'), 'No weight files in source setup.'
            top = top or parts[0]
            assert parts[0] == top
        extraction = Path('/content/redpad_source_extract_' + CODE_COMMIT[:12])
        assert not extraction.exists(), 'Preserve prior partial setup; inspect before retry.'
        extraction.mkdir()
        archive.extractall(extraction)
        (extraction/top).rename(SOURCE)
    (SOURCE/'REDPAD_CODE_COMMIT').write_text(CODE_COMMIT)
os.chdir(SOURCE)
sys.path.insert(0, str(SOURCE))
print('Pinned source ready:', CODE_COMMIT, '; no model weights downloaded.')
''')
    md('''## Read-only runtime and dependency inspection
The reported planning RAM/VRAM gates remain conservative estimates. Do not reduce
precision, swap models or silently override them to fit. No dependency installer is
included: preserve a verified compatible environment or report incompatibility.
Native Music/Voice must retain the existing isolated supervisor. Missing bubblewrap
or unsupported kernel isolation is a blocker, never permission to remove it.
''')
    code('''import shutil, importlib.metadata
from redpad_pipeline.stages_1_3 import runtime_probe, Session, write_human_package
inventory = runtime_probe()
print(json.dumps(inventory, indent=2))
print('native isolation tool:', shutil.which('bwrap'))
print('Remaining free quota: unknown unless actually exposed in Colab UI.')
FREE_RUNTIME_VERIFIED = False  # Work sets True only after inspecting this existing runtime's UI.
ROOT = Path('/content/redpad_stages_1_3')
session = Session(ROOT)
print('Use only existing owner-approved research install receipts and exact cached bundles.')
print('This notebook never creates a license approval or downloads missing components.')
''')
    md('''## Cache/approval gate
Reuse original `shared_model_installs` / `native_local_installs` receipts through the
existing Studio research controls in this marked research workspace. The receipts must
refer to real approved local files and retain original owner/license/source metadata.
Do not fabricate receipts or mark an unrelated/production database as research.
If no approved receipt/cache exists, stop and request the minimum separate download
and license authorization **after** identifying exact missing components. Prior GGUF
Story results are unrelated to the Qwen NF4 YouTube trial here.

The next cells are already within the owner's bounded three-model test authorization;
the free-runtime flag adds the actual platform check. Canary A counts toward the minimum.
No model is loaded just by opening this notebook.
''')
    for stage,title in [(1,'Qwen3.5 9B → YouTube'),(2,'ACE-Step 1.5 → Music'),(3,'Indic-Speak → Voice')]:
        md(f'''## Stage {stage} — {title}
One canary first. If blocked or technically unsuccessful, retain the exact state/logs
and continue the next independent stage only when GPU memory is released. Never rerun
a captured sample. A failed/interrupted reservation requires inspection, not auto retry.
''')
        code(f'''state{stage} = session.run({stage}, authorized=True, free_runtime_verified=FREE_RUNTIME_VERIFIED, full=False)
print(json.dumps({{k:state{stage}.get(k) for k in ('status','blocker','real_inference_calls','worker_execution_attempts')}}, ensure_ascii=False, indent=2))
print(write_human_package(ROOT, {stage}, state{stage}))
''')
        code(f'''# Run only after the actual canary has been technically checked.
if state{stage}['status'] in ('CANARY_CAPTURED','REAL_OUTPUTS_CAPTURED'):
    state{stage} = session.run({stage}, authorized=True, free_runtime_verified=FREE_RUNTIME_VERIFIED, full=True)
    print(json.dumps({{k:state{stage}.get(k) for k in ('status','blocker','real_inference_calls','worker_execution_attempts')}}, ensure_ascii=False, indent=2))
    print(write_human_package(ROOT, {stage}, state{stage}))
else:
    print('STOP THIS STAGE:', state{stage}.get('blocker'))
''')
    md('''## Readable private review and real audio playback
Review only actual captured files. A template with no samples is NOT READY. Scores,
creative acceptance, pronunciation and listening opinions stay blank until actual
independent experts inspect the media. Source brief/plan text is an authored input,
not model-generated text evidence. Music-only testing leaves SFX capability pending.
''')
    code('''from IPython.display import display, Markdown, Audio
from redpad_pipeline.professional_readiness import file_sha
for stage in (1,2,3):
    state_path = ROOT/f'stage{stage}/state.json'
    if not state_path.exists(): continue
    state = json.loads(state_path.read_text())
    package = write_human_package(ROOT, stage, state)
    display(Markdown(package.read_text()))
    for sample in state['samples']:
        if sample.get('path'):
            audio = ROOT/'agent_media'/sample['path']
            assert audio.is_file() and file_sha(audio) == sample['sha256'], 'Preservation blocker.'
            display(Audio(filename=str(audio)))
''')
    md('''## Preserve evidence before the free runtime expires
Download to the owner's device or another already authorized **private** evidence location.
Never commit raw audio, model files, databases or private administrator mappings to GitHub.
No public sharing or permanent Drive mount is created here. The archive below excludes
weight/cache files and includes only stage records and generated worker evidence.
Check that the download actually finishes before claiming persistence. No background promise.
''')
    code('''from google.colab import files
bundle = Path('/content/REDPAD_stage123_PRIVATE_evidence.zip')
assert not bundle.exists(), 'Preserve prior evidence export; choose a fresh filename.'
with zipfile.ZipFile(bundle, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for path in ROOT.rglob('*'):
        if not path.is_file() or path.is_symlink(): continue
        relative = path.relative_to(ROOT)
        allowed = relative.parts[0].startswith('stage') or relative.parts[0] == 'agent_media'
        if not allowed or path.suffix.lower() not in ('.json','.txt','.md','.wav','.log'): continue
        assert path.stat().st_size <= 200*1024*1024, 'Unexpected evidence size; inspect privately.'
        archive.write(path, relative)
print('Private archive SHA256:', file_sha(bundle))
files.download(str(bundle))
''')
    notebook={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}},'cells':cells}
    path=Path(__file__).resolve().parents[1]/'verification/real_stages_1_3_20261115/STAGES_1_3_CACHED_MODELS_ONLY.ipynb'
    path.write_text(json.dumps(notebook,ensure_ascii=False,indent=2)+'\n')
    return path


if __name__=='__main__':print(build())
