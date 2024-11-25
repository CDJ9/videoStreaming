let localStream;
const peerConnections = {};

async function initializeWebRTC() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: true
        });
        document.getElementById("localVideo").srcObject = localStream;
    } catch (err) {
        console.error("Error accessing media devices:", err);
        updateDebugInfo("Error accessing camera/mic");
    }
}

initializeWebRTC();