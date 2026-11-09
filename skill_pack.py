"""Install and verify the three original, public-safe Markdown skills.

Standard library only. No network, credential access, agent execution or sending.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
SKILLS=('source-grounded-brief','permission-first-followup','measurement-honesty')
MAX_FILE=100000


def digest(raw):return hashlib.sha256(raw).hexdigest()


def read_public(relative):
    p=ROOT/relative
    if p.is_symlink() or not p.is_file() or p.resolve().parent!=p.parent.resolve() or p.stat().st_size>MAX_FILE:
        raise ValueError('missing, unsafe or oversized public asset')
    if not p.resolve().is_relative_to(ROOT):raise ValueError('asset escapes repository')
    return p.read_bytes()


def verify():
    manifest=json.loads(read_public('pack-manifest.json'))
    expected=manifest['files']
    if set(manifest)!= {'schema','files','skills','purpose'} or manifest['schema']!=1 or manifest['skills']!=list(SKILLS):
        raise ValueError('unexpected manifest contract')
    actual=set()
    for path in ROOT.rglob('*'):
        rel=path.relative_to(ROOT)
        if rel.parts[0] in {'.git','.agents','demo-workspace'} or '__pycache__' in rel.parts:continue
        if path.is_symlink():raise ValueError('symlink in publication tree')
        if path.is_file() and rel.as_posix()!='pack-manifest.json':actual.add(rel.as_posix())
    if actual!=set(expected):raise ValueError('extra or missing publication files')
    for name,sha in expected.items():
        if not isinstance(name,str) or Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('invalid manifest path')
        if digest(read_public(name))!=sha:raise ValueError('hash mismatch: '+name)
    return {'verified':True,'file_count':len(expected)+1,'skills':list(SKILLS),'manifest_sha256':digest(read_public('pack-manifest.json')),'network_requests':0}


def show(skill):
    if skill not in SKILLS:raise ValueError('unknown skill')
    raw=read_public('skills/'+skill+'/SKILL.md')
    return {'skill':skill,'sha256':digest(raw),'markdown':raw.decode()}


def install(workspace,skills):
    verify()
    if not skills or len(skills)!=len(set(skills)) or any(s not in SKILLS for s in skills):
        raise ValueError('select unique known skills')
    root=Path(workspace).absolute()
    # Never resolve through a symlink supplied by an operator or nested workspace.
    for candidate in [root,*root.parents]:
        if candidate.is_symlink():raise ValueError('symlink workspace denied')
    root.mkdir(parents=True,exist_ok=True)
    base=root/'.agents'/'skills'
    for candidate in [root/'.agents',base]:
        if candidate.is_symlink():raise ValueError('symlink destination denied')
        candidate.mkdir(exist_ok=True)
    checked=[]
    for skill in skills:
        if skill not in SKILLS:raise ValueError('unknown skill')
        directory=base/skill
        if directory.is_symlink():raise ValueError('symlink skill directory denied')
        target=directory/'SKILL.md'
        if target.exists() or target.is_symlink():raise ValueError('refusing to overwrite an installed skill')
        checked.append((directory,target,read_public('skills/'+skill+'/SKILL.md')))
    installed=[]
    for directory,target,raw in checked:
        directory.mkdir(exist_ok=True)
        fd=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as f:f.write(raw)
        if target.read_bytes()!=raw:raise RuntimeError('installation readback mismatch')
        installed.append({'skill':directory.name,'path':str(target),'sha256':digest(raw)})
    return {'installed':installed,'executed_skill_instructions':False,'network_requests':0}


def example(skill):
    verify()
    if skill not in SKILLS:raise ValueError('unknown skill')
    data=json.loads(read_public('examples/'+skill+'.json'))
    if data.get('data_class')!='synthetic_public_example':raise ValueError('example must disclose synthetic input')
    if skill=='source-grounded-brief':
        source=read_public('skills/source-grounded-brief/SKILL.md').decode()
        if data['quote'] not in source:raise ValueError('example citation not supported')
        result={'answer':data['quote'],'source':'skills/source-grounded-brief/SKILL.md','source_sha256':digest(source.encode()),'why':data['why'],'how':data['how'],'what':data['what'],'publication_approved':False}
    elif skill=='permission-first-followup':
        permitted=data['channel_consent'] is True and data['opted_out'] is False
        result={'draft_eligible_in_example':permitted,'draft':data['draft'] if permitted else None,'send_allowed':False,'required_live_checks':['channel consent','current opt-out','reply ledger','human approval']}
    else:
        events=data['events'];seen={};duplicates=0
        for event in events:
            if set(event)!= {'event_id','visitor','name'} or event['name'] not in {'visit','conversion'}:raise ValueError('bad example event')
            if event['event_id'] in seen:
                if seen[event['event_id']]!=event:raise ValueError('event collision')
                duplicates+=1
            else:seen[event['event_id']]=event
        visitors={e['visitor'] for e in seen.values() if e['name']=='visit'}
        converters={e['visitor'] for e in seen.values() if e['name']=='conversion'}
        if not converters<=visitors:raise ValueError('conversion without visitor')
        result={'unique_visitors':len(visitors),'unique_converters':len(converters),'duplicates_removed':duplicates,'conversion_rate':len(converters)/len(visitors) if visitors else None,'production_measurement':False}
    return {'skill':skill,'data_class':data['data_class'],'result':result,'network_requests':0}


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    sub.add_parser('verify');sub.add_parser('list')
    for verb in ['show','example']:sub.add_parser(verb).add_argument('skill',choices=SKILLS)
    ip=sub.add_parser('install');ip.add_argument('--workspace',required=True);ip.add_argument('--skill',action='append',choices=SKILLS)
    args=p.parse_args()
    try:
        if args.action=='verify':result=verify()
        elif args.action=='list':result={'skills':list(SKILLS)}
        elif args.action=='show':result=show(args.skill)
        elif args.action=='example':result=example(args.skill)
        else:result=install(args.workspace,args.skill or SKILLS)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (ValueError,OSError,RuntimeError) as exc:
        print(json.dumps({'status':'blocked','reason':str(exc)}));return 2

if __name__=='__main__':raise SystemExit(main())
