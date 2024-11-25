// Configuration constants
const YOUTUBE_API_KEY = "AIzaSyBw25yHvV8FMBtdX2x2wkppk4B5TcpMjHA";
const SYNC_THRESHOLD = 0.5;
const SYNC_INTERVAL = 2000;
const STRICT_SYNC_THRESHOLD = 0.1;
const SYNC_CHECK_INTERVAL = 1000;
const MAX_SYNC_ATTEMPTS = 3;

// Socket.IO configuration
const socket = io("http://localhost:8000", {
    withCredentials: true,
    transports: ["websocket"]
});