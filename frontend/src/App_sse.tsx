import { useEffect, useState } from "react";

function App() {
  const [imgb64State, setImgb64State] = useState<string>("");

  useEffect(() => {
    const eventSource = new EventSource("http://localhost:8000/sse");
    eventSource.onmessage = (event) => {
      setImgb64State(event.data);
    };

    eventSource.onerror = (event) => {
      console.error("EventSource failed:", event);
      eventSource.close();
    };

    return () => {
      eventSource.close();
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
