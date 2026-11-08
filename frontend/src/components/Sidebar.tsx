import {LayoutDashboard,ScanText,FilePenLine,History,Sun,Moon,PanelLeftClose,PanelLeftOpen,Sparkles,ShieldCheck} from 'lucide-react';
export type View='dashboard'|'analyse'|'studio'|'history';
const nav=[{id:'dashboard',icon:LayoutDashboard,label:'Overview'},{id:'analyse',icon:ScanText,label:'Analyse resume'},{id:'studio',icon:FilePenLine,label:'Resume studio'},{id:'history',icon:History,label:'Analysis history'}] as const;
export function Sidebar({view,setView,theme,toggleTheme,collapsed,setCollapsed}:{view:View;setView:(v:View)=>void;theme:string;toggleTheme:()=>void;collapsed:boolean;setCollapsed:(v:boolean)=>void}){
 return <aside className={'sidebar '+(collapsed?'collapsed':'')}><div className="brand"><div className="brand-mark"><Sparkles size={21}/></div>{!collapsed&&<div><strong>AI Resume</strong><small>ANALYSER STUDIO</small></div>}</div>
 <div className="nav-label">{!collapsed?'WORKSPACE':'•'}</div><nav aria-label="Main navigation">{nav.map(({id,icon:Icon,label})=><button key={id} className={'nav-item '+(view===id?'active':'')} onClick={()=>setView(id)} title={label}><Icon size={19}/>{!collapsed&&<span>{label}</span>}</button>)}</nav>
 <div className="sidebar-bottom">{!collapsed&&<div className="sidebar-note"><ShieldCheck size={18}/><span>Your resume stays on your local server unless you choose AI mode.</span></div>}
 <button className="nav-item" onClick={toggleTheme} title="Toggle color scheme">{theme==='dark'?<Sun size={19}/>:<Moon size={19}/ >}{!collapsed&&<span>{theme==='dark'?'Light mode':'Dark mode'}</span>}</button><button className="nav-item collapse" onClick={()=>setCollapsed(!collapsed)} title="Collapse sidebar">{collapsed?<PanelLeftOpen size={19}/>:<PanelLeftClose size={19}/ >}{!collapsed&&<span>Collapse</span>}</button></div></aside>
}
