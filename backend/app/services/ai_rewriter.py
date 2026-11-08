import json, os, re, urllib.request, urllib.error
from fastapi import HTTPException
from app.services.resume_sections import FIELDS, compact
def gemini_rewrite(data,jd,target,api_key,model=None):
    """Single compact request, strict JSON, limited input/output; no key logged or stored."""
    if not api_key:raise HTTPException(400,'Set GEMINI_API_KEY in your .env / environment to use Gemini mode.')
    prompt={
        'task':'Improve wording and relevance of an existing resume; never invent or infer employers, dates, degrees, metrics, duties, certificates, skills, or links. Preserve user facts and chronology. Empty sections stay empty. Output strictly JSON with exactly these uppercase keys: '+','.join(FIELDS)+'. No markdown.',
        'target_role':target[:100], 'job_description':compact(jd,1800),
        'verified_resume_sections':{k:compact(v,3500 if k in ('EXPERIENCE','PROJECTS') else 850) for k,v in data.items()}
    }
    req_data=json.dumps({'contents':[{'parts':[{'text':json.dumps(prompt,ensure_ascii=False)}]}], 'generationConfig':{'responseMimeType':'application/json','maxOutputTokens':1800,'temperature':0.15}},ensure_ascii=False).encode()
    model = (model or os.getenv('GEMINI_MODEL') or 'gemini-2.5-flash-lite').strip()
    if not re.fullmatch(r'[A-Za-z0-9._-]+',model):
        raise HTTPException(400,'Invalid GEMINI_MODEL value.')
    url=f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    req=urllib.request.Request(url,req_data,headers={'Content-Type':'application/json','x-goog-api-key':api_key},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=28) as response: body=json.load(response)
        txt=''.join(part.get('text','') for c in body.get('candidates',[]) for part in c.get('content',{}).get('parts',[]))
        obj=json.loads(txt)
    except urllib.error.HTTPError as exc:
        detail=exc.read(1500).decode('utf-8','replace')
        try: detail=json.loads(detail).get('error',{}).get('message',detail)
        except (ValueError,AttributeError): pass
        if exc.code==404:
            raise HTTPException(502, f'Gemini model {model} was not found or is unavailable for your API key (404). Set GEMINI_MODEL to an accessible model, choose a model returned by the Google models API. Google says: {str(detail)[:350]}')
        raise HTTPException(502, f'Gemini HTTP {exc.code}: {str(detail)[:400]}')
    except (urllib.error.URLError,TimeoutError,ValueError,KeyError) as exc:
        raise HTTPException(502,'Gemini request failed: '+str(exc)[:250])
    if not isinstance(obj,dict):raise HTTPException(502,'Gemini response was not valid resume JSON.')
    result={k:compact(obj.get(k,''),9000) if data.get(k) else '' for k in FIELDS}
    # Safety: retain exact supplied identity/contact; all other sections require user review.
    result['NAME']=data['NAME'];result['CONTACT']=data['CONTACT']
    return result
