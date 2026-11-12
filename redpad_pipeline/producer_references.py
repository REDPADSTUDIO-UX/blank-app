"""Project-local immutable reference versions. Uploaded media is untrusted data."""
import hashlib, io, json, re, zipfile
from pathlib import Path
from uuid import uuid4
from .agents import AgentError, encode

MAX_FILE=32*1024*1024
MAX_PROJECT=256*1024*1024
CATEGORIES=('story','character','casting','costume_hair_makeup','movie','location','audio')
RIGHTS=('fictional_ai','authorized_person','reference_only')
EXTENSIONS={'.txt','.pdf','.docx','.png','.jpg','.jpeg','.webp','.wav','.mp3','.m4a','.mp4','.mov','.webm'}

def inspect_file(name,data):
    ext=Path(name).suffix.lower()
    if ext not in EXTENSIONS or not isinstance(data,bytes) or not 0<len(data)<=MAX_FILE:
        raise AgentError('Supported reference required; maximum 32 MiB per file.')
    info={'extension':ext,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'text':'',
          'status':'stored_uninspected','limitation':'No semantic media inspection; upload is not evidence of understanding or performance.'}
    if ext=='.txt':
        try:info.update(text=data.decode('utf-8-sig')[:20000],status='text_extracted',limitation='UTF-8 text; bounded to 20,000 characters.')
        except UnicodeDecodeError:raise AgentError('TXT must be UTF-8.') from None
    elif ext in ('.png','.jpg','.jpeg','.webp'):
        from PIL import Image
        try:
            with Image.open(io.BytesIO(data)) as im:
                if im.width*im.height>20_000_000:raise AgentError('Image exceeds 20 megapixels.')
                im.verify();info.update(width=im.width,height=im.height,status='image_preview_available')
        except (OSError,ValueError) as exc:raise AgentError('Invalid image reference.') from exc
    elif ext=='.docx':
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                entries=z.infolist()
                if len(entries)>500 or sum(x.file_size for x in entries)>16*1024*1024:raise AgentError('DOCX decompression limit exceeded.')
                xml=z.read('word/document.xml')
                if b'<!DOCTYPE' in xml.upper() or b'<!ENTITY' in xml.upper():raise AgentError('XML entities prohibited.')
                from xml.etree import ElementTree
                root=ElementTree.fromstring(xml)
                info.update(text=' '.join(n.text or '' for n in root.iter() if n.tag.endswith('}t'))[:20000],status='text_extracted',limitation='Document body text only; tables/layout/images may need human inspection; 20,000 character limit.')
        except (zipfile.BadZipFile,KeyError,ValueError) as exc:raise AgentError('Invalid DOCX.') from exc
    elif ext=='.pdf':
        if not data.startswith(b'%PDF-'):raise AgentError('Invalid PDF header.')
        # Parsing in a killable subprocess bounds both wall time and address space.
        import subprocess,sys
        code="""import io,json,resource,sys
resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))
from pypdf import PdfReader
r=PdfReader(io.BytesIO(sys.stdin.buffer.read()))
print(json.dumps({'text':'\\n'.join((p.extract_text() or '')[:20000] for p in r.pages[:20])[:20000],'pages':len(r.pages)}))
"""
        try:
            p=subprocess.run([sys.executable,'-c',code],input=data,capture_output=True,timeout=12)
            if p.returncode:raise ValueError()
            extracted=json.loads(p.stdout);info.update(**extracted,status='text_extracted',limitation='First 20 pages and 20,000 characters only; no OCR or visual interpretation.')
        except (subprocess.TimeoutExpired,ValueError):info.update(status='parser_unavailable_or_failed',limitation='PDF text extraction unavailable/failed; no document understanding claimed. Provide TXT or inspect manually.')
    else:
        valid=(ext=='.wav' and data.startswith(b'RIFF') and data[8:12]==b'WAVE') or (ext=='.mp3' and (data.startswith(b'ID3') or data[:1]==b'\xff')) or (ext in ('.mp4','.m4a','.mov') and b'ftyp' in data[:32]) or (ext=='.webm' and data.startswith(b'\x1aE\xdf\xa3'))
        if not valid:raise AgentError('Media signature does not match supported reference format.')
    return info

class References:
    def __init__(self,store):
        self.store=store;self.root=store.path.parent/'agent_media'/'producer_references'
        if any(p.is_symlink() for p in (self.root,*self.root.parents)):raise AgentError('Reference symlinks prohibited.')
        self.root.mkdir(parents=True,exist_ok=True,mode=0o700)
        with store.tx() as db:db.executescript('''
          CREATE TABLE IF NOT EXISTS producer_refs(id TEXT,version INTEGER,payload TEXT,PRIMARY KEY(id,version));
          CREATE TABLE IF NOT EXISTS producer_ref_heads(id TEXT PRIMARY KEY,version INTEGER);
          CREATE TABLE IF NOT EXISTS producer_ref_pins(task TEXT,id TEXT,version INTEGER,PRIMARY KEY(task,id));
        ''')
    def rows(self,history=False):
        with self.store.tx() as db:
            sql='SELECT r.payload FROM producer_refs r' if history else 'SELECT r.payload FROM producer_refs r JOIN producer_ref_heads h ON h.id=r.id AND h.version=r.version'
            return [json.loads(r[0]) for r in db.execute(sql)]
    def get(self,id,version=None):
        with self.store.tx() as db:
            if version is None:
                h=db.execute('SELECT version FROM producer_ref_heads WHERE id=?',(id,)).fetchone()
                if not h:raise AgentError('Unknown reference.')
                version=h[0]
            r=db.execute('SELECT payload FROM producer_refs WHERE id=? AND version=?',(id,version)).fetchone()
        if not r:raise AgentError('Unknown reference version.')
        return json.loads(r[0])
    def path(self,row):
        p=self.root/row['id']/(str(row['version'])+row['extension'])
        if p.is_symlink() or p.parent.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:raise AgentError('Reference file missing or changed.')
        return p
    def put(self,name,data,category,notes='',source='',rights='reference_only',id=None,expected=None,confirm_invalidation=False,archived=False):
        if category not in CATEGORIES or rights not in RIGHTS or not isinstance(name,str) or len(name)>240 or any(not isinstance(v,str) or len(v)>4000 for v in (notes,source)):raise AgentError('Invalid reference metadata.')
        info=inspect_file(name,data)
        old=self.get(id) if id else None
        if old and old['version']!=expected:raise AgentError('Reference changed; refresh.')
        id=id or uuid4().hex
        if not re.fullmatch('[a-f0-9]{32}',id):raise AgentError('Invalid reference ID.')
        version=old['version']+1 if old else 1
        row=dict(info,id=id,version=version,original_name=Path(name).name,category=category,notes=notes,source=source,rights=rights,archived=bool(archived),project=str(self.store.path.parent.name))
        with self.store.tx() as db:
            db.execute('BEGIN IMMEDIATE')
            h=db.execute('SELECT version FROM producer_ref_heads WHERE id=?',(id,)).fetchone()
            if (h[0] if h else None)!=(old['version'] if old else None):raise AgentError('Concurrent reference update; refresh.')
            used=db.execute('SELECT task FROM producer_ref_pins WHERE id=?',(id,)).fetchall()
            if used and confirm_invalidation is not True:raise AgentError('Reference is pinned to work. Confirm affected work invalidation before replacing/relabeling/removing.')
            total=sum(json.loads(r[0])['bytes'] for r in db.execute('SELECT payload FROM producer_refs'))
            if total+len(data)>MAX_PROJECT:raise AgentError('Project reference history exceeds 256 MiB.')
            folder=self.root/id
            if folder.is_symlink():raise AgentError('Reference symlink prohibited.')
            folder.mkdir(exist_ok=True,mode=0o700);path=folder/(str(version)+info['extension'])
            with path.open('xb') as f:f.write(data)
            path.chmod(0o600)
            db.execute('INSERT INTO producer_refs VALUES (?,?,?)',(id,version,encode(row)))
            db.execute('INSERT OR REPLACE INTO producer_ref_heads VALUES (?,?)',(id,version))
            self.store.event(db,'','owner','reference_version',{'id':id,'version':version,'affected_tasks':[r[0] for r in used]})
        return row
    def update(self,id,expected,confirm_invalidation=False,**changes):
        old=self.get(id,expected)
        if set(changes)-{'category','notes','source','rights','archived'}:raise AgentError('Unknown reference metadata.')
        return self.put(old['original_name'],self.path(old).read_bytes(),id=id,expected=expected,confirm_invalidation=confirm_invalidation,**{k:changes.get(k,old[k]) for k in ('category','notes','source','rights','archived')})
    def pin(self,task,rows):
        with self.store.tx() as db:
            db.execute('BEGIN IMMEDIATE');t=self.store._task(db,task)
            if t['revision']:raise AgentError('Bind references before generation only.')
            for row in rows:
                current=self.get(row['id'])
                if current['version']!=row['version'] or current['archived']:raise AgentError('Reference is stale or removed.')
                self.path(current)
                old=db.execute('SELECT version FROM producer_ref_pins WHERE task=? AND id=?',(task,row['id'])).fetchone()
                if old and old[0]!=row['version']:raise AgentError('Immutable reference pin differs.')
                db.execute('INSERT OR IGNORE INTO producer_ref_pins VALUES (?,?,?)',(task,row['id'],row['version']))
    def context(self):
        # Image/media are not included as imagined text. Human notes stay explicitly attributed.
        return [{**{k:r[k] for k in ('id','version','category','status','limitation','rights','sha256')},'text':r['text'][:1500],'notes':r['notes'][:500],'context_limit':'Excerpt only: 1,500 text characters per reference, first 20 active references. Original remains available for explicit inspection.'} for r in self.rows() if not r['archived']][:20]

def check_pins(db,task,project_root=None):
    if db.execute("SELECT 1 FROM sqlite_master WHERE name='producer_ref_pins'").fetchone():
        for p in db.execute('SELECT p.version,h.version,r.payload FROM producer_ref_pins p JOIN producer_ref_heads h ON h.id=p.id JOIN producer_refs r ON r.id=h.id AND r.version=h.version WHERE p.task=?',(task,)):
            row=json.loads(p[2])
            if p[0]!=p[1] or row['archived']:raise AgentError('Reference version changed; affected work is stale.')
            if project_root is not None:
                file=project_root/'agent_media'/'producer_references'/row['id']/(str(row['version'])+row['extension'])
                if any(p.is_symlink() for p in (file,*file.parents)) or not file.is_file() or file.stat().st_size>MAX_FILE or hashlib.sha256(file.read_bytes()).hexdigest()!=row['sha256']:raise AgentError('Pinned reference file missing or changed.')
