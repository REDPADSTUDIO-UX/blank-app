"""Owner-triggered routing of approved QC findings to exact reviewed task versions."""
import json
from .agents import AgentError,encode


def route_revision(store,qc_task,target_task):
    with store.tx() as db:
        qc=store._task(db,qc_task);target=store._task(db,target_task)
        if qc['agent']!='qc' or qc['state']!='Approved':raise AgentError('Owner-approved QC task required.')
        store._current(db,qc)
        refs=json.loads(qc['refs'])
        if not any(r['id']==target_task and r['revision']==target['revision'] for r in refs):raise AgentError('Revision routing requires the exact reviewed dependency version.')
        row=db.execute('SELECT payload FROM outputs WHERE task=? AND revision=?',(qc_task,qc['revision'])).fetchone()
        body=json.loads(json.loads(row[0])['summary'])
        routes=body['artifact'].get('derived',{}).get('revision_routes',{})
        findings=routes.get(target['agent'],[])
        if not findings:raise AgentError('No findings for the target department.')
    # Trusted owner workspace action; model outputs never call this helper.
    store.review(target_task,target['revision'],'Request revision',encode({'qc_task':qc_task,'findings':findings}),'owner')
