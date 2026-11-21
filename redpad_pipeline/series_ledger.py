"""Bounded episode architecture with explicit state/causal/setup links.
Technical draft validation only. No promotion to approved Studio artifacts.
"""
import json,re,os,fcntl
from pathlib import Path
from .agents import AgentError
from .filmmaking_knowledge import retrieve
from .staged_writing import StagedDraft,digest,obj,text_schema,enum
from .screenwriter import WritingError

class SeriesLedger:
    def __init__(self,folder):
        self.folder=Path(folder)
        if any(p.is_symlink() for p in (self.folder,*self.folder.parents)):raise AgentError('Series symlinks prohibited.')
        self.folder.mkdir(parents=True,exist_ok=True)

    def create(self,brief,actors,state,episodes=30):
        if not isinstance(brief,str) or not 1<=len(brief)<=8000:raise AgentError('Bounded original series brief required.')
        if not isinstance(actors,list) or not 1<=len(actors)<=8 or any(not isinstance(a,str) or not a.strip() or len(a)>60 for a in actors) or len(set(actors))!=len(actors):raise AgentError('One to eight distinct character names required.')
        if not isinstance(state,dict) or not 1<=len(state)<=8 or any(not isinstance(k,str) or not 1<=len(k)<=80 or not isinstance(v,str) or not 1<=len(v)<=100 for k,v in state.items()):raise AgentError('One to eight named initial states required.')
        if type(episodes) is not int or not 1<=episodes<=100:raise AgentError('Series supports one to one hundred bounded episodes.')
        p=self.folder/'series.json'
        packet={'brief':brief,'actors':actors,'initial_state':state,'episodes':episodes,'guidance':retrieve('story',brief)}
        if p.exists():
            old=json.loads(p.read_text())
            if {k:old[k] for k in ('brief','actors','initial_state','episodes')}!={k:packet[k] for k in ('brief','actors','initial_state','episodes')}:raise AgentError('Existing series is immutable; create a new version.')
            return old
        packet['sha256']=digest(packet);p.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
        return packet

    def state(self):
        config=json.loads((self.folder/'series.json').read_text())
        if config['sha256']!=digest({k:v for k,v in config.items() if k!='sha256'}):raise AgentError('Series configuration integrity failed.')
        before=config['initial_state'];previous='origin';parent=config['sha256'];planted={};completed=0
        for number in range(1,config['episodes']+1):
            p=self.folder/f'ep{number:03}.json'
            if not p.exists():
                if any(self.folder.glob('ep[0-9][0-9][0-9].json')) and any((self.folder/f'ep{n:03}.json').exists() for n in range(number+1,config['episodes']+1)):raise AgentError('Episode history has a gap; do not regenerate completed successors.')
                break
            r=json.loads(p.read_text())
            if r['status']!='validated_stage':break
            # Older runner writes model_digest only after its post-call inventory
            # check. Retain those verified records without rewriting their chain.
            e=r.get('evidence',{})
            legacy_identity=r.get('series_identity_verified') is None and re.fullmatch(r'sha256:[a-f0-9]{64}',e.get('model_digest','')) and e.get('model')==r['request'].get('model')
            if r.get('provenance')=='local_inference' and r.get('series_identity_verified') is not True and not legacy_identity:raise AgentError('Episode post-inference identity check is incomplete; preserve evidence and recover explicitly.')
            if r['request_sha256']!=digest(r['request']) or json.loads(r['raw'])!=r['result'] or r['request']['data']['parent_sha256']!=parent:raise AgentError('Episode provenance or parent chain changed.')
            self.validate(r['result'],number,config,before,previous,planted)
            before=r['result']['state_after'];previous=r['result']['event_id'];parent=digest(r);completed=number
            for setup in r['result']['plant']:planted[setup]=number
        return {'config':config,'completed':completed,'state':before,'previous_event':previous,'parent_sha256':parent,'planted':planted,'production_approved':False,'human_review_completed':False}

    @staticmethod
    def validate(result,number,config,before,previous,planted):
        if result['event_id']!=f'episode_{number}' or result['cause_id']!=previous or result['actor'] not in config['actors']:raise WritingError('Episode identity or causal predecessor differs.')
        if result['state_before']!=before or set(result['state_after'])!=set(before):raise WritingError('Continuity state or known fact keys differ.')
        if result['state_after']==before:raise WritingError('Episode choice must change at least one tracked state.')
        if len(set(result['plant']))!=len(result['plant']) or any(not re.fullmatch(rf'e{number}_s[1-3]',s) or s in planted for s in result['plant']):raise WritingError('Setup IDs must be unique and planted in their own episode.')
        if len(set(result['payoff']))!=len(result['payoff']) or any(s not in planted or planted[s]>=number for s in result['payoff']):raise WritingError('Payoff has no earlier planted setup.')

    def run_next(self,*,model=None,store=None,complete=None):
        return self._locked_run(model=model,store=store,complete=complete)

    def retry_next(self,correction,*,model=None,store=None,complete=None):
        if not isinstance(correction,str) or not 1<=len(correction.strip())<=500:raise AgentError('One bounded corrective instruction required.')
        return self._locked_run(model=model,store=store,complete=complete,correction=correction)

    def _locked_run(self,*,model=None,store=None,complete=None,correction=None):
        fd=os.open(self.folder/'.execution.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'a') as lock:
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise AgentError('A series worker is already active; no duplicate inference allowed.') from None
            if correction is not None:
                state=self.state();key=f"ep{state['completed']+1:03}"
                StagedDraft(self.folder).retry(key)
            return self._run_next(model=model,store=store,complete=complete,correction=correction)

    def _run_next(self,*,model=None,store=None,complete=None,correction=None):
        state=self.state();config=state['config'];number=state['completed']+1
        if number>config['episodes']:return {'status':'architecture_complete_unreviewed','production_approved':False,'human_review_completed':False}
        if complete is None:
            from .model_routing import ModelRoutes,inventory
            approved=next((m for m in ModelRoutes(store).models() if m['name']==model and m['approved']),None) if store else None
            if not approved or inventory().get(model)!=approved['digest']:raise AgentError('An exact installed and owner-approved research model is required.')
        schema=obj({'event_id':enum([f'episode_{number}']),'cause_id':enum([state['previous_event']]),'actor':enum(config['actors']),
                    **{k:text_schema(100) for k in ('want','choice','cost','consequence','emotion_action','hook_decision')},
                    'state_before':obj({k:enum([v]) for k,v in state['state'].items()}),
                    'state_after':obj({k:text_schema(100) for k in state['state']}),
                    'plant':{'type':'array','maxItems':3,'items':enum([f'e{number}_s{i}' for i in range(1,4)])},
                    'payoff':{'type':'array','maxItems':3,'items':enum(list(state['planted']))} if state['planted'] else {'type':'array','maxItems':0}})
        data={'brief':config['brief'],'episode':number,'total_episodes':config['episodes'],'state_before':state['state'],
              'previous_event':state['previous_event'],'planted_setups':state['planted'],'parent_sha256':state['parent_sha256']}
        if correction is not None:data['targeted_correction']=correction
        check=lambda r:self.validate(r,number,config,state['state'],state['previous_event'],state['planted'])
        result=StagedDraft(self.folder).run(f'ep{number:03}','story',data,
            'একটি মৌলিক পর্বের ছোট কাঠামো লিখুন। চরিত্রের চাওয়া থেকে দামি সিদ্ধান্ত, ফল ও পরবর্তী সিদ্ধান্তের হুক আসবে। '
            'state_before অপরিবর্তিত নিন; সিদ্ধান্তে state_after-এর অন্তত একটি তথ্য বদলাবে। নতুন fact key নয়। '
            'setup চাইলে e'+str(number)+'_s1 আকারে plant করুন; payoff কেবল আগের episode-এ planted ID। আবেগ কাজে দেখান। '
            'targeted_correction থাকলে শুধু ওই ভুল সংশোধন করুন; মূল source facts বা অনুমোদন বদলাবেন না।',
            schema,model=model,tokens=1024,complete=complete,check=check,guidance=config['guidance'])
        if complete is None:
            try:unchanged=inventory().get(model)==approved['digest']
            except (OSError,ValueError):unchanged=False
            if not unchanged:
                result['status']='failed';result['error']='Research model identity changed after inference.'
            result.setdefault('evidence',{})['model_digest']=approved['digest']
            result['series_identity_verified']=unchanged
            (self.folder/f'ep{number:03}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        return result
