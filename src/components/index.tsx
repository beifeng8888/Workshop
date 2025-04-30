import React from 'react';
import ReactDOM, {createRoot} from 'react-dom/client';
import ChatApp from "./chat";


const root = createRoot(document.querySelector('#root')as HTMLElement);
root.render(<ChatApp />);