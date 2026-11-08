export type Fields = Record<'NAME'|'CONTACT'|'SUMMARY'|'SKILLS'|'EXPERIENCE'|'PROJECTS'|'EDUCATION'|'CERTIFICATIONS',string>;
export const FIELD_KEYS: (keyof Fields)[] = ['NAME','CONTACT','SUMMARY','SKILLS','EXPERIENCE','PROJECTS','EDUCATION','CERTIFICATIONS'];
export const blankFields = (): Fields => Object.fromEntries(FIELD_KEYS.map(k=>[k,''])) as Fields;
export type Analysis={id:string; score:number; predicted_role:string; target_match:number; filename:string; skills:string[];missing_skills:string[];recommendations:string[];score_breakdown:Record<string,number>;section_checks:Record<string,boolean>;roles:{name:string;match:number}[];stats:{word_count:number;bullets:number;metrics:number};roadmap:{skill:string;action:string}[]};
export type MapItem={id:string;field:keyof Fields;page:number;x:number;y:number;width:number;height:number;fontSize:number;color:string;whiteout:boolean};
export type PdfTemplate={template_id:string;preview:string;page_count:number;page_size:{width:number;height:number}};
export async function api<T>(path:string,options?:RequestInit):Promise<T>{
 const res=await fetch('/api'+path,options);if(!res.ok){let error='Request failed';try{const j=await res.json();error=typeof j.detail==='string'?j.detail:JSON.stringify(j.detail||j)}catch{error=`Server returned ${res.status}`}throw new Error(error)}return res.json() as Promise<T>;
}
export async function download(path:string,options:RequestInit,name:string){const r=await fetch('/api'+path,options);if(!r.ok){let d='Export failed';try{d=(await r.json()).detail||d}catch{}throw new Error(d)}const b=await r.blob();const u=URL.createObjectURL(b);const a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),2000)}
