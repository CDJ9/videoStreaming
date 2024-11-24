class VideoManager {
    constructor() {
        this.player = null;
        this.isReady = false;
        this.setupYouTubePlayer();
        this.setupSearch();
        this.setupSocketListeners();
        this.syncThreshold = 2; // seconds threshold for syncing
        this.lastTimeUpdate = 0;
        this.ignoreStateChange = false;
    }

    setupYouTubePlayer() {
        window.onYouTubeIframeAPIReady = () => {
            this.player = new YT.Player('youtubePlayer', {
                height: '360',
                width: '640',
                videoId: '',
                playerVars: {
                    'playsinline': 1,
                    'controls': 1,
                    'enablejsapi': 1
                },
                events: {
                    'onReady': this.onPlayerReady.bind(this),
                    'onStateChange': this.onPlayerStateChange.bind(this)
                }
            });
        };
    }

    setupSocketListeners() {
        roomManager.socket.on('video_changed', (data) => {
            console.log('Video changed:', data);
            this.loadVideo(data.videoId);
        });

        roomManager.socket.on('video_state_updated', (data) => {
            console.log('Video state updated:', data);
            this.handleVideoStateUpdate(data);
        });

        roomManager.socket.on('video_buffering', (data) => {
            console.log('Video buffering:', data);
            if (!roomManager.isLeader) {
                this.handleBuffering(data);
            }
        });
    }

    onPlayerReady(event) {
        console.log('YouTube player ready');
        this.isReady = true;
    }

    onPlayerStateChange(event) {
        if (!this.isReady || this.ignoreStateChange) return;
        
        if (roomManager.isLeader) {
            const state = event.data;
            const currentTime = this.player.getCurrentTime();
            const timestamp = Date.now();
            
            roomManager.socket.emit('video_state_change', {
                roomId: roomManager.roomId,
                state: this.getStateString(state),
                currentTime: currentTime,
                timestamp: timestamp,
                playbackRate: this.player.getPlaybackRate()
            });
        }
    }

    handleVideoStateUpdate(data) {
        if (!roomManager.isLeader && this.isReady) {
            this.ignoreStateChange = true;
            
            const currentTime = this.player.getCurrentTime();
            const timeDiff = Math.abs(currentTime - data.currentTime);
            
            if (timeDiff > this.syncThreshold) {
                this.player.seekTo(data.currentTime, true);
            }

            if (data.state === 'playing' && this.player.getPlayerState() !== YT.PlayerState.PLAYING) {
                this.player.playVideo();
            } else if (data.state === 'paused' && this.player.getPlayerState() !== YT.PlayerState.PAUSED) {
                this.player.pauseVideo();
            }

            if (data.playbackRate) {
                this.player.setPlaybackRate(data.playbackRate);
            }
            
            setTimeout(() => {
                this.ignoreStateChange = false;
            }, 1000);
        }
    }

    handleBuffering(data) {
        if (this.isReady && !roomManager.isLeader) {
            this.player.seekTo(data.currentTime, true);
            if (data.state === 'paused') {
                this.player.pauseVideo();
            } else {
                this.player.playVideo();
            }
        }
    }

    getStateString(state) {
        switch (state) {
            case YT.PlayerState.PLAYING:
                return 'playing';
            case YT.PlayerState.PAUSED:
                return 'paused';
            case YT.PlayerState.BUFFERING:
                return 'buffering';
            default:
                return 'unknown';
        }
    }

    loadVideo(videoId) {
        console.log('Changing video to:', videoId);
        if (this.player && videoId) {
            this.player.loadVideoById(videoId);
            if (roomManager.isLeader) {
                roomManager.socket.emit('change_video', {
                    roomId: roomManager.roomId,
                    videoId: videoId
                });
            }
        }
    }

    onPlayerStateChange(event) {
        if (roomManager.isLeader && roomManager.socket) {
            roomManager.socket.emit('video_state_change', {
                roomId: roomManager.roomId,
                state: event.data,
                currentTime: this.player.getCurrentTime()
            });
        }
    }
}

const videoManager = new VideoManager();