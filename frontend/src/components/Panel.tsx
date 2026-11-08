import {motion} from 'framer-motion';import type {ReactNode} from 'react';
export function Panel({children,className='',delay=0}:{children:ReactNode;className?:string;delay?:number}){return <motion.section initial={{opacity:0,y:13}} animate={{opacity:1,y:0}} transition={{duration:.38,delay}} className={'panel '+className}>{children}</motion.section>}
export function Header({eyebrow,title,subtitle}:{eyebrow:string;title:string;subtitle:string}){return <header className="page-header"><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{subtitle}</p></header>}
export function Tag({children}:{children:ReactNode}){return <span className="tag">{children}</span>}
export function Alert({message}:{message:string}){return message?<div role="alert" className="alert">{message}</div>:null}
