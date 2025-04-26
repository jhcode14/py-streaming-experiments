import { useEffect, useRef, useState } from "react";
function App() {
  const [imgb64State, setImgb64State] = useState<string>("");
  const ws = useRef<WebSocket | null>(null);
  const frame_idx = useRef(0);

  useEffect(() => {
    ws.current = new WebSocket("ws://localhost:5000/video");

    ws.current.onopen = () => {
      console.log("connected to server");
      if (ws.current) {
        ws.current.send(String(frame_idx.current));
        frame_idx.current = frame_idx.current + 1;
      }
    };

    ws.current.onclose = () => {
      console.log("disconnected from server");
    };

    ws.current.onmessage = (event) => {
      setImgb64State(event.data);
      if (ws.current) {
        ws.current.send(String(frame_idx.current));
        frame_idx.current = frame_idx.current + 1;
      }
    };

    ws.current.onerror = (event) => {
      console.error("error", event);
    };

    return () => {
      if (ws.current) {
        ws.current.close();
        ws.current = null;
      }
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
