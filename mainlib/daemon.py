import os
import subprocess
import psutil
import resource

processes = {"1": {}}
containers = {"1": {"running": False, "console": ""}}
#with open("servers.json", 'r') as f:
#    servers = f.read()
servers = {"1": {"name": "test", "egg": "python", "port": 25565, "mem": 4096, "cpu": 400, "cores": [0,1,2,3]}}

def start_process(id: str, command: str):
    print(id, command)
    #try:
    if 2 > 1:
        processes[id] = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            shell=True,
            cwd=f"servers/{id}/",
        )
        return {"code": True, "message": f"{id} - {command}"}
    #except Exception as e:
    #    return {"code": False, "message": "Ошибка запуска процесса"}


def set_limits(id: str):
    server = servers["id"]
    try:
        if server["mem"] is not None and hasattr(resource, 'RLIMIT_RSS'):
            ram_bytes = int(server["mem"] * 1024 * 1024)
            resource.setrlimit(resource.RLIMIT_RSS, (ram_bytes, ram_bytes))

        # Привязка к ядрам CPU
        if server["cores"] is not None and hasattr(psutil.Process(), 'cpu_affinity'):
            try:
                cores = min(server["cores"], os.cpu_count() or 1)
                psutil.Process().cpu_affinity(list(range(cores)))
            except Exception as e:
                print(f"Ошибка установки CPU affinity: {e}")

    except Exception as e:
        print(f"Ошибка установки лимитов ресурсов: {e}")

def send_command(id: str, command: str) -> bool:
    if id not in processes:
        print(f"Процесс {id} не найден!")
        return False

    try:
        proc = processes[id]
        proc.stdin.write(command + "\n")
        proc.stdin.flush()
        return True
    except Exception as e:
        print(f"Ошибка отправки команды в процесс {id}: {e}")
        return False

def stop_process(id: str) -> bool:
    if id not in processes:
        print(f"Процесс {id} не найден!")
        return False

    try:
        proc = processes[id]
        proc.stdin.close()  # Закрываем stdin, чтобы процесс мог завершиться

        # Читаем вывод в реальном времени (если процесс завис, можно добавить timeout)
        stdout, stderr = proc.communicate(timeout=10)

        print(f"[Процесс {id}] Вывод:")
        print(stdout.strip())
        if stderr.strip():
            print(f"[Процесс {id}] Ошибки:")
            print(stderr.strip())

        del processes[id]  # Удаляем процесс из словаря
        return True
    except subprocess.TimeoutExpired:
        print(f"Процесс {id} не завершился вовремя, принудительно убиваю...")
        proc.kill()
        return False
    except Exception as e:
        print(f"Ошибка остановки процесса {id}: {e}")
        return False

def is_running(id: str):
    try:
        return processes[id].poll() == None
    except:
        return False