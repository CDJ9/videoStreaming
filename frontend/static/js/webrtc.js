class WebRTCManager {
    constructor() {
        this.peerConnections = {};
        this.setupWebRTC();
    }

    async setupWebRTC() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true
            });
            this.handleStream(stream);
        } catch (error) {
            console.error('Error accessing media devices:', error);
        }
    }

    handleStream(stream) {
        const remoteVideos = document.getElementById('remoteVideos');
        const videoElement = document.createElement('video');
        videoElement.srcObject = stream;
        videoElement.autoplay = true;
        videoElement.muted = true;
        remoteVideos.appendChild(videoElement);
    }
}

const webrtcManager = new WebRTCManager();