const logOutput = document.getElementById('log-output');

function connect() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(`${wsProtocol}//${window.location.host}/ws/monitor`);

    const addLine = (text, className) => {
        const line = document.createElement('div');
        line.className = `log-line ${className || ''}`;
        line.textContent = text;
        logOutput.appendChild(line);
        window.scrollTo(0, document.body.scrollHeight);
    };

    socket.onopen = () => {
        addLine("INFO: Connected to Brain Monitor...");
    };

    socket.onmessage = (event) => {
        const text = event.data;
        let className = '';
        if (text.includes('tool_code')) className = 'tool';
        if (text.includes('error')) className = 'error';
        if (text.includes('"role": "user"')) className = 'user';
        if (text.includes('"role": "assistant"')) className = 'assistant';
        addLine(text, className);
    };

    socket.onclose = () => {
        addLine("ERROR: Connection lost. Reconnecting in 3s...", 'error');
        setTimeout(connect, 3000);
    };

    socket.onerror = () => {
        socket.close();
    }
}

connect();
