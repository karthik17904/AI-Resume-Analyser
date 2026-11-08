from typing import Optional
from pydantic import BaseModel, Field
class TextPayload(BaseModel):
    resume_text:str
    job_description:str=''
    job_title:str=''

class ChatPayload(BaseModel):
    message:str
    analysis_id:Optional[str]=None
class ImprovePayload(BaseModel):
    resume_text:str=Field(min_length=40,max_length=45000)
    job_description:str=''
    target_role:str=''
    mode:str='local'

class FieldsPayload(BaseModel):
    fields:dict[str,str]
    accent:str='#4f46e5'
    font:str='Aptos'
    design:str='classic'
