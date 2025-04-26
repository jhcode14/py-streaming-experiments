import { useEffect, useState } from "react";
import { io } from "socket.io-client";

// Iimplementation for Socket.io

const URL = "http://localhost:3000";
const socket = io(URL);

function App() {
  const [imgb64State, setImgb64State] = useState<string>("");

  useEffect(() => {
    socket.on("connect", () => {
      console.log("connected to server");
      socket.send("start");
    });

    socket.on("onclose", () => {
      console.log("disconnected from server");
    });

    socket.on("message", (data) => {
      setImgb64State(data);
    });

    socket.on("error", (event) => {
      console.error("error", event);
    });

    return () => {
      socket.close();
    };
  }, []);

  return (
    <div>
      <h1>Hello World</h1>
      <img src={`data:image/png;base64,${imgb64State}`} alt="screenshot" />
    </div>
  );
}

export default App;
