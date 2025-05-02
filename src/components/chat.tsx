import React, { useState, useRef, useEffect } from 'react';
import { marked } from 'marked';
import DOMPurify from "dompurify";
import '../static/styles.css';

type MessageType = 'user' | 'ai';

interface ChatMessage {
    sender: string;
    content: string;
    time: string;
    type: MessageType;
    isTyping?: boolean;
}

const ChatApp:React.FC = () => {
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            sender: 'AI',
            content: '您好！我是编程助手，请问有什么可以帮助您？',
            time: new Date().toLocaleTimeString(),
            type: 'ai'
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const chatHistoryRef = useRef<HTMLDivElement>(null);

    // 转义特殊字符
    const escapeHtml = (unsafe: string): string => {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // 获取CSRF token
    const getCookie = (name: string): string | null => {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    const processContent = async (content: string) => {
        const escaped = escapeHtml(content);
        const parsed = await marked.parse(escaped);
        return DOMPurify.sanitize(parsed);
    };

    const SendQuestion = async () => {
        const question = inputValue.trim();
        if (!question) return;

        // 添加用户消息
        const userMessage: ChatMessage = {
            sender: 'You',
            content: question,
            time: new Date().toLocaleTimeString(),
            type: 'user'
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');

        // 添加AI消息占位符
        const aiMessage: ChatMessage = {
            sender: 'AI',
            content: '▌',
            time: new Date().toLocaleTimeString(),
            type: 'ai',
            isTyping: true
        };
        setMessages(prev => [...prev, aiMessage]);

        try {
            const csrfToken = getCookie('csrftoken');
            if (!csrfToken) throw new Error('CSRF token not found');

            const response = await fetch('api/get-ai-response/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ question })
            });

            if (!response.body) throw new Error('No response body');

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullContent = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n').filter(l => l.trim());

                for (const line of lines) {
                    if (line.trim() === '[DONE]') continue;
                    if (line.startsWith('data:')) {
                        try {
                            const data = JSON.parse(line.substring(5));
                            if (data.choices?.[0]?.delta.content) {
                                fullContent += data.choices[0].delta.content;
                                const processed = await processContent(fullContent + '<span class="blinking-cursor">▌</span>');
                                setMessages(prev => {
                                    const last = prev[prev.length - 1];
                                    if (last.isTyping) {
                                        return [
                                            ...prev.slice(0, -1),
                                            {
                                                ...last,
                                                content: processed
                                            }
                                        ];
                                    }
                                    return prev;
                                });
                            }
                        } catch (e) {
                            console.error('解析错误', e);
                        }
                    }
                }
            }

            // 移除光标
            const finalContent = await processContent(fullContent);
            setMessages(prev => {
                const last = prev[prev.length - 1];
                if (last.isTyping) {
                    return [
                        ...prev.slice(0, -1),
                        {
                            ...last,
                            content: finalContent,
                            isTyping: false
                        }
                    ];
                }
                return prev;
            });
        } catch (error) {
            console.error('请求失败:', error);
            setMessages(prev => {
                const last = prev[prev.length - 1];
                if (last.isTyping) {
                    return [
                        ...prev.slice(0, -1),
                        {
                            ...last,
                            content: '<span class="text-danger">请求失败，请重试</span>',
                            isTyping: false
                        }
                    ];
                }
                return prev;
            });
        }
    };

    useEffect(() => {
        if (chatHistoryRef.current) {
            chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
        }
    }, [messages]);

    return (
        <div className="ai-panel" style={{ height: '100vh', width:"33vw",display:'inline-block' }}>
            <div className="p-3" style={{ height: '100%', width:'100%',display: 'flex', flexDirection: 'column' }}>
                <h2 className="mb-3">编程助手</h2>
                <div
                    ref={chatHistoryRef}
                    className="overflow-auto"
                    style={{
                        height:'70vh',
                        flexGrow: 1,
                        border: '1px solid #dee2e6',
                        padding: '15px',
                        marginBottom: '15px',
                        background: 'white',
                        borderRadius: '5px',
                        minHeight: '300px',
                        maxHeight: '70vh',
                        boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.1)',
                        overflowY:'auto',
                    }}
                >
                    {messages.map((msg, index) => (
                        <div
                            key={index}
                            className={msg.type === 'user' ? 'user-message' : 'ai-message'}
                            style={{
                                marginBottom: '15px',
                                padding: '10px',
                                borderRadius: '5px',
                                background: msg.type === 'user' ? '#e3f2fd' : '#f1f1f1',
                                borderLeft: `3px solid ${msg.type === 'user' ? '#2196f3' : '#607d8b'}`
                            }}
                        >
                            <span className="time"
                                style={{ fontSize: '0.8em', color: '#6c757d', display: 'block', marginBottom: '5px' }}>
                                {msg.time}
                            </span>
                            <strong>{msg.sender}:</strong>
                            <span dangerouslySetInnerHTML={{ __html: msg.content }} />
                        </div>
                    ))}
                </div>
                <div
                    style={{
                        marginTop: 'auto',
                        background: 'white',
                        padding: '10px',
                        borderRadius: '5px',
                        boxShadow: '0 -1px 3px rgba(0,0,0,0.1)'
                    }}
                >
                    <div className="input-group" style={{marginBottom:'90px'}}>
                        <input
                            type="text"
                            className="form-control"
                            placeholder="请输入你的问题..."
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && SendQuestion()}
                            style={{width:'85%'}}
                        />
                        <button
                            className="btn btn-primary"
                            onClick={SendQuestion}
                            style={{marginLeft:'15px'}}
                        >
                            发送
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChatApp;