import re, io
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from fastapi.responses import StreamingResponse
from app.services.resume_sections import FIELDS
def color(s):
    if re.fullmatch(r'#[0-9a-fA-F]{6}',s or ''):return RGBColor.from_string(s[1:])
    return RGBColor(79,70,229)

def new_resume(fields,accent='#245b95',font='Aptos',design='classic'):
    """Generate three real, editable Word layouts with different typographic structures."""
    if design not in ('classic','modern','executive'):
        raise ValueError('Unknown document design')
    doc=Document();section=doc.sections[0]
    section.top_margin=Inches(.64);section.bottom_margin=Inches(.58)
    section.left_margin=Inches(.76);section.right_margin=Inches(.76)
    style=doc.styles['Normal'];style.font.name=font[:60];style.font.size=Pt(9.5)
    style.paragraph_format.space_after=Pt(4)
    ink=color(accent)
    if design=='executive':
        ink=RGBColor(37,49,66)
    name=fields.get('NAME','').strip() or 'YOUR NAME'
    p=doc.add_paragraph();p.alignment=1 if design=='executive' else 0
    p.paragraph_format.space_after=Pt(4)
    r=p.add_run(name);r.bold=True;r.font.size=Pt(21 if design=='modern' else 18)
    r.font.name='Georgia' if design=='executive' else font[:60]
    r.font.color.rgb=ink
    if fields.get('CONTACT'):
        p=doc.add_paragraph(fields['CONTACT']);p.alignment=1 if design=='executive' else 0
        p.paragraph_format.space_after=Pt(11)
    if design=='modern':
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        p=doc.add_paragraph();p.paragraph_format.space_after=Pt(5)
        pbdr=OxmlElement('w:pBdr'); bottom=OxmlElement('w:bottom')
        for key,value in [('val','single'),('sz','18'),('color',accent.lstrip('#') if re.fullmatch(r'#[0-9a-fA-F]{6}',accent) else '245B95')]:
            bottom.set(qn('w:'+key),value)
        pbdr.append(bottom);p._p.get_or_add_pPr().append(pbdr)
    for key in FIELDS[2:]:
        value=fields.get(key,'').strip()
        if not value:continue
        h=doc.add_paragraph();h.paragraph_format.space_before=Pt(10)
        h.paragraph_format.space_after=Pt(4)
        r=h.add_run(key.title() if design!='executive' else key.upper())
        r.bold=True;r.font.size=Pt(10 if design!='executive' else 9.5)
        r.font.color.rgb=ink
        for line in value.splitlines():
            if line.strip():
                p=doc.add_paragraph()
                p.paragraph_format.space_after=Pt(2)
                line=line.strip()
                if line.startswith('• '):
                    p.style='List Bullet';line=line[2:]
                p.add_run(line)
    return doc

def iter_paragraphs(doc):
    def table_paras(table):
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:yield p
                for t in cell.tables:yield from table_paras(t)
    for p in doc.paragraphs:yield p
    for table in doc.tables:yield from table_paras(table)
    for section in doc.sections:
        for part in (section.header,section.footer):
            for p in part.paragraphs:yield p
            for table in part.tables:yield from table_paras(table)

def replace_placeholders(doc,fields):
    """Replace {{NAME}} etc in user DOCX, including placeholders split between runs.
    Retains formatting of the first run covered by each placeholder and document layout.
    """
    count=0
    pattern=re.compile(r'\{\{\s*('+ '|'.join(FIELDS)+r')\s*\}\}',re.I)
    for p in iter_paragraphs(doc):
        if not p.runs:continue
        joined=''.join(r.text for r in p.runs)
        if not pattern.search(joined):continue
        # Map each char back to run and offset; process matches backwards.
        for match in list(pattern.finditer(joined))[::-1]:
            start,end=match.span();value=fields.get(match.group(1).upper(),'')
            positions=[]
            for ri,r in enumerate(p.runs):positions.extend((ri,j) for j in range(len(r.text)))
            if end>len(positions):continue
            a,ao=positions[start];b,bo=positions[end-1]
            if a==b:
                old=p.runs[a].text;p.runs[a].text=old[:ao]+value+old[bo+1:]
            else:
                first=p.runs[a];first.text=first.text[:ao]+value
                for idx in range(a+1,b):p.runs[idx].text=''
                last=p.runs[b];last.text=last.text[bo+1:]
            count+=1
    return count

def response_doc(doc,name):
    buf=io.BytesIO();doc.save(buf);buf.seek(0)
    return StreamingResponse(buf,media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',headers={'Content-Disposition':f'attachment; filename="{name}"'})
