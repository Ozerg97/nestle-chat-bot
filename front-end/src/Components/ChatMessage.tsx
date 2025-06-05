import Icon from "./icon";
import DOMPurify from "dompurify";
import { marked } from "marked";


type Chat = {
  role: "user" | "model";
  text: string;
};

type ChatMessageProps = {
  chat: Chat;
};


const ChatMessage: React.FC<ChatMessageProps> = ({ chat }) => {


  const isBot = chat.role === "model";
  const safeHtml = isBot
    ? DOMPurify.sanitize(marked.parse(chat.text) as string) : "";   //  ← cast ici
    
    



  return (
     <div className={`message ${isBot ? "bot" : "user"}-message`}>
      {isBot && <Icon />}
      {isBot ? (
       
        <div
          className="message-text"
          dangerouslySetInnerHTML={{ __html: safeHtml }}
        />
      ) : (
        <p className="message-text">{chat.text}</p>
      )}
    </div>


  )

}


export default ChatMessage