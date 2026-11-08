import io, json, os
from pathlib import Path
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from docx import Document
from app.api.schemas import ImprovePayload, FieldsPayload
from app.services.resume_sections import FIELDS, parse_resume, tune_local
from app.services.ai_rewriter import gemini_rewrite
from app.services.documents import new_resume, replace_placeholders, response_doc
router=APIRouter(prefix='/api/studio',tags=['Resume Studio'])
MAX_FILE=5*1024*1024

@router.get('/config')
def config():return {'gemini_available':bool(os.getenv('GEMINI_API_KEY')),'modes':['local','gemini'],'template_formats':['DOCX','PDF overlay']}

@router.post('/improve')
def improve(payload:ImprovePayload):
    original=parse_resume(payload.resume_text)
    edited,changes=tune_local(original,payload.job_description,payload.target_role)
    if payload.mode=='gemini':
        edited=gemini_rewrite(original,payload.job_description,payload.target_role,os.getenv('GEMINI_API_KEY',''))
        changes=['AI-suggested rewrite. Review facts before export.']
    elif payload.mode!='local':raise HTTPException(400,'Unknown improvement mode')
    return {'fields':edited,'original_fields':original,'changes':changes,'mode':payload.mode,'notice':'Review all suggestions for accuracy. The application does not certify factual accuracy.'}

@router.post('/export')
async def export_resume(payload_json:str=Form(...),template:UploadFile|None=File(None)):
    try:payload=FieldsPayload.model_validate_json(payload_json)
    except Exception:raise HTTPException(422,'Invalid resume fields')
    fields={k:str(payload.fields.get(k,'')).strip()[:12000] for k in FIELDS}
    if template and template.filename:
        if not template.filename.lower().endswith('.docx'):raise HTTPException(415,'Only DOCX custom templates are supported.')
        data=await template.read(MAX_FILE+1)
        if len(data)>MAX_FILE:raise HTTPException(413,'Maximum template size is 5 MB')
        try:doc=Document(io.BytesIO(data))
        except Exception:raise HTTPException(422,'Invalid DOCX template')
        if replace_placeholders(doc,fields)==0:raise HTTPException(422,'No supported {{FIELD}} placeholders found in custom template.')
    else:
        if payload.design not in ('classic','modern','executive'):raise HTTPException(422,'Unknown design')
        doc=new_resume(fields,payload.accent,payload.font,payload.design)
    return response_doc(doc,'AI_Resume_Analyser_Resume.docx')

@router.get('/template/sample')
def sample_template():return response_doc(new_resume({k:'{{'+k+'}}' for k in FIELDS}),'Customisable_Resume_Template.docx')
