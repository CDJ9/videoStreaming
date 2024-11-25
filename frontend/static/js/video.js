let player = null;
let isStateChange = false;
let lastSyncTime = 0;
let syncInterval;
let syncAttempts = 0;
let pendingVideoId = null;
let playerReady = false;

// YouTube Player initialization
function onYouTubeIframeAPIReady() {
    console.log("YouTube API Ready");
    player = new YT.Player("youtubePlayer", {
        height: '390',
        width: '640',
        videoId: '',
        playerVars: {
            'playsinline': 1,
            'controls': 1,
            'enablejsapi': 1,
            'origin': window.location.origin,
            'rel': 0
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange,
            'onError': onPlayerError
        }
    });
}

function onPlayerReady(event) {
    console.log("YouTube player ready");
    playerReady = true;
    updateDebugInfo("YouTube player ready");
    if (pendingVideoId) {
        changeVideo(pendingVideoId);
        pendingVideoId = null;
    }
    startVideoSync();
}

function onPlayerError(event) {
    console.error('Player error:', event);
    updateDebugInfo(`Player error: ${event.data}`);
}

function startVideoSync() {
    if (syncInterval) clearInterval(syncInterval);
    syncInterval = setInterval(() => {
        if (currentRoom && player && playerReady && player.getPlayerState) {
            sendVideoState();
        }
    }, SYNC_INTERVAL);
}

function sendVideoState() {
    if (!isLeader || !player || !playerReady) return;

    const state = player.getPlayerState();
    const currentTime = player.getCurrentTime();
    const timestamp = Date.now();

    if (timestamp - lastSyncTime > 500) {
        lastSyncTime = timestamp;
        socket.emit("video_state_change", {
            roomId: currentRoom,
            state: state === 1 ? "playing" : "paused",
            currentTime: currentTime,
            timestamp: timestamp,
            playbackRate: player.getPlaybackRate()
        });
    }
}

async function searchVideos() {
    const query = document.getElementById("searchInput").value;
    if (!query.trim()) return;

    try {
        const response = await fetch("http://localhost:8000/search-youtube", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                query: query,
                api_key: YOUTUBE_API_KEY
            })
        });

        const data = await response.json();
        displaySearchResults(data.items);
    } catch (error) {
        console.error("Search error:", error);
        updateDebugInfo("Search failed: " + error.message);
    }
}

function displaySearchResults(videos) {
    const resultsDiv = document.getElementById("searchResults");
    resultsDiv.innerHTML = "";

    if (!videos || videos.length === 0) {
        resultsDiv.innerHTML = "<p>No results found</p>";
        return;
    }

    videos.forEach((video) => {
        const videoDiv = document.createElement("div");
        videoDiv.className = "video-item";
        videoDiv.innerHTML = `
            <img src="${video.snippet.thumbnails.default.url}" alt="${video.snippet.title}">
            <div>
                <h3>${video.snippet.title}</h3>
                <p>${video.snippet.description}</p>
            </div>
        `;
        videoDiv.onclick = () => changeVideo(video.id.videoId);
        resultsDiv.appendChild(videoDiv);
    });
}

function changeVideo(videoId) {
    if (!currentRoom) {
        alert("Please join a room first!");
        return;
    }
    if (!isLeader) {
        alert("Only the room leader can change videos");
        return;
    }

    console.log("Changing video to:", videoId);
    updateDebugInfo(`Changing video to: ${videoId}`);

    if (!player || !playerReady) {
        console.log("Player not ready, queueing video");
        pendingVideoId = videoId;
        return;
    }

    try {
        player.loadVideoById(videoId);
        socket.emit("change_video", {
            roomId: currentRoom,
            videoId: videoId
        });
    } catch (error) {
        console.error("Error changing video:", error);
        updateDebugInfo("Error changing video: " + error.message);
    }
}

function onPlayerStateChange(event) {
    if (!isStateChange && currentRoom && isLeader && playerReady) {
        const state = event.data === YT.PlayerState.PLAYING ? "playing" : "paused";

        if (event.data === YT.PlayerState.BUFFERING) {
            socket.emit("video_buffering", {
                roomId: currentRoom,
                currentTime: player.getCurrentTime(),
                state: state
            });
            updateDebugInfo("Buffering...");
        } else {
            sendVideoState();
            updateDebugInfo(`State changed to: ${state}`);
        }
    }
    isStateChange = false;
}

// Updates from socket events
socket.on("video_changed", (data) => {
    console.log("Video changed from server:", data);
    if (player && playerReady) {
        player.loadVideoById(data.videoId);
    } else {
        pendingVideoId = data.videoId;
    }
});

socket.on("video_state_updated", (data) => {
    if (!player || !playerReady || isLeader) return;

    isStateChange = true;
    const currentTime = player.getCurrentTime();
    const timeDiff = Math.abs(currentTime - data.currentTime);

    if (timeDiff > SYNC_THRESHOLD) {
        player.seekTo(data.currentTime, true);
    }

    if (data.state === "playing" && player.getPlayerState() !== 1) {
        player.playVideo();
    } else if (data.state === "paused" && player.getPlayerState() === 1) {
        player.pauseVideo();
    }
});

window.addEventListener('load', () => {
    // Load YouTube API if not already loaded
    if (!window.YT) {
        const tag = document.createElement('script');
        tag.src = 'https://www.youtube.com/iframe_api';
        const firstScriptTag = document.getElementsByTagName('script')[0];
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
    }
});