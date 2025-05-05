import { Button, TextField, Stack } from "@mui/material";
import { useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";

const URL = "http://localhost:3000";
const RTCP_CONFIG = {
  iceServers: [
    {
      urls: "stun:stun.l.google.com:19302",
    },
  ],
};

function App() {
  const [roomName, setRoomName] = useState("");
  const rtcpConnectionMapRef = useRef<Map<string, RTCPeerConnection>>(
    new Map()
  );
  const socketRef = useRef<Socket | null>(null);
  const localMediaRef = useRef<MediaStream | null>(null);

  const localVideoRef = useRef<HTMLVideoElement>(null);
  const [remoteStreams, setRemoteStreams] = useState<Map<string, MediaStream>>(
    new Map()
  );

  const handlePeers = async (ids: string[]) => {
    console.log(`Handling peers: ${ids.join(", ")}`);
    for (const id of ids) {
      if (!rtcpConnectionMapRef.current.has(id)) {
        // create new rtcpconnection if it dosen't already exist
        console.log(`Creating new RTCPeerConnection for peer ${id}`);
        const newConnection = new RTCPeerConnection(RTCP_CONFIG);

        rtcpConnectionMapRef.current.set(id, newConnection);
        for (const track of localMediaRef.current!.getTracks()) {
          rtcpConnectionMapRef.current
            .get(id)
            ?.addTrack(track, localMediaRef.current!);
        }
        console.log(`Added local tracks to peer ${id}`);

        newConnection.ontrack = (e: RTCTrackEvent) => {
          const stream = e.streams[0];
          console.log(`Received track from peer ${id}`);
          setRemoteStreams((prev) => new Map(prev).set(id, stream));
        };

        // add event to add ip to offer
        newConnection.onicecandidate = (e: RTCPeerConnectionIceEvent) => {
          if (e.candidate == null) {
            console.log(`ICE candidate found for peer ${id}`, e.candidate);
            socketRef.current!.emit(
              "sendOffer",
              id,
              newConnection.localDescription?.sdp
            );
          }
        };

        // create offer
        console.log(`Creating offer for peer ${id}`);
        const offer = await newConnection.createOffer();
        await newConnection.setLocalDescription(offer);
        console.log(`Set local description for peer ${id}`);
      }
    }
  };

  const handleOffer = async (senderId: string, offer: string) => {
    // got offer, now return an answer
    console.log(`Received offer from ${senderId}`);
    //create connection if does not exist
    if (!rtcpConnectionMapRef.current.has(senderId)) {
      console.log(
        `Creating new RTCPeerConnection for peer ${senderId} (from offer)`
      );
      rtcpConnectionMapRef.current.set(
        senderId,
        new RTCPeerConnection(RTCP_CONFIG)
      );
    }
    const connection = rtcpConnectionMapRef.current.get(senderId);

    connection!.ontrack = (e: RTCTrackEvent) => {
      const stream = e.streams[0];
      console.log(`Received track from peer ${senderId}`);
      setRemoteStreams((prev) => new Map(prev).set(senderId, stream));
    };

    //add your track to connections
    for (const track of localMediaRef.current!.getTracks()) {
      connection!.addTrack(track, localMediaRef.current!);
    }
    console.log(`Added local tracks to peer ${senderId}`);

    connection!.onicecandidate = (e: RTCPeerConnectionIceEvent) => {
      if (e.candidate == null) {
        console.log(
          `ICE candidate found for peer ${senderId} (from offer)`,
          e.candidate
        );
        socketRef.current?.emit(
          "sendAnswer",
          senderId,
          connection!.localDescription?.sdp ?? ""
        );
      }
    };

    //store offer in remote
    console.log(`Setting remote description from offer for peer ${senderId}`);
    await connection!.setRemoteDescription(
      new RTCSessionDescription({ type: "offer", sdp: offer })
    );

    //generate answer
    console.log(`Creating answer for peer ${senderId}`);
    const answer = await connection!.createAnswer();

    //store answer
    await connection!.setLocalDescription(new RTCSessionDescription(answer));
    console.log(`Set local description (answer) for peer ${senderId}`);
  };

  const handleAnswer = async (senderId: string, answer: string) => {
    console.log(`Received answer from ${senderId}`);
    //store answer
    if (!rtcpConnectionMapRef.current.has(senderId)) {
      console.log("Connection not found for sender", senderId);
      return;
    }
    // store answer
    console.log(`Setting remote description from answer for peer ${senderId}`);
    await rtcpConnectionMapRef.current
      .get(senderId)
      ?.setRemoteDescription(
        new RTCSessionDescription({ type: "answer", sdp: answer })
      );
    console.log(`Successfully set remote description for peer ${senderId}`);
  };

  useEffect(() => {
    socketRef.current = io(URL);

    const init = async () => {
      localMediaRef.current = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });
      localVideoRef.current!.srcObject = localMediaRef.current;

      socketRef.current!.on("connect", () => {
        console.log("connected to server");
      });

      socketRef.current!.on("onclose", () => {
        console.log("disconnected from server");
      });

      socketRef.current!.on("peers", (ids: string[]) => {
        handlePeers(ids);
      });

      socketRef.current!.on("offer", (id: string, offer: string) => {
        handleOffer(id, offer);
      });

      socketRef.current!.on("answer", (id: string, answer: string) => {
        handleAnswer(id, answer);
      });

      socketRef.current!.on("someoneDisconnected", (id: string) => {
        const handlePeerDisconnected = (userId: string) => {
          setRemoteStreams((previous) => {
            const newMap = new Map(previous);
            newMap.delete(userId);
            return newMap;
          });
          rtcpConnectionMapRef.current.delete(userId);
        };
        handlePeerDisconnected(id);
      });

      socketRef.current!.on("error", (event) => {
        console.error("error", event);
      });
    };

    init();

    return () => {
      socketRef.current!.close();
    };
  }, []);

  const handleJoinRoom = () => {
    // sent event join room
    socketRef.current!.emit("join", roomName);
  };

  return (
    <>
      <Stack spacing={2}>
        <div>
          <h3>Local Video</h3>
          <video ref={localVideoRef} autoPlay muted playsInline />
        </div>

        {Array.from(remoteStreams.entries()).length > 0 && (
          <div>
            <h3>Remote Videos</h3>
            <Stack direction="row" spacing={2} sx={{ flexWrap: "wrap" }}>
              {Array.from(remoteStreams.entries()).map(([id, stream]) => (
                <div key={id}>
                  <video
                    autoPlay
                    playsInline
                    ref={(element) => {
                      if (element) {
                        element.srcObject = stream;
                      }
                    }}
                    style={{ width: "300px", height: "225px" }}
                  />
                </div>
              ))}
            </Stack>
          </div>
        )}

        <Button variant="contained" onClick={handleJoinRoom}>
          Join Button
        </Button>
        <TextField
          id="outlined-basic"
          label="Room Name"
          variant="outlined"
          multiline
          value={roomName}
          onChange={(e) => setRoomName(e.target.value)}
        />
      </Stack>
    </>
  );
}

export default App;
