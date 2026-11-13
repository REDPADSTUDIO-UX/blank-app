"""Isolated, explicitly authorized research worker lifecycle, never production.

CPU fixtures exercise the very same process supervision without model libraries.
Native execution requires an existing authenticated owner-approved installation,
current task/source/consent pins, explicit launch authorization, and kernel isolation.
"""
import hashlib,json,os,signal,subprocess,sys,time,shutil
from fractions import Fraction
from pathlib import Path
from uuid import uuid4
from .agents import AgentError,encode
from .no_gpu_staging import fingerprint
from .native_local_bundle import NativeInstalls,local_path
from .resource_guard import serialized

ROOT=Path(__file__).resolve().parents[1]
WORKER=ROOT/'redpad_pipeline/native_local_worker.py'
FIXTURE=ROOT/'redpad_pipeline/native_fixture_worker.py'
TERMINAL={'CPU MOCK COMPLETE','RETURNED FOR TECHNICAL REVIEW','FAILED','CANCELLED','TIMED OUT','INTERRUPTED','STALE','ISOLATION BLOCKED'}

def controller_fingerprint():
    return fingerprint({name:hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest() for name in ('native_execution.py','native_local_bundle.py')})


def process_identity(pid):
    try:
        raw=Path('/proc')/str(pid)/'stat';s=raw.read_text();tail=s.rsplit(')',1)[1].split()
        if tail[0]=='Z':return None
        return tail[19]  # field 22: process start ticks, protects against PID reuse.
    except (OSError,IndexError):return None


def terminate_group(process):
    # start_new_session=True makes the worker the group leader, including MPI children.
    try:os.killpg(process.pid,signal.SIGTERM)
    except ProcessLookupError:
        process.wait(timeout=2);return
    try:process.wait(timeout=.4)
    except subprocess.TimeoutExpired:pass
    # Kill descendants even when the leader has already exited on SIGTERM.
    try:os.killpg(process.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    process.wait(timeout=2)


def cancel_owned_process(pid,ticks,folder):
    """Stop only our recorded generation, including after a controller restart."""
    if process_identity(pid)!=ticks:return False
    try:
        command=(Path('/proc')/str(pid)/'cmdline').read_bytes().split(b'\0')
        if not any(str(folder).encode() in arg for arg in command):return False
        os.killpg(pid,signal.SIGTERM)
        end=time.monotonic()+.4
        while process_identity(pid)==ticks and time.monotonic()<end:time.sleep(.01)
        # A surviving leader must still be the original process; never kill reused PID.
        current=process_identity(pid)
        if current is None or current==ticks:
            try:os.killpg(pid,signal.SIGKILL)
            except ProcessLookupError:pass
        return True
    except (ProcessLookupError,OSError):return False


def isolated_command(job_path,output_dir,devices):
    binary=shutil.which('bwrap')
    if not binary:raise AgentError('Kernel network/filesystem isolation unavailable; native launch blocked.')
    if not isinstance(devices,list) or any(d not in ('/dev/nvidia0','/dev/nvidiactl','/dev/nvidia-uvm','/dev/nvidia-uvm-tools') for d in devices):raise AgentError('Only separately authorized local GPU device bindings permitted.')
    args=[binary,'--unshare-user','--unshare-pid','--unshare-net','--die-with-parent','--new-session','--ro-bind','/','/','--dev','/dev','--proc','/proc','--tmpfs','/tmp','--bind',str(output_dir),str(output_dir),'--chdir',str(output_dir)]
    for device in devices:args+=['--dev-bind',device,device]
    return args+['--',sys.executable,'-m','redpad_pipeline.native_local_worker',str(job_path)]


def compile_job(prepared,stage,install,output_dir):
    pid=prepared['profile']
    if pid!=install['profile'] or stage['plan']['profile']!=pid or stage['id']!=prepared['stage_id']:raise AgentError('Stage/model identity differs.')
    if stage['plan']['role'] not in ('performance','motion','video','voice','music','casting'):raise AgentError('Native six-agent scope only.')
    paths={};pins=stage['references'];r=stage['plan']['request']
    from .producer_references import References
    # Paths supplied by the caller below are source-hash checked, never request strings.
    for key in ('image_reference','video_reference','reference'):
        pin=r.get(key)
        if pin is not None:
            row=next((x for x in pins if x['id']==pin['id'] and x['version']==pin['version']),None)
            if not row:raise AgentError('Missing pinned native reference.')
            paths[key]=row['id']  # Parent replaces IDs with verified copied file paths.
    if pid in ('ltx25','wan_animate2','ace15') and 'native_call_preparation' not in prepared:raise AgentError('Explicit specialist spec required; old contract-only draft cannot launch.')
    call=prepared.get('native_call_preparation')
    job={'profile':pid,'stage_id':stage['id'],'prepared_id':prepared['prepared_id'],'install':install,
         'references':paths,'call':call,'output_dir':str(output_dir),'research_execution_authorized':True,
         'network_namespace_required':True,'production_ready':False}
    if 'payload' in prepared:
        payload=dict(prepared['payload']);payload['checkpoint']=install['model_root']
        payload['output']=str(Path(output_dir)/('output.mp4' if pid in ('wan22_5','svd_xt') else 'output.wav'))
        job['legacy_payload']=payload
    return job


def validate_video_metadata(info,expected):
    """Pure format/timing validation; never a cinematic/physics assessment."""
    video=next((s for s in info.get('streams',[]) if s.get('codec_type')=='video'),None)
    if not video:raise AgentError('Generated artifact has no video stream.')
    try:
        rate=float(Fraction(video['avg_frame_rate']));frames=int(video['nb_read_frames'])
        duration=float(info['format']['duration'])
        if (int(video['width']),int(video['height']))!=(expected['width'],expected['height']) or abs(rate-expected['fps'])>.01 or frames!=expected['frames'] or abs(duration-frames/rate)>max(.15,1/rate):raise ValueError()
    except (KeyError,ValueError,ZeroDivisionError,TypeError):raise AgentError('Native output dimensions/frame count/rate/duration differ; retain output as failed evidence.') from None
    return {'container_checked':True,'frame_count':frames,'fps':rate,'duration':duration,'creative_quality_verified':False}


def inspect_native_output(path,expected):
    probe=shutil.which('ffprobe')
    if not probe:raise AgentError('Local ffprobe unavailable; output cannot pass technical gate.')
    with path.open('rb') as f:header=f.read(12)
    if header[4:8]!=b'ftyp':raise AgentError('Native video must be an MP4/MOV container; no playlist or URL.')
    result=subprocess.run([probe,'-v','error','-protocol_whitelist','file,pipe','-f','mov','-count_frames','-show_format','-show_streams','-of','json',str(path)],capture_output=True,text=True,timeout=30,check=True)
    return validate_video_metadata(json.loads(result.stdout),expected)


class NativeExecution:
    def __init__(self,store):
        self.store=store;self.installs=NativeInstalls(store)
        self.root=(store.path.parent/'agent_media'/'native_research_runs').absolute()
        if any(p.is_symlink() for p in (self.root,*self.root.parents)):raise AgentError('Unsafe worker workspace.')
        self.root.mkdir(parents=True,exist_ok=True,mode=0o700)
        with store.tx() as db:
            db.execute('CREATE TABLE IF NOT EXISTS native_research_runs(id TEXT PRIMARY KEY,payload TEXT,sha256 TEXT,state TEXT,cancel INTEGER,pid INTEGER,start_ticks TEXT,result TEXT)')
            columns={r[1] for r in db.execute('PRAGMA table_info(native_research_runs)')}
            for name,kind in (('controller_pid','INTEGER'),('controller_ticks','TEXT')):
                if name not in columns:db.execute('ALTER TABLE native_research_runs ADD COLUMN '+name+' '+kind)
            db.execute('CREATE TABLE IF NOT EXISTS native_run_keys(key TEXT PRIMARY KEY,run TEXT)')
    def _row(self,id):
        if not isinstance(id,str) or len(id)!=32 or any(x not in '0123456789abcdef' for x in id):raise AgentError('Invalid worker run ID.')
        with self.store.tx() as db:r=db.execute('SELECT * FROM native_research_runs WHERE id=?',(id,)).fetchone()
        if not r or hashlib.sha256(r['payload'].encode()).hexdigest()!=r['sha256']:raise AgentError('Unknown or altered worker run.')
        return dict(r)
    def _insert(self,data,*,dedup=False):
        id=uuid4().hex;raw=encode(data)
        with self.store.tx() as db:
            db.execute('BEGIN IMMEDIATE')
            if dedup:
                key=fingerprint(data);old=db.execute('SELECT r.id,r.state FROM native_run_keys k JOIN native_research_runs r ON r.id=k.run WHERE k.key=?',(key,)).fetchone()
                if old and old['state'] not in ('FAILED','CANCELLED','TIMED OUT','INTERRUPTED','STALE','ISOLATION BLOCKED'):return old['id']
            db.execute('INSERT INTO native_research_runs(id,payload,sha256,state,cancel) VALUES (?,?,?,\'QUEUED\',0)',(id,raw,hashlib.sha256(raw.encode()).hexdigest()))
            if dedup:db.execute('INSERT OR REPLACE INTO native_run_keys VALUES (?,?)',(key,id))
        return id
    def queue(self,prepared_id,install_id):
        from .offline_preparation import PreparedRequests
        prepared=PreparedRequests(self.store).get(prepared_id);install=self.installs.get(install_id)
        if prepared['profile']!=install['profile']:raise AgentError('No hidden model fallback.')
        data={'prepared_id':prepared_id,'install_id':install_id,'worker_sha256':hashlib.sha256(WORKER.read_bytes()).hexdigest(),'controller_sha256':controller_fingerprint(),'software_fixture':False}
        return self._insert(data,dedup=True)
    def queue_fixture(self,case='success'):
        if case not in ('success','failure','timeout','child','invalid_output','network'):raise AgentError('Fixed software fixture only; no script/argv/model override.')
        return self._insert({'software_fixture':True,'case':case,'worker_sha256':hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),'controller_sha256':controller_fingerprint()})
    def status(self,id):
        r=self._row(id);return {'id':id,'state':r['state'],'cancel_requested':bool(r['cancel']),
                              'software_fixture':json.loads(r['payload'])['software_fixture'],'result':json.loads(r['result']) if r['result'] else None,'production_ready':False}
    def cancel(self,id):
        r=self._row(id)
        with self.store.tx() as db:
            if r['state']=='QUEUED':db.execute("UPDATE native_research_runs SET cancel=1,state='CANCELLED' WHERE id=? AND state='QUEUED'",(id,))
            elif r['state']=='RUNNING':db.execute('UPDATE native_research_runs SET cancel=1 WHERE id=?',(id,))
        if r['state']=='RUNNING' and r['pid'] and process_identity(r['pid'])==r['start_ticks']:
            cancel_owned_process(r['pid'],r['start_ticks'],self.root/id)
        if r['state']=='RUNNING' and (not r['controller_pid'] or process_identity(r['controller_pid'])!=r['controller_ticks']):
            return self._finish(id,'CANCELLED',{'software_fixture':json.loads(r['payload'])['software_fixture'],'error':'owner_cancel_after_controller_exit'})
        return self.status(id)
    def recover(self,id):
        r=self._row(id)
        controller_alive=r['controller_pid'] and process_identity(r['controller_pid'])==r['controller_ticks']
        if r['state']=='RUNNING' and not controller_alive and (not r['pid'] or process_identity(r['pid'])!=r['start_ticks']):
            with self.store.tx() as db:db.execute("UPDATE native_research_runs SET state='INTERRUPTED' WHERE id=? AND state='RUNNING'",(id,))
        return self.status(id)  # Never automatically retries an interrupted generation.
    def _finish(self,id,state,result):
        result.update(production_ready=False,human_reviewed=False,independent_qc_required=True,owner_acceptance_required=True)
        with self.store.tx() as db:db.execute('UPDATE native_research_runs SET state=?,result=? WHERE id=?',(state,encode(result),id))
        return self.status(id)
    @serialized
    def run(self,id,*,authorized=False,timeout=120,devices=None):
        if authorized is not True:raise AgentError('Explicit owner launch authorization required; queueing is not inference permission.')
        if type(timeout) not in (float,int) or not .02<=timeout<=7200:raise AgentError('Bounded timeout required.')
        row=self._row(id);data=json.loads(row['payload']);fixture=data['software_fixture']
        worker=FIXTURE if fixture else WORKER
        if hashlib.sha256(worker.read_bytes()).hexdigest()!=data['worker_sha256'] or data.get('controller_sha256')!=controller_fingerprint():return self._finish(id,'STALE',{'error':'worker_or_controller_source_changed'})
        if row['state']!='QUEUED':raise AgentError('Run not queued; no automatic duplicate/retry.')
        folder=self.root/id
        if folder.exists():raise AgentError('Worker output directory already exists; no overwrite or symlink reuse.')
        folder.mkdir(mode=0o700)
        with self.store.tx() as db:
            cursor=db.execute("UPDATE native_research_runs SET state='RUNNING',controller_pid=?,controller_ticks=? WHERE id=? AND state='QUEUED' AND cancel=0",(os.getpid(),process_identity(os.getpid()),id))
            if cursor.rowcount!=1:raise AgentError('Run concurrently cancelled/claimed.')
        begin=time.monotonic();process=None
        try:
            if fixture:
                command=[sys.executable,'-m','redpad_pipeline.native_fixture_worker',data['case'],str(folder)]
            else:
                from .offline_preparation import PreparedRequests
                from .no_gpu_staging import StagingLedger
                from .producer_references import References
                prepared=PreparedRequests(self.store).get(data['prepared_id']);stage=StagingLedger(self.store).get(prepared['stage_id'])
                install=self.installs.get(data['install_id']);job=compile_job(prepared,stage,install,folder);refs=References(self.store)
                for k,reference_id in job['references'].items():
                    original=next(p for p in stage['references'] if p['id']==reference_id);source=refs.path(original)
                    target=folder/(reference_id+original['extension']);shutil.copyfile(source,target)
                    if hashlib.sha256(target.read_bytes()).hexdigest()!=original['sha256']:raise AgentError('Reference changed during isolated copy.')
                    job['references'][k]=str(target)
                if 'legacy_payload' in job and job['references'].get('reference'):
                    job['legacy_payload']['reference']=job['references']['reference']
                    job['legacy_payload']['request']['reference']=job['references']['reference']
                job['parent_network_namespace']=os.readlink('/proc/self/ns/net')
                request_path=folder/'request.json';request_path.write_text(encode(job))
                command=isolated_command(request_path,folder,devices or [])
            # No inherited tokens/proxies/account credentials enter the child environment.
            env={'PATH':os.environ.get('PATH','/usr/bin:/bin'),'PYTHONPATH':str(ROOT),'HOME':str(folder),'TMPDIR':str(folder),'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HF_DATASETS_OFFLINE':'1','TORCH_FORCE_WEIGHTS_ONLY_LOAD':'1','PYTHONDONTWRITEBYTECODE':'1'}
            if not fixture and devices:env['CUDA_VISIBLE_DEVICES']='0'
            if self._row(id)['cancel']:return self._finish(id,'CANCELLED',{'software_fixture':fixture,'error':'cancelled_before_launch'})
            with (folder/'stdout.txt').open('wb') as stdout,(folder/'stderr.txt').open('wb') as stderr:
                process=subprocess.Popen(command,cwd=folder,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
                ticks=process_identity(process.pid)
                with self.store.tx() as db:db.execute('UPDATE native_research_runs SET pid=?,start_ticks=? WHERE id=?',(process.pid,ticks,id))
                state=None
                while process.poll() is None:
                    if self._row(id)['cancel']:state='CANCELLED';break
                    if time.monotonic()-begin>timeout:state='TIMED OUT';break
                    if sum(p.stat().st_size for p in folder.rglob('*') if p.is_file() and not p.is_symlink())>600*1024*1024:state='FAILED';break
                    time.sleep(.015)
                terminate_group(process)  # Also reaps leaked descendants after normal completion.
            if self._row(id)['cancel']:state='CANCELLED'
            if state:return self._finish(id,state,{'software_fixture':fixture,'error':state,'elapsed_seconds':time.monotonic()-begin})
            if process.returncode!=0:
                return self._finish(id,'FAILED' if fixture else 'ISOLATION BLOCKED' if process.returncode==1 and b'bwrap:' in (folder/'stderr.txt').read_bytes() else 'FAILED',{'software_fixture':fixture,'error':'worker_exit','returncode':process.returncode})
            state_file=local_path(folder,'worker_state.json');result=json.loads(state_file.read_text())
            if type(result.get('inference_completed')) is not bool or result.get('software_fixture') is not fixture:raise AgentError('Worker provenance/type mismatch.')
            if fixture and (result['inference_completed'] or result.get('artifact')):raise AgentError('Mock cannot claim inference or generated artistic evidence.')
            if not fixture:
                if not result['inference_completed']:raise AgentError('Incomplete inference; retain raw evidence, no pass.')
                artifact=local_path(folder,result['artifact'])
                if hashlib.sha256(artifact.read_bytes()).hexdigest()!=result['artifact_sha256']:raise AgentError('Artifact/provenance mismatch.')
                pid=prepared['profile'];spec=prepared.get('owner_annotations')
                if pid in ('ltx25','wan_animate2','wan22_5','svd_xt'):
                    expected={k:(spec[k] if spec else stage['plan']['request'][k]) for k in ('width','height','fps','frames')}
                    result['technical_validation']=inspect_native_output(artifact,expected)
                result.update(profile=pid,stage_id=stage['id'],prepared_id=data['prepared_id'],install_id=data['install_id'],model_revision=install['revision'])
                # Reject stale task/source/rights/consent changes that occurred during work.
                PreparedRequests(self.store).get(data['prepared_id']);self.installs.get(data['install_id'])
            result['elapsed_seconds']=time.monotonic()-begin
            return self._finish(id,'CPU MOCK COMPLETE' if fixture else 'RETURNED FOR TECHNICAL REVIEW',result)
        except (AgentError,ValueError,KeyError,OSError,subprocess.SubprocessError) as exc:
            if process:terminate_group(process)
            return self._finish(id,'FAILED',{'software_fixture':fixture,'error_type':type(exc).__name__,'elapsed_seconds':time.monotonic()-begin})
