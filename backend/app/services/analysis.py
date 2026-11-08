import re, uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from app.core.catalog import ROLES
from app.services.nlp import extract_skills, flatten, section_detection, similarity
from app.repositories import analyses as repository
def analyse(text, filename='pasted-resume.txt', jd='', job_title=''):
    if len(text.strip())<40: raise HTTPException(422,'Resume must contain at least 40 characters of readable text.')
    groups=extract_skills(text)
    known=flatten(groups)
    sections=section_detection(text)
    email=bool(re.search(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}',text))
    phone=bool(re.search(r'(?:\+?\d[\d\s().-]{8,}\d)',text))
    links=bool(re.search(r'github\.com|linkedin\.com|https?://',text,re.I))
    bullets=len(re.findall(r'(?m)^\s*(?:[-*•]|\d+[.)])\s+',text))
    metrics=len(re.findall(r'\b\d+(?:\.\d+)?\s*(?:%|percent|users|projects|hours|months|years|x\b|\+)',text,re.I))
    contact=min(15, (7 if email else 0)+(5 if phone else 0)+(3 if links else 0))
    structure=round(25*sum(sections.values())/len(sections))
    content=min(30, (10 if sections['Experience'] else 0)+(8 if sections['Projects'] else 0)+(8 if len(known)>=5 else len(known))+(4 if len(text.split())>=180 else 0))
    impact=min(20, bullets*2+metrics*4)
    readability=min(10, (5 if 180<=len(text.split())<=1100 else 2)+(5 if len(text.splitlines())>=10 else 2))
    score=min(100,contact+structure+content+impact+readability)
    roles=[{'name':r,'match':round(100*len(set(known)&set(req))/len(req)),'matched':sorted(set(known)&set(req))} for r,req in ROLES.items()]
    roles.sort(key=lambda x:x['match'],reverse=True)
    best=roles[0]['name']
    target=job_title.strip() or best
    target_skills=ROLES.get(target,ROLES[best])
    jd_skills=flatten(extract_skills(jd)) if jd.strip() else []
    wanted=jd_skills if jd_skills else target_skills
    missing=sorted(set(wanted)-set(known))
    skill_match=round(100*len(set(known)&set(wanted))/max(1,len(wanted)))
    jd_similarity=similarity(text,jd) if jd.strip() else None
    match=round(0.75*skill_match+0.25*jd_similarity) if jd_similarity is not None else skill_match
    tips=[]
    if not email or not phone: tips.append('Add a professional email address and phone number near the top.')
    if not links: tips.append('Include a GitHub, portfolio, or LinkedIn profile link.')
    for s,present in sections.items():
        if not present and s!='Certifications':tips.append('Add a clearly labeled '+s.lower()+' section.')
    if bullets<3: tips.append('Use concise achievement-focused bullet points for experience and projects.')
    if metrics<2: tips.append('Quantify impact with measurable outcomes (percentages, time saved, users, or scale).')
    if missing: tips.append('Prioritize these missing target skills: '+', '.join(missing[:5])+'.')
    if len(text.split())<180:tips.append('Add relevant detail and results; the resume currently has limited content.')
    roadmap=[{'step':i+1,'skill':skill,'action':f'Learn {skill}, build one demonstrable mini-project, and describe the result on your resume.'} for i,skill in enumerate(missing[:6])]
    summary={'email_present':email,'phone_present':phone,'links_present':links,'word_count':len(text.split()),'bullets':bullets,'metrics':metrics}
    result={'id':str(uuid.uuid4()),'created_at':datetime.now(timezone.utc).isoformat(),'filename':filename,'job_title':target,'score':score,'predicted_role':best,'skill_groups':groups,'skills':known,'section_checks':sections,'score_breakdown':{'Contact':contact,'Structure':structure,'Content':content,'Impact':impact,'Readability':readability},'roles':roles,'target_match':match,'similarity':jd_similarity,'matched_skills':sorted(set(known)&set(wanted)),'missing_skills':missing,'recommendations':tips[:9],'roadmap':roadmap,'stats':summary,'job_description_provided':bool(jd.strip()),'preview':text[:1200]}
    repository.save(result)
    return result
