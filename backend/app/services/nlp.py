import re
from app.core.catalog import SKILLS, ALIASES, COMMON_WORDS
def extract_skills(text: str):
    found={}
    for category, items in SKILLS.items():
        matches=[]
        for skill in items:
            patterns=ALIASES.get(skill,[re.escape(skill)])
            if any(re.search(r'(?<!\w)(?:'+p+r')(?!\w)',text,re.I) for p in patterns):matches.append(skill)
        found[category]=matches
    return found

def flatten(groups): return sorted({s for values in groups.values() for s in values})

def keywords(text):
    tokens=re.findall(r'[a-zA-Z][a-zA-Z+#.]{2,}',text.lower())
    return [t for t in tokens if t not in COMMON_WORDS and not t.isdigit()]

def similarity(a,b):
    if not a.strip() or not b.strip(): return 0
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        matrix=TfidfVectorizer(stop_words='english',ngram_range=(1,2)).fit_transform([a,b])
        return int(round(float(cosine_similarity(matrix[0],matrix[1])[0,0])*100))
    except (ImportError, ValueError):
        x,y=set(keywords(a)),set(keywords(b))
        return int(round(100*len(x&y)/max(1,len(x|y))))

def section_detection(text):
    patterns={'Summary':r'\b(summary|objective|profile|about me)\b', 'Experience':r'\b(experience|employment|work history|internship)\b', 'Education':r'\b(education|academic|bachelor|master|b\.?tech|b\.?e\.?|university|college)\b', 'Projects':r'\b(projects?|portfolio)\b', 'Skills':r'\b(technical skills|skills|technologies|tech stack)\b', 'Certifications':r'\b(certifications?|certificates?|credentials)\b'}
    return {s:bool(re.search(p,text,re.I)) for s,p in patterns.items()}
