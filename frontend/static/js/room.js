class RoomManager {
    constructor() {
        // Update Socket.IO client configuration
        this.socket = io('http://localhost:8000', {
            transports: ['websocket', 'polling'],
            reconnectionAttempts: 5,
            reconnectionDelay: 1000,
            autoConnect: true,
            forceNew: true,
            timeout: 20000,
            withCredentials: true
        });
        
        this.roomId = null;
        this.isLeader = false;
        
        this.setupSocketListeners();
        this.setupUIElements();
    }

    setupSocketListeners() {
        this.socket.on('connect', () => {
            console.log('Connected to server:', this.socket.id);
            document.getElementById('roomInfo').textContent = 'Connected to server';
        });

        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            document.getElementById('roomInfo').textContent = 'Connection error: ' + error.message;
        });

        this.socket.on('disconnect', (reason) => {
            console.log('Disconnected:', reason);
        });

        this.socket.on('room_state', (state) => {
            console.log('Received room state:', state);
            this.handleRoomState(state);
        });

        this.socket.on('user_joined', (data) => {
            console.log('User joined:', data);
            this.updateRoomInfo(data);
        });

        this.socket.on('user_left', (data) => {
            console.log('User left:', data);
            this.updateRoomInfo(data);
        });

        this.socket.on('error', (error) => {
            console.error('Server error:', error);
            alert(`Error: ${error.message}`);
        });
    }

    setupUIElements() {
        document.getElementById('createRoom').addEventListener('click', () => {
            this.createRoom();
        });

        document.getElementById('joinRoom').addEventListener('click', () => {
            const roomId = prompt('Enter room ID:');
            if (roomId) {
                this.joinRoom(roomId);
            }
        });
    }

    createRoom() {
        this.roomId = Math.random().toString(36).substring(7);
        this.isLeader = true;
        this.joinRoom(this.roomId);
        alert(`Room created! Share this code: ${this.roomId}`);
    }

    joinRoom(roomId) {
        console.log('Joining room:', roomId);
        this.roomId = roomId;
        this.socket.emit('join_room', { roomId: this.roomId });
    }

    handleRoomState(state) {
        console.log('Handling room state:', state);
        if (state.current_video) {
            videoManager.loadVideo(state.current_video);
        }
        if (state.leader) {
            this.isLeader = this.socket.id === state.leader;
        }
    }

    updateRoomInfo(data) {
        const roomInfo = document.getElementById('roomInfo');
        roomInfo.textContent = `Room: ${this.roomId} - Users: ${data.totalUsers}`;
        if (data.leader) {
            this.isLeader = this.socket.id === data.leader;
        }
    }
}

const roomManager = new RoomManager();