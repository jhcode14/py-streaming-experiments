import { Button, TextField, Stack } from "@mui/material";
import { useRef, useState } from "react";

function App() {
  const rtcpConnectionRef = useRef<RTCPeerConnection | null>(null);
  const localVideo = useRef<HTMLVideoElement>(null);
  const remoteVideo = useRef<HTMLVideoElement>(null);

  // Input field states
  const [yourOffer, setYourOffer] = useState("");
  const [peerOffer, setPeerOffer] = useState("");
  const [yourAnswer, setYourAnswer] = useState("");
  const [peerAnswer, setPeerAnswer] = useState("");

  // Button click handlers
  const handleCreateOffer = async () => {
    await createOffer();
    // TODO: Set the offer in the yourOffer state
  };

  const handleCreateAnswer = async () => {
    await createAnswer();
    // TODO: Implement create answer logic
  };

  const handleConsumeAnswer = async () => {
    await consumeAnswer();
    // TODO: Implement consume answer logic
  };

  const createOffer = async () => {
    // check rtcp connection already exists, if not, create
    if (rtcpConnectionRef.current == null) {
      rtcpConnectionRef.current = new RTCPeerConnection({
        iceServers: [
          {
            urls: "stun:stun.l.google.com:19302",
          },
        ],
      });
    }
    const media = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true,
    });
    for (const track of media.getTracks()) {
      rtcpConnectionRef.current.addTrack(track, media);
    }
    localVideo.current!.srcObject = media;

    rtcpConnectionRef.current.ontrack = (e: RTCTrackEvent) => {
      const streams = e.streams[0];
      remoteVideo.current!.srcObject = streams;
    };

    rtcpConnectionRef.current.onicecandidate = (
      e: RTCPeerConnectionIceEvent
    ) => {
      if (e.candidate == null) {
        setYourOffer(rtcpConnectionRef.current?.localDescription?.sdp ?? "");
      }
    };

    const offer = await rtcpConnectionRef.current.createOffer();
    await rtcpConnectionRef.current.setLocalDescription(offer);
  };

  const createAnswer = async () => {
    // check rtcp connection already exists, if not, create
    if (rtcpConnectionRef.current == null) {
      rtcpConnectionRef.current = new RTCPeerConnection({
        iceServers: [
          {
            urls: "stun:stun.l.google.com:19302",
          },
        ],
      });
    }
    const media = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true,
    });
    for (const track of media.getTracks()) {
      rtcpConnectionRef.current.addTrack(track, media);
    }
    localVideo.current!.srcObject = media;

    rtcpConnectionRef.current.ontrack = (e: RTCTrackEvent) => {
      const streams = e.streams[0];
      remoteVideo.current!.srcObject = streams;
    };

    rtcpConnectionRef.current.setRemoteDescription(
      new RTCSessionDescription({ type: "offer", sdp: peerOffer })
    );

    rtcpConnectionRef.current.onicecandidate = (
      e: RTCPeerConnectionIceEvent
    ) => {
      if (e.candidate == null) {
        setYourAnswer(rtcpConnectionRef.current?.localDescription?.sdp ?? "");
      }
    };

    const answer = await rtcpConnectionRef.current.createAnswer();
    await rtcpConnectionRef.current.setLocalDescription(answer);
  };

  const consumeAnswer = async () => {
    rtcpConnectionRef.current?.setRemoteDescription(
      new RTCSessionDescription({ type: "answer", sdp: peerAnswer })
    );
  };

  return (
    <>
      <h1>WebRTC Demo</h1>
      <Stack spacing={1}>
        <Button variant="contained" onClick={handleCreateOffer}>
          Create Offer
        </Button>
        <TextField
          id="outlined-basic"
          label="Your Offer"
          variant="outlined"
          multiline
          value={yourOffer}
          onChange={(e) => setYourOffer(e.target.value)}
        />
        <Button variant="contained" onClick={handleCreateAnswer}>
          Create Answer
        </Button>
        <TextField
          id="outlined-basic"
          label="Peer's Offer"
          variant="outlined"
          multiline
          value={peerOffer}
          onChange={(e) => setPeerOffer(e.target.value)}
        />
        <TextField
          id="outlined-basic"
          label="Your Answer"
          variant="outlined"
          multiline
          value={yourAnswer}
          onChange={(e) => setYourAnswer(e.target.value)}
        />
        <Button variant="contained" onClick={handleConsumeAnswer}>
          Consume Answer
        </Button>
        <TextField
          id="outlined-basic"
          label="Peer's Answer"
          variant="outlined"
          multiline
          value={peerAnswer}
          onChange={(e) => setPeerAnswer(e.target.value)}
        />
      </Stack>
      <video autoPlay playsInline ref={localVideo}></video>
      <video autoPlay playsInline ref={remoteVideo}></video>
    </>
  );
}

export default App;
