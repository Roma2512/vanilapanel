import docker
import os
import socket
import select
import time
from threading import Thread

client = docker.from_env()
socket_connections = {}
logs = {}

def run_server(id: str):
    # Исправлена опечатка в client.containers.run()
    container = client.containers.run(
        "ubuntu",
        name=f"vanilapanel_{id}",
        working_dir="/server",
        volumes={os.path.abspath("servers/1"): {"bind": "/server", "mode": "rw"}},
        tty=True,
        stdin_open=True,
        detach=True,
        ports={'25565/tcp': 25565},
        mem_limit="1000M",
        cpu_quota=50000,
        command="/bin/bash"  # Запускаем bash
    )
    
    # Получаем сырой сокет от Docker
    sock = container.attach_socket(params={
        'stdin': 1,
        'stdout': 1,
        'stderr': 1,
        'stream': 1
    })
    
    # Конвертируем SocketIO в обычный сокет
    fd = sock.fileno()
    new_sock = socket.fromfd(fd, socket.AF_UNIX, socket.SOCK_STREAM)
    
    socket_connections[id] = {
        'socket': new_sock,
        'container': container,
        'buffer': b''
    }
    
    return container

def send_command(id: str, command: str):
    if id not in socket_connections:
        raise ValueError(f"No active connection for container {id}")
    
    sock = socket_connections[id]['socket']
    try:
        sock.sendall((command + "\n").encode('utf-8'))
    except (ConnectionResetError, BrokenPipeError, socket.error):
        print(f"Connection to container {id} lost")
        if id in socket_connections:
            socket_connections[id]['socket'].close()
            del socket_connections[id]

def stop_server(id: str):
    if id in socket_connections:
        socket_connections[id]['socket'].close()
        del socket_connections[id]
    
    try:
        container = client.containers.get(f"vanilapanel_{id}")
        container.stop()
        container.remove()
    except:
        pass

def kill_server(id: str):
    if id in socket_connections:
        socket_connections[id]['socket'].close()
        del socket_connections[id]
    
    try:
        container = client.containers.get(f"vanilapanel_{id}")
        container.kill()
        container.remove()
    except:
        pass

def is_running(id: str):
    try:
        container = client.containers.get(f"vanilapanel_{id}")
        return container.status == "running"
    except:
        return False