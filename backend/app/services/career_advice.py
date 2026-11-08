from app.api.schemas import ChatPayload
from app.repositories import analyses as repository
def chat(payload:ChatPayload):
    msg=payload.message.lower().strip()
    context=None
    if payload.analysis_id:
        context=repository.get(payload.analysis_id)
    if any(x in msg for x in ['missing','gap','improve','learn','roadmap']):
        answer=('Your highest-priority gaps are '+', '.join(context['missing_skills'][:5])+'. ' if context and context['missing_skills'] else 'Focus on the skills listed in your target job description. ')+ 'Build small practical projects, add achievements with numbers, and tailor your resume to each role.'
    elif any(x in msg for x in ['score','ats','rating']):
        answer=(f"Your heuristic resume quality score is {context['score']}/100. " if context else '')+'Improve section organization, show measurable impact, add relevant skills, and use straightforward formatting. This score is an estimate, not a real employer ATS result.'
    elif any(x in msg for x in ['role','career','job']):
        answer=(f"Your current best matched role is {context['predicted_role']}. " if context else '')+'Compare your skills against multiple job descriptions, choose a target role, and demonstrate the required tools in practical projects.'
    elif any(x in msg for x in ['interview','prepare']):
        answer='Prepare concise STAR stories for projects, collaboration and setbacks. Review your strongest technical skills, practice explaining architecture decisions, and solve role-relevant coding or case questions.'
    else:answer='I can help with your resume score, missing skills, suitable roles, learning roadmap, and interview preparation. Ask me about one of those topics. This is a local rule-based assistant, not a hosted LLM.'
    return {'reply':answer,'mode':'local-guidance'}
