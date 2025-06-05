import React, { useEffect, useState } from "react";
import nestleBackground from "./assets/nestle background.png";
import Chatbot from "./Components/Chatbot";

const App: React.FC = () => {
  const [coords, setCoords] = useState<{ latitude: number; longitude: number } | null>(null);


  useEffect(() => {
    // Geolocation detection
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        ({ coords }) => {
          const { latitude, longitude } = coords;
          
          setCoords({ latitude, longitude });
          
          fetch("https://nestle2-158884498350.us-central1.run.app/user_location", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ latitude, longitude }),
          })
            .then(() =>  console.log("Coordinates sent"))
            .catch((err) => console.error("Geolocation sending error :", err));
        },
        (error) => console.error("Geolocation error :", error)
      );
    } else {
      console.error("Geolocation is not supported by this browser.");
    }
  }, []);


  return (
    <div
      style={{
        minHeight: "100vh",
        background: `url(${nestleBackground}) center/cover no-repeat fixed`,
      }}
    >
      <Chatbot coords={coords}/>
    </div>
  );
};

export default App;
