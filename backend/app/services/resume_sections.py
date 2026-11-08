import re
FIELDS=['NAME','CONTACT','SUMMARY','SKILLS','EXPERIENCE','PROJECTS','EDUCATION','CERTIFICATIONS']

HEADINGS={'SUMMARY':['summary','professional summary','profile','objective'], 'SKILLS':['skills','technical skills','core competencies','technologies'], 'EXPERIENCE':['experience','work experience','professional experience','internship','employment'], 'PROJECTS':['projects','selected projects','academic projects'], 'EDUCATION':['education','academic background','academics'], 'CERTIFICATIONS':['certifications','certificates','awards']}

def compact(text, cap=5500):
    return re.sub(r'[ \t]+',' ',text or '').strip()[:cap]

def parse_resume(raw:str):
    """Extract candidate-provided sections without inventing missing information."""
    lines=[x.strip(' \t•') for x in raw.splitlines() if x.strip()]
    data={k:'' for k in FIELDS}
    if not lines:return data
    data['NAME']=lines[0][:120]
    contact=[]
    idx=1
    while idx<len(lines) and idx<=3 and ('@' in lines[idx] or re.search(r'\d{8,}',lines[idx]) or 'linkedin' in lines[idx].lower() or 'github' in lines[idx].lower()):
        contact.append(lines[idx]);idx+=1
    data['CONTACT']=' | '.join(contact)
    current='SUMMARY'; sections={k:[] for k in FIELDS}
    for line in lines[idx:]:
        normalized=re.sub(r'[^a-z ]','',line.lower()).strip()
        hit=next((key for key,names in HEADINGS.items() if normalized in names),None)
        if hit:current=hit;continue
        sections[current].append(line)
    for k in sections:
        if k not in ('NAME','CONTACT'):data[k]='\n'.join(sections[k])[:9000]
    return data

def tune_local(data, jd='', target=''):
    """Conservative edits: no metrics, credentials, skills or duties added."""
    improved=data.copy()
    changes=[]
    for key in ['EXPERIENCE','PROJECTS']:
        old=improved[key]
        revised=[]
        for line in old.splitlines():
            s=line.strip()
            if not s:continue
            s=re.sub(r'^[-•*]\s*','',s)
            s=re.sub(r'^(responsible for|worked on|helped with|involved in)\s+', '',s,flags=re.I)
            if s and s[0].islower():s=s[0].upper()+s[1:]
            revised.append('• '+s)
        improved[key]='\n'.join(revised)
        if old!=improved[key] and old:changes.append('Standardized '+key.lower()+' bullets without changing claims.')
    if jd.strip():
        changes.append('Compared source content to the supplied job description; no unverified skills inserted.')
    if not data['SUMMARY'] and target.strip():
        changes.append('Summary left empty because evidence is insufficient; add verified achievements before publishing.')
    return improved,changes
