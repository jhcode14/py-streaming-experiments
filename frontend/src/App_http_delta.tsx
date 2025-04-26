import { useEffect, useState, useRef } from "react";

function App() {
  const [imgb64State, setImgb64State] = useState<string>("");
  const isFirstRef = useRef<boolean>(true);
  const isImgb64Ref = useRef<string>("");

  function base64ToBytes(base64: string) {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes;
  }

  function xorByteArray(arr1: Uint8Array, arr2: Uint8Array) {
    const result = new Uint8Array(arr1.length);
    for (let i = 0; i < result.length; i++) {
      result[i] = arr1[i] ^ arr2[i];
    }
    return result;
  }

  function bytesToBase64(bytes: Uint8Array) {
    let binary = "";
    for (let i = 0; i < bytes.length; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  useEffect(() => {
    setInterval(() => {
      fetch("http://localhost:8000/", {
        credentials: "include",
      })
        .then((res) => res.json())
        .then((data) => {
          if (isFirstRef.current) {
            setImgb64State(data.message);
            isImgb64Ref.current = data.message;
            isFirstRef.current = false;
          } else {
            const prevBytes = base64ToBytes(isImgb64Ref.current); // actual image
            const curBytes = base64ToBytes(data.message); // image diff
            const xored = xorByteArray(prevBytes, curBytes);
            const frame = bytesToBase64(xored);

            isImgb64Ref.current = frame;
            setImgb64State(frame);
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }, 120);
  }, []);

  return (
    <div>
      <h1>Hello World</h1>
      <img src={`data:image/png;base64,${imgb64State}`} alt="screenshot" />
    </div>
  );
}

export default App;
