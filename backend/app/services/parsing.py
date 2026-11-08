import io
from pathlib import Path
from fastapi import UploadFile, HTTPException
MAX_SIZE = 5 * 1024 * 1024
async def file_text(upload:UploadFile):
    raw=await upload.read(MAX_SIZE+1)
    if len(raw)>MAX_SIZE:raise HTTPException(413,'Maximum file size is 5 MB.')
    ext=Path(upload.filename or '').suffix.lower()
    try:
        if ext=='.pdf':
            from pypdf import PdfReader
            return '\n'.join(page.extract_text() or '' for page in PdfReader(io.BytesIO(raw)).pages)
        if ext=='.docx':
            from docx import Document
            d=Document(io.BytesIO(raw))
            return '\n'.join([p.text for p in d.paragraphs]+[c.text for t in d.tables for row in t.rows for c in row.cells])
        if ext=='.txt':return raw.decode('utf-8-sig')
    except Exception as e:raise HTTPException(422,'Could not read the file: '+str(e))
    raise HTTPException(415,'Only PDF, DOCX and TXT files are supported.')
