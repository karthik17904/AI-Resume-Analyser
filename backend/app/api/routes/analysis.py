from pathlib import Path
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from app.api.schemas import TextPayload
from app.core.catalog import ROLES
from app.services.analysis import analyse
from app.services.parsing import file_text
from app.repositories import analyses as repository
router=APIRouter(prefix='/api',tags=['Analysis'])

@router.get('/roles')
def roles():return list(ROLES)

@router.post('/analyse')
def analyse_text(payload:TextPayload):return analyse(payload.resume_text,jd=payload.job_description,job_title=payload.job_title)

@router.post('/upload')
async def upload(file:UploadFile=File(...),job_description:str=Form(''),job_title:str=Form('')):
    content=await file_text(file)
    return analyse(content,filename=Path(file.filename or 'resume').name,jd=job_description,job_title=job_title)

@router.post('/extract')
async def extract_only(file:UploadFile=File(...)):
    content=await file_text(file)
    if len(content.strip())<40:raise HTTPException(422,'No readable text found. Scanned PDFs require OCR.')
    return {'text':content,'filename':Path(file.filename or 'resume').name}

@router.get('/history')
def history():return repository.list_recent()

@router.get('/history/{analysis_id}')
def get_history(analysis_id:str):
    found=repository.get(analysis_id)
    if not found:raise HTTPException(404,'Analysis not found.')
    return found

@router.delete('/history/{analysis_id}')
def delete_history(analysis_id:str):
    if not repository.remove(analysis_id):raise HTTPException(404,'Analysis not found.')
    return {'deleted':True}
