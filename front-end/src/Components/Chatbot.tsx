import Icon from "./icon"
import "../css/Chatbot.css"
import {  useEffect, useRef, useState } from "react";
import Chatform from "./Chatform";
import ChatMessage from "./ChatMessage";


type Message = {
    role: "user" | "model";
    text: string;
};

type ChatbotProps = {
  coords: { latitude: number; longitude: number } | null;
};


const API_URL = "https://nestle2-158884498350.us-central1.run.app/ask";
const PLACEHOLDER = "...";   


const Chatbot: React.FC<ChatbotProps> = ({ coords }) => {

    const [chatHistory, setChatHistory] = useState<Message[]>([]);
    const chatBodyRef = useRef<HTMLDivElement>(null);
    const [showChatBot, setShowChatBot] = useState(false)
    
     const generateBotResponse = async (history: Message[]) => {
    try {
      const question = history[history.length - 1].text; 

      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          question, 
          latitude: coords?.latitude,
          longitude: coords?.longitude }),
      });

      if (!res.ok) throw new Error("Network Error");

      const { answer } = await res.json();

      setChatHistory((prev) =>
        prev.map((m) =>
          m.role === "model" && m.text === PLACEHOLDER
            ? { ...m, text: answer }
            : m
        )
      );
    } catch (err) {
      console.error(err);
      setChatHistory((prev) =>
        prev
          .filter((m) => !(m.role === "model" && m.text === PLACEHOLDER)) // retire le "..."
          .concat({
            role: "model",
            text: "Oops! An error has occurred.",
          })
      );
    }
  };

    useEffect(()=> {
        chatBodyRef.current?.scrollTo({top: chatBodyRef.current.scrollHeight, behavior: "smooth"})
    }, [chatHistory])



    return (
        <div className={`container ${showChatBot ? "show-chatbot" : ""}`}>

            <button onClick={() => setShowChatBot(prev => !prev)} id="chatbot-toggler">
                <span className="material-symbols-outlined">mode_comment</span>
                <span className="material-symbols-outlined">close</span>
            </button>

            <div className="chatbot-popup">
                <div className="chat-header">
                    <div className="header-info">
                        <Icon />
                        <h2 className="logo-text">SMARTIE</h2>
                    </div>
                    <button onClick={() => setShowChatBot(prev => !prev)} className="material-symbols-outlined arrow-white">keyboard_arrow_down</button>
                </div>

                <div ref={chatBodyRef} className="chat-body">
                    <div className="message bot-message">
                        <Icon />
                        <p className="message-text">
                            Hey! I'm Smartie, your personal MadeWithNestlé assistant. Ask me anything, and I'll quickly search the entire site to find the answers you need!
                        </p>
                    </div>

                    {chatHistory.map((chat, index) => (
                        <ChatMessage key={index} chat={chat} />
                    ))}

                </div>


                <div className="chat-footer">
                    <Chatform chatHistory={chatHistory} setChatHistory={setChatHistory} generateBotResponse={generateBotResponse} />
                </div>


            </div>
        </div>
    )
};

export default Chatbot