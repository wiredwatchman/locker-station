# Locker Station - main.py
# Runs on a Raspberry Pi Pico W (MicroPython).
# Creates a Wi-Fi access point and serves a keypad web page that
# unlocks lockers by driving a relay/GPIO output for a set time.

import network
import socket
import machine
import time
import json
import gc

# Map sequential locker numbers to GPIO pins
gpio_map = {
    1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8, 10: 9, 11: 10, 12: 11,
    13: 12, 14: 13, 15: 14, 16: 15, 17: 16, 18: 17, 19: 18, 20: 19, 21: 20, 22: 21,
    23: 22, 24: 26, 25: 27, 26: 28
}

# Configure pins for lockers
lockers = {f"Locker {i}": machine.Pin(gpio_map[i], machine.Pin.OUT) for i in range(1, 27)}

# Variables for cooldown mechanism and locker reset
last_authorized_changes = {locker: 0 for locker in lockers}
cooldown_period = 15  # 15 seconds cooldown
toggle_back_timers = {locker: 12 for locker in lockers}  # All timers set to 12 seconds
reset_times = {locker: 0 for locker in lockers}

# Valid codes and their corresponding user names
# CHANGE THESE before using or publishing the project
valid_codes = {
    '2585': 'Overberg',
    '2358': 'Barnett',
    '919': 'Donohue',
    '974': 'Reynolds',
    '1022': 'Preston',
}

# Access Point configuration
# CHANGE ap_password before using or publishing the project
ap_ssid = "JosephLockerStation"
ap_password = "lockercontrol123"

# Locker logs
locker_logs = {locker: [] for locker in lockers}

# Data logging file
log_file = 'code_entries.txt'

def setup_ap():
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ap_ssid, password=ap_password)
    ap.active(True)

    while not ap.active():
        pass

    print('Access Point Mode Is Active, You can Now Connect')
    print('SSID:', ap_ssid)
    print('Password:', ap_password)
    print('IP Address To Connect to:', ap.ifconfig()[0])

def web_page():
    html = """
  <!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Aisin Tool Locker Station</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f4f8;
            text-align: center;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        h1, h2, h3 {
            color: #2c3e50;
            margin-bottom: 30px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .keypad {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            max-width: 300px;
            margin: 30px auto;
        }
        .digit, .enter-btn {
            width: 80px;
            height: 80px;
            font-size: 24px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .digit {
            background-color: #3498db;
            color: white;
        }
        .digit:hover {
            background-color: #2980b9;
        }
        .enter-btn {
            background-color: #2ecc71;
            color: white;
            grid-column: span 3;
        }
        .enter-btn:hover {
            background-color: #27ae60;
        }
        .lockers {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 30px;
        }
        .locker {
            width: 100%;
            height: 100px;
            font-size: 16px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            background-color: #2ecc71;
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
        }
        .locker:hover {
            background-color: #27ae60;
        }
        .locker.active {
            background-color: #e74c3c;
        }
        .gpio {
            font-size: 12px;
            margin-top: 5px;
        }
        .countdown {
            position: absolute;
            bottom: 5px;
            font-size: 14px;
            font-weight: bold;
            color: black;
        }
        #code-display {
            font-size: 28px;
            margin: 20px 0;
            height: 40px;
            background-color: #ecf0f1;
            border-radius: 10px;
            padding: 10px;
            letter-spacing: 5px;
        }
        #message {
            color: #e74c3c;
            height: 20px;
            margin-top: 20px;
            font-weight: bold;
        }
        #logs-container {
            margin-top: 30px;
            text-align: left;
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 5px;
        }
        #logs ul {
            list-style-type: none;
            padding-left: 0;
        }
        #logs li {
            margin-bottom: 5px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Aisin Tool Locker Station</h1>
        <div id="code-display"></div>
        <div class="keypad">
            <button class="digit" onclick="pressDigit(1)">1</button>
            <button class="digit" onclick="pressDigit(2)">2</button>
            <button class="digit" onclick="pressDigit(3)">3</button>
            <button class="digit" onclick="pressDigit(4)">4</button>
            <button class="digit" onclick="pressDigit(5)">5</button>
            <button class="digit" onclick="pressDigit(6)">6</button>
            <button class="digit" onclick="pressDigit(7)">7</button>
            <button class="digit" onclick="pressDigit(8)">8</button>
            <button class="digit" onclick="pressDigit(9)">9</button>
            <button class="digit" onclick="pressDigit(0)">0</button>
            <button class="enter-btn" onclick="enterCode()">Enter</button>
        </div>
        <div class="lockers">
                 """
    for i in range(1, 27):
        locker = f"Locker {i}"
        gpio_num = gpio_map[i]
        active = "active" if lockers[locker].value() else ""
        html += f"""
            <button class="button locker {active}" id="{locker}" onclick="pressLocker('{locker}')">
                {locker}
                <span class="gpio">GPIO {gpio_num}</span>
                <span class="countdown" id="countdown_{i}"></span>
            </button>
        """

    html += """
            </div>
            <div id="message"></div>
            <div id="logs-container">
                <h2>Locker Logs</h2>
                <div id="logs"></div>
            </div>
        </div>
        <button class="help-button" onclick="showHelp()">?</button>
        <div id="helpModal" class="help-modal">
            <div class="modal-content">
                <span class="close" onclick="closeHelp()">&times;</span>
                <h2>Help</h2>
                <p>Welcome to Aisin Tool Locker Station!</p>
                <p>1. Enter a 4-digit code using the keypad.</p>
                <p>2. After entering the code, select a locker to toggle.</p>
                <p>3. The locker will activate for 12 seconds, then automatically deactivate.</p>
                <p>4. The logs at the bottom show recent locker activities.</p>
            </div>
        </div>
        <script>
        let code = "";
        const validCodes = {"2585": "Overberg", "2358": "Barnett", "919": "Donohue", "974": "Reynolds", "1022": "Preston"};
        const toggleBackTimer = 12;  // 12 seconds for all lockers

        function pressDigit(digit) {
            if (code.length < 6) {
                code += digit;
                document.getElementById("code-display").innerText = code;
            }
        }

        function enterCode() {
            if (code.length >= 3 && code.length <= 6) {
                if (validCodes[code]) {
                    showMessage("Valid code entered. Select a locker.");
                } else {
                    showMessage("Invalid code! Please try again.");
                    countdownAndClear();
                }
            } else {
                showMessage("Enter a 3 to 6-digit code!");
            }
        }

        function pressLocker(locker) {
            if (code.length >= 3 && code.length <= 6) {
                if (validCodes[code]) {
                    const button = document.getElementById(locker);
                    button.classList.add("active");
                    startCountdown(locker);
                    addLog(locker, validCodes[code]);
                    fetch(`/locker?name=${encodeURIComponent(locker)}&code=${code}`);
                    code = "";
                    document.getElementById("code-display").innerText = code;
                } else {
                    showMessage("Invalid code! Please try again.");
                    countdownAndClear();
                }
            } else {
                showMessage("Enter a 3 to 6-digit code first!");
            }
        }

        function countdownAndClear() {
            const display = document.getElementById("code-display");
            let timeLeft = 3;

            const countdownInterval = setInterval(() => {
                if (timeLeft > 0) {
                    display.innerText = `Resetting in ${timeLeft}...`;
                    timeLeft--;
                } else {
                    clearInterval(countdownInterval);
                    code = "";
                    display.innerText = code;
                }
            }, 1000);
        }

        function startCountdown(locker) {
            const button = document.getElementById(locker);
            const countdownElement = document.getElementById(`countdown_${locker.split(' ')[1]}`);
            let timeLeft = toggleBackTimer;

            countdownElement.innerText = timeLeft;

            const intervalId = setInterval(() => {
                timeLeft--;
                if (timeLeft <= 0) {
                    button.classList.remove("active");
                    countdownElement.innerText = "";
                    clearInterval(intervalId);
                } else {
                    countdownElement.innerText = timeLeft;
                }
            }, 1000);
        }

        function addLog(locker, user) {
            const logContainer = document.getElementById("logs");
            const newLog = document.createElement("li");
            newLog.innerText = `${user} activated ${locker}`;
            logContainer.insertBefore(newLog, logContainer.firstChild);
            if (logContainer.children.length > 10) {
                logContainer.removeChild(logContainer.lastChild);
            }
        }

        function showMessage(message) {
            const messageDiv = document.getElementById("message");
            messageDiv.innerText = message;
            setTimeout(() => { messageDiv.innerText = ""; }, 2000);
        }

        function showHelp() {
            document.getElementById("helpModal").style.display = "block";
        }

        function closeHelp() {
            document.getElementById("helpModal").style.display = "none";
        }

        function initializeButtonStates() {
            fetch('/get_locker_states')
                .then(response => response.json())
                .then(states => {
                    for (let locker in states) {
                        const button = document.getElementById(locker);
                        if (states[locker]) {
                            button.classList.add("active");
                            startCountdown(locker);
                        }
                    }
                });
        }

        window.onload = initializeButtonStates;
        </script>
    </body>
    </html>
    """
    return html

def log_data(code, locker, success):
    timestamp = time.localtime()
    formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        timestamp[0], timestamp[1], timestamp[2],
        timestamp[3], timestamp[4], timestamp[5]
    )
    log_entry = f"Timestamp={formatted_time},Code={code},Locker={locker},Success={success}\n"

    try:
        with open(log_file, 'a') as f:
            f.write(log_entry)
    except:
        print("Error! Could not save to log file")

def get_current_date():
    current_time = time.localtime()
    return f"{current_time[1]:02d}-{current_time[2]:02d}-{current_time[0]}"

def reset_locker(locker):
    lockers[locker].off()
    print(f"{locker} has been reset")

def handle_client(client_socket):
    try:
        request = b""
        while True:
            try:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                request += chunk
                if b"\r\n\r\n" in request:
                    break
            except OSError as e:
                if e.args[0] == 11:  # EAGAIN
                    continue
                else:
                    raise

        request = request.decode()
        if 'GET /locker?' in request:
            params = request.split(' ')[1].split('?')[1].split('&')
            locker = params[0].split('=')[1]
            locker = locker.replace('%20', ' ')  # URL decode the locker name
            code = params[1].split('=')[1]
            if code in valid_codes and 3 <= len(code) <= 6:
                if time.time() - last_authorized_changes[locker] > cooldown_period:
                    lockers[locker].on()
                    last_authorized_changes[locker] = time.time()
                    reset_times[locker] = time.time() + toggle_back_timers[locker]
                    log_data(code, locker, True)
                    add_log_entry(locker, f"Activated by {valid_codes[code]}")
                else:
                    log_data(code, locker, False)
            else:
                log_data(code, locker, False)
        elif 'GET /get_locker_states' in request:
            states = {locker: pin.value() for locker, pin in lockers.items()}
            response = json.dumps(states)
            send_response(client_socket, 'application/json', response)
            return

        # Send HTTP response
        response = web_page()
        send_response(client_socket, 'text/html', response)
    except Exception as e:
        print(f"Error handling client request: {e}")
    finally:
        client_socket.close()

def send_response(client_socket, content_type, content):
    response = f'HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nConnection: close\r\n\r\n'
    response = response.encode() + content.encode()
    while response:
        try:
            sent = client_socket.send(response)
            response = response[sent:]
        except OSError as e:
            if e.args[0] == 11:  # EAGAIN
                continue
            else:
                raise

def add_log_entry(locker, message):
    current_date = get_current_date()
    log_entry = f"{current_date}: {message}"
    locker_logs[locker].insert(0, log_entry)  # Add new log entry at the beginning
    if len(locker_logs[locker]) > 10:
        locker_logs[locker] = locker_logs[locker][:10]  # Keep only the last 10 entries

def start_server():
    setup_ap()
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(5)
    server_socket.setblocking(False)
    print('Listening on', addr)

    while True:
        try:
            client_socket, client_addr = server_socket.accept()
            print('Client connected from', client_addr)
            client_socket.setblocking(False)
            handle_client(client_socket)
        except OSError as e:
            if e.args[0] == 11:  # EAGAIN
                pass
            else:
                print(f"Error accepting client connection: {e}")

        # Check and reset lockers
        current_time = time.time()
        for locker, reset_time in reset_times.items():
            if reset_time > 0 and current_time >= reset_time:
                reset_locker(locker)
                reset_times[locker] = 0

        gc.collect()
        time.sleep(0.1)

# Start the server
if __name__ == '__main__':
    start_server()
