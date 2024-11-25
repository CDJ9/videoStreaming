let currentRoom = null;
let isLeader = false;

function updateDebugInfo(message) {
    const syncInfo = document.getElementById("syncInfo");
    syncInfo.textContent = `${new Date().toLocaleTimeString()}: ${message}`;
}

function createRoom() {
    currentRoom = Math.random().toString(36).substring(7);
    isLeader = true;
    joinRoom();
}

function joinRoom() {
    const roomId = currentRoom || document.getElementById("roomInput").value;
    if (!roomId) {
        alert("Please enter a room ID");
        return;
    }
    currentRoom = roomId;
    console.log("Joining room:", roomId);
    socket.emit("join_room", { roomId });
    document.getElementById("roomInfo").textContent = `Room: ${roomId}`;
    updateDebugInfo(`Joining room: ${roomId}`);
}

function assignLeader(sid) {
    isLeader = sid === socket.id;
    updateDebugInfo(`Role: ${isLeader ? "Leader" : "Follower"}`);
    document.getElementById("roomInfo").textContent += ` (${isLeader ? "Leader" : "Follower"})`;
}

// Socket event listeners
socket.on("connect", () => {
    console.log("Connected to server");
    updateDebugInfo("Connected to server");
});

socket.on("connect_error", (error) => {
    console.error("Connection error:", error);
    updateDebugInfo("Connection error: " + error.message);
});

socket.on("room_state", (data) => {
    if (data.current_video) {
        isStateChange = true;
        player.loadVideoById(data.current_video);
        if (data.video_state === "playing") {
            player.seekTo(data.current_time);
            player.playVideo();
        } else {
            player.seekTo(data.current_time);
            player.pauseVideo();
        }
        updateDebugInfo(`Received room state: ${data.video_state} at ${data.current_time}`);
    }
});

socket.on("video_state_updated", (data) => {
    if (!player || !player.seekTo) return;
    if (isLeader) return;

    isStateChange = true;
    const currentTime = player.getCurrentTime();
    const receivedTime = data.currentTime;
    const timeDiff = Math.abs(currentTime - receivedTime);
    const networkDelay = data.timestamp ? (Date.now() - data.timestamp) / 1000 : 0;
    const compensatedTime = receivedTime + (data.state === "playing" ? networkDelay : 0);

    updateDebugInfo(`Sync diff: ${timeDiff.toFixed(3)}s, Delay: ${networkDelay.toFixed(3)}s`);

    if (timeDiff > STRICT_SYNC_THRESHOLD) {
        console.log(`Strict sync: local=${currentTime}, target=${compensatedTime}`);
        player.seekTo(compensatedTime, true);
        if (data.playbackRate) {
            player.setPlaybackRate(data.playbackRate);
        }
        setTimeout(() => {
            verifySyncAccuracy(compensatedTime);
        }, 200);
    }

    if (data.state === "playing" && player.getPlayerState() !== 1) {
        player.playVideo();
    } else if (data.state === "paused" && player.getPlayerState() === 1) {
        player.pauseVideo();
    }
});

socket.on("video_changed", (data) => {
    console.log("Video changed:", data);
    updateDebugInfo(`Video changed to: ${data.videoId}`);
    if (player && player.loadVideoById) {
        player.loadVideoById(data.videoId);
    }
});

socket.on("video_buffering", (data) => {
    if (currentRoom && player) {
        isStateChange = true;
        player.pauseVideo();
        updateDebugInfo("Remote user buffering...");
        setTimeout(() => {
            if (data.state === "playing") {
                player.seekTo(data.currentTime);
                player.playVideo();
            }
        }, 1000);
    }
});