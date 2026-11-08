import re
SKILLS = {
 'Languages': ['Python','Java','JavaScript','TypeScript','C++','C#','SQL','HTML','CSS','Go','Rust','PHP','Kotlin','Swift','R'],
 'Frameworks': ['React','Next.js','Angular','Vue','Node.js','Express','FastAPI','Flask','Django','Spring Boot','.NET','Tailwind CSS'],
 'Data & AI': ['Machine Learning','Deep Learning','NLP','TensorFlow','PyTorch','scikit-learn','Pandas','NumPy','OpenCV','LLM','Generative AI','LangChain','RAG','Computer Vision','Data Analysis','Power BI','Tableau'],
 'Cloud & DevOps': ['AWS','Azure','GCP','Docker','Kubernetes','Git','GitHub Actions','CI/CD','Linux','Terraform'],
 'Databases': ['PostgreSQL','MySQL','MongoDB','SQLite','Redis','Supabase','Firebase'],
 'Professional': ['Leadership','Communication','Problem Solving','Teamwork','Agile','Scrum','Project Management'],
}

ALIASES = {'Node.js':[r'node\.?js'], 'Next.js':[r'next\.?js'], 'React':[r'react(?:\.?js)?'], 'Vue':[r'vue(?:\.?js)?'], 'scikit-learn':[r'scikit[ -]?learn',r'sklearn'], 'C++':[r'c\+\+'], 'C#':[r'c#'],'.NET':[r'\.net'], 'CI/CD':[r'ci\s*/\s*cd'], 'LLM':[r'\bllms?\b',r'large language models?'], 'NLP':[r'\bnlp\b',r'natural language processing'], 'RAG':[r'\brag\b',r'retrieval augmented generation'], 'GCP':[r'\bgcp\b',r'google cloud'], 'AWS':[r'\baws\b',r'amazon web services']}

ROLES = {
 'AI / ML Engineer': ['Python','Machine Learning','Deep Learning','scikit-learn','TensorFlow','PyTorch','NLP','Pandas','NumPy','LLM','RAG'],
 'Data Scientist': ['Python','SQL','Machine Learning','Pandas','NumPy','scikit-learn','Data Analysis','Tableau','Power BI'],
 'Frontend Developer': ['HTML','CSS','JavaScript','TypeScript','React','Next.js','Vue','Angular','Tailwind CSS'],
 'Backend Developer': ['Python','Java','Node.js','Express','FastAPI','Django','Flask','SQL','PostgreSQL','MongoDB'],
 'Full Stack Developer': ['HTML','CSS','JavaScript','TypeScript','React','Node.js','SQL','PostgreSQL','FastAPI','Git'],
 'DevOps Engineer': ['Linux','Docker','Kubernetes','AWS','Azure','CI/CD','Git','Terraform'],
 'Data Analyst': ['SQL','Python','Excel','Power BI','Tableau','Data Analysis','Pandas'],
 'Software Engineer': ['Python','Java','C++','JavaScript','SQL','Git','Problem Solving','Agile'],
}

COMMON_WORDS = set('the and for with from are this that you your our their have will should must can using work role team strong good experience years ability skills knowledge an in on to of as is a at by be or it we a plus'.split())
