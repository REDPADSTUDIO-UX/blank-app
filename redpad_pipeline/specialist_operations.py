"""Production scheduling, promotional planning and read-only release preparation."""
from .specialists import need,text,number,records,finding
from .agents import AGENTS


def process(key,rows,data):
    derived={};findings=[]
    if key=='production_manager':
        from .readiness import inspect_resources
        records(rows,['id','agent','dependencies','estimated_seconds','gpu_required','vram_gb','state','artifacts','cost_bdt'])
        ids={r['id'] for r in rows};jobs={r['id']:r for r in rows};visited=set();active=set();order=[]
        def visit(jid):
            need(jid not in active,'Production dependency cycle.')
            if jid in visited:return
            active.add(jid)
            for dep in jobs[jid]['dependencies']:visit(dep)
            active.remove(jid);visited.add(jid);order.append(jid)
        for r in rows:
            need(r['agent'] in AGENTS and isinstance(r['dependencies'],list) and set(r['dependencies'])<=ids,'Invalid department/dependency.')
            need(number(r['estimated_seconds']) and number(r['vram_gb'],0,256) and type(r['gpu_required']) is bool,'Invalid resource requirement.')
            need(r['state'] in ('pending','running','blocked','failed','awaiting_approval','approved'),'Unknown production state.')
            need(r['cost_bdt']==0 and isinstance(r['artifacts'],list),'Paid work prohibited; artifact list required.')
        for r in rows:visit(r['id'])
        resources=inspect_resources(False);finish={};batches={};blocked=[]
        for jid in order:
            r=jobs[jid];start=max([finish[d] for d in r['dependencies']] or [0]);finish[jid]=start+r['estimated_seconds']
            level=max([batches[d]+1 for d in r['dependencies']] or [0]);batches[jid]=level
            if r['gpu_required'] and not resources['cuda_device']:blocked.append(jid)
        ready=[r['id'] for r in rows if r['state']=='pending' and r['id'] not in blocked and all(jobs[d]['state']=='approved' for d in r['dependencies'])]
        derived.update(order=order,parallel_batches=[[jid for jid in order if batches[jid]==level] for level in sorted(set(batches.values()))],
                       ready=ready,resource_blocked=blocked,resources=resources,critical_path_estimate_seconds=max(finish.values()),
                       estimates_verified=False,paid_provisioning=False,approval_checkpoints=[r['id'] for r in rows if r['state']=='awaiting_approval'],
                       inventory={r['id']:r['artifacts'] for r in rows},recovery='Explicit Engine.retry/recover only; no resource provisioning')
    elif key=='growth':
        records(rows,['id','audience','genre','title_bn','title_en','description_bn','description_en','keywords','thumbnail','campaign','release_date','trailer','metrics'])
        for r in rows:
            need(all(text(r[k]) and len(r[k])<=100 for k in ('title_bn','title_en')),'Promotional titles must be 1–100 characters (internal limit).')
            need(all(text(r[k]) and len(r[k])<=5000 for k in ('description_bn','description_en')),'Invalid description.')
            need(isinstance(r['keywords'],list) and all(text(v) for v in r['keywords']) and len(','.join(r['keywords']))<=500,'Invalid keywords.')
            from datetime import date
            try:date.fromisoformat(r['release_date'])
            except (ValueError,TypeError):need(False,'Invalid release calendar date.')
            need(isinstance(r['metrics'],list),'Supplied analytics records required.')
            for m in r['metrics']:
                need(isinstance(m,dict) and all(number(m.get(k)) for k in ('impressions','views','clicks','engagements','conversions','spend_bdt')),'Invalid supplied metrics.')
            from .marketing import metric_summary
            r['analytics_summary']=metric_summary(r['metrics'])
        derived.update(concept_comparison=[dict(id=r['id'],bn_title_length=len(r['title_bn']),en_title_length=len(r['title_en']),keywords=len(r['keywords']),audience=r['audience']) for r in rows],
                       analytics_provenance='Supplied data; no platform fetch',posting=False)
    elif key=='youtube':
        from .youtube import channel_id,YouTubeError
        from .specialist_media import asset
        records(rows,['id','channel_id','channel_name','title','description','keywords','thumbnail','video','action','oauth_scope','connection','checks'])
        readonly='https://www.googleapis.com/auth/youtube.readonly'
        for r in rows:
            try:channel_id(r['channel_id'])
            except YouTubeError as exc:need(False,str(exc))
            need(r['action']=='prepare' and r['oauth_scope']==readonly,'Only read-only preparation is authorized; upload/publish/schedule prohibited.')
            need(text(r['title']) and len(r['title'])<=100 and text(r['description']) and len(r['description'])<=5000,'Invalid release title/description.')
            need(isinstance(r['keywords'],list) and all(text(v) for v in r['keywords']) and len(','.join(r['keywords']))<=500,'Invalid release keywords.')
            asset(r['thumbnail']);asset(r['video']);need(r['connection'] in ('missing','unverified'),'Connection claims require existing secure OAuth UI verification.')
            need(isinstance(r['checks'],dict) and set(r['checks'])=={'media_qc','rights','owner_review'} and all(type(v) is bool for v in r['checks'].values()),'Release checks required.')
            if not all(r['checks'].values()):findings.append(finding(r['id'],'incomplete_release_checks','all checks reviewed',r['checks'],key,'blocker'))
        derived.update(release_state='Prepared metadata — publishing disabled',connection='Not connected/verified by this workflow; use existing YouTube Connect',
                       analytics_interface=dict(scope=readonly,operations=['channel_profile','video_statistics'],transport='Existing secure GoogleOAuth adapter only; not called'),
                       upload=False,publish=False,schedule=False,owner_approval=False)
    else:need(False,'Unknown specialist department.')
    return derived,findings
