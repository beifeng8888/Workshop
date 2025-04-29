import React,{useState,useRef,useEffect} from 'react'
import marked from 'marked'
import {DOMPurify} from "dompurify";

type MessageType = 'user'|'ai';

interface ChatMessage{
    sender:string;
    content:string;
    time:string;
    type:MessageType;
    isTyping?:boolean;
}

const ChatApp:React.FC=()=>{
    const[messages,setMessages]=useState<ChatMessage[]>([
        {
            sender:'AI',
            content:'您好！我是编程助手，请问有什么可以帮助您？',
            time:new Data().toLocaleTimeString(),
            type:'ai'
        }
    ]);
    const[inputValue,setInputValue]=useState('');
    const chatHistoryRef=useRef<HTMLDivElement>(null);

    //转义特殊字符
    const escapeHtml=(unsafe)=>{
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    const SendQuestion = async() =>{
        const question = inputValue.trim();
        if(!question) return;

        //添加用户消息
        const userMessage:ChatMessage = {
            sender:'You',
            content:question,
            time:new Data().toLocaleTimeString(),
            type:'user'
        }
    }
    setMessages(prev=>[...prev,userMessage]);
    setInputValue('');

    //添加AI消息占位符
    const aiMessage:ChatMessage = {
        sender:'AI',
        content:'▌',
        time:new Date().toLocaleDateString(),
        type:'ai',
        isTyping:true
    };
    setMessages(prev=>[...prev,aiMessage])
}