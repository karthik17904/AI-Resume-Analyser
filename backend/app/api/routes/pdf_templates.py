import base64, json
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from pydantic import BaseModel, Field
from app.services.pdf_templates import store_pdf,render_pdf

router=APIRouter(prefix='/api/pdf-template',tags=['Custom PDF template'])

class PdfExport(BaseModel):
    template_id:str
    fields:dict[str,str]
    mappings:list[dict]

@router.post('/preview')
async def preview(template:UploadFile=File(...)):
    if not (template.filename or '').lower().endswith('.pdf'):raise HTTPException(415,'Select a PDF template.')
    data=await template.read(8*1024*1024+1)
    key,image,size,pages=store_pdf(data)
    return {'template_id':key,'preview':'data:image/png;base64,'+base64.b64encode(image).decode(),'page_size':size,'page_count':pages}

@router.post('/export')
def export(payload:PdfExport):
    return render_pdf(payload.template_id,payload.fields,payload.mappings)
