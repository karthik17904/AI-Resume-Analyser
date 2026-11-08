import io,os,fitz,pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.pdf_templates import store_pdf,render_pdf

client=TestClient(app)

def pdf_sample():
    doc=fitz.open();p=doc.new_page(width=595,height=842)
    p.insert_text((48,55),'EXAMPLE RESUME TEMPLATE',fontsize=19)
    p.draw_rect(fitz.Rect(45,95,550,99),fill=(.15,.3,.7),color=None)
    data=doc.tobytes();doc.close();return data

def test_template_preview_returns_real_png():
    r=client.post('/api/pdf-template/preview',files={'template':('sample.pdf',pdf_sample(),'application/pdf')})
    assert r.status_code==200,r.text
    obj=r.json();assert obj['page_count']==1
    assert obj['preview'].startswith('data:image/png;base64,')
    assert len(obj['template_id'])==32

def test_template_overlay_preserves_artwork():
    r=client.post('/api/pdf-template/preview',files={'template':('sample.pdf',pdf_sample(),'application/pdf')})
    key=r.json()['template_id']
    e=client.post('/api/pdf-template/export',json={'template_id':key,'fields':{'NAME':'Alex Engineer'},'mappings':[{'field':'NAME','x':8,'y':18,'width':80,'height':9,'fontSize':18,'page':0,'whiteout':False}]})
    assert e.status_code==200,e.text
    output=fitz.open(stream=e.content,filetype='pdf');txt=output[0].get_text()
    assert 'EXAMPLE RESUME TEMPLATE' in txt and 'Alex Engineer' in txt
    output.close()

def test_template_invalid_or_oversized():
    r=client.post('/api/pdf-template/preview',files={'template':('fake.pdf',b'not a pdf','application/pdf')})
    assert r.status_code==415
    r=client.post('/api/pdf-template/preview',files={'template':('huge.pdf',b'%PDF-'+b'x'*(8*1024*1024),'application/pdf')})
    assert r.status_code==413

def test_template_refuses_text_that_does_not_fit():
    key,_,_,_=store_pdf(pdf_sample())
    r=client.post('/api/pdf-template/export',json={'template_id':key,'fields':{'EXPERIENCE':'Too much text '*100},'mappings':[{'field':'EXPERIENCE','x':10,'y':18,'width':10,'height':2,'fontSize':15,'page':0}]})
    assert r.status_code==422
