import { useRef } from "react";


type Message = {
  role: "user" | "model";
  text: string;
};

type ChatformProps = {
  chatHistory: Message[]; 
  setChatHistory: React.Dispatch<React.SetStateAction<Message[]>>; 
  generateBotResponse: (history: Message[]) => void; 
};

const PLACEHOLDER = "...";

const Chatform: React.FC<ChatformProps> = ({ chatHistory, setChatHistory, generateBotResponse }) => {

    const inputRef = useRef<HTMLInputElement>(null);

    

    const handleFormSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const userMessage = inputRef.current?.value.trim();

        if (!userMessage) return
        if (inputRef.current) {
            inputRef.current.value = "";
        }
        const newHistory: Message[] = [
            ...chatHistory,
            { role: "user", text: userMessage },
        ];

        setChatHistory([...newHistory, { role: "model", text: PLACEHOLDER }]);
        
        generateBotResponse(newHistory);    
    };  

    return (
        <form action="" className="chat-form" onSubmit={handleFormSubmit}>
            <input ref={inputRef} type="text" placeholder="Message..." className="message-input" required />
            <button className="material-symbols-outlined">arrow_upward</button>
        </form>
    )
};


export default Chatform





