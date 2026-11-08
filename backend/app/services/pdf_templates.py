"""PDF templates are preserved as underlying artwork; mapped field text is stamped onto a copy.

PDFs are fixed-layout. There is no generic lossless way to reflow arbitrary documents.
A template mapper therefore asks users where content should be placed.
"""
from pathlib import Path
from uuid import uuid4
import io, os, time
import fitz
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

MAX_BYTES=8*1024*1024
STORE=Path(os.getenv('PDF_TEMPLATE_STORAGE',str(Path(__file__).resolve().parents[3]/'.pdf_templates')))
STORE.mkdir(parents=True,exist_ok=True)
ALLOWED_FIELDS={'NAME','CONTACT','SUMMARY','SKILLS','EXPERIENCE','PROJECTS','EDUCATION','CERTIFICATIONS'}

def store_pdf(data:bytes):
    if len(data)>MAX_BYTES:raise HTTPException(413,'PDF template must be under 8 MB.')
    if not data.startswith(b'%PDF-'):raise HTTPException(415,'Please upload a real PDF document.')
    try:
        doc=fitz.open(stream=data,filetype='pdf')
        if doc.needs_pass:raise HTTPException(422,'Password-protected PDFs are not supported.')
        if not 1<=len(doc)<=8:raise HTTPException(422,'PDF must have 1–8 pages.')
        page=doc[0]
        if max(page.rect.width,page.rect.height)>3000:raise HTTPException(422,'Page dimensions are too large.')
        pix=page.get_pixmap(matrix=fitz.Matrix(min(1.5,1000/page.rect.width),min(1.5,1000/page.rect.width)),alpha=False)
        preview=pix.tobytes('png')
        size={'width':round(page.rect.width,1),'height':round(page.rect.height,1)}
        count=len(doc)
        doc.close()
    except HTTPException:raise
    except Exception as e:raise HTTPException(422,'PDF could not be processed.') from e
    key=uuid4().hex
    (STORE/f'{key}.pdf').write_bytes(data)
    return key, preview, size, count

def read_pdf(key:str):
    if len(key)!=32 or any(c not in '0123456789abcdef' for c in key):raise HTTPException(422,'Invalid template identifier.')
    path=STORE/f'{key}.pdf'
    if not path.exists():raise HTTPException(404,'Template not found. Upload the PDF again.')
    if time.time()-path.stat().st_mtime>24*3600:
        path.unlink(missing_ok=True)
        raise HTTPException(410,'Template expired. Upload the PDF again.')
    return path

def render_pdf(key:str,fields:dict,mappings:list):
    """Coordinates in percentages of page dimensions. Text is truncated to fit chosen boxes."""
    path=read_pdf(key)
    if len(mappings)>40:raise HTTPException(422,'At most 40 field placements are supported.')
    doc=fitz.open(path)
    for m in mappings:
        field=m.get('field')
        if field not in ALLOWED_FIELDS:raise HTTPException(422,'Unsupported field.')
        try:
            page_no=int(m.get('page',0));x=float(m['x']);y=float(m['y']);w=float(m.get('width',70));h=float(m.get('height',9));size=float(m.get('fontSize',10))
        except (TypeError,ValueError,KeyError):raise HTTPException(422,'Invalid field coordinates.')
        if not(0<=page_no<len(doc) and 0<=x<=100 and 0<=y<=100 and 3<=w<=100 and 2<=h<=100 and 6<=size<=26):raise HTTPException(422,'Field coordinates out of bounds.')
        page=doc[page_no]; rect=page.rect
        box=fitz.Rect(rect.x0+x/100*rect.width,rect.y0+y/100*rect.height,rect.x0+min(100,x+w)/100*rect.width,rect.y0+min(100,y+h)/100*rect.height)
        if box.is_empty:continue
        val=str(fields.get(field,'')).strip()[:5000]
        if not val:continue
        if m.get('whiteout'):
            # Paint only the selected field box; existing artwork elsewhere remains unchanged.
            page.draw_rect(box,color=None,fill=(1,1,1),overlay=True)
        colorstr=str(m.get('color','#17233d'))
        try:rgb=tuple(int(colorstr[i:i+2],16)/255 for i in (1,3,5)) if len(colorstr)==7 and colorstr.startswith('#') else (0.1,0.14,0.24)
        except ValueError:rgb=(0.1,0.14,0.24)
        # Reduce font until text fits, never invent or drop candidate facts silently.
        lines=val.replace('\r','').split('\n')
        if len(lines)>24:raise HTTPException(422,f'{field} contains too many lines for PDF placement. Reduce text or use DOCX export.')
        rc=-1
        for fs in [size,size-1,size-2,size-3,size-4,6]:
            if fs<6:continue
            rc=page.insert_textbox(box,val,fontsize=fs,fontname='helv',color=rgb,overlay=True,lineheight=1.17)
            if rc>=0:break
        if rc<0:raise HTTPException(422,f'{field} does not fit the selected PDF box. Increase the box height or reduce the content.')
    data=doc.tobytes(garbage=3,deflate=True)
    doc.close()
    return StreamingResponse(io.BytesIO(data),media_type='application/pdf',headers={'Content-Disposition':'attachment; filename="AI_Resume_Analyser_Custom_Template.pdf"'})
