import paramiko,json

# This will get the server's information like CPU, Memory .etc.


def log_in(ip, port, username, password, cmd):
    tmp = []
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(ip, port, username, password)
    (stdin, stdout, stderr) = s.exec_command(cmd)
    obtain = stdout.readlines()[0].strip().encode("utf-8")
    s.close()
    return obtain


def server_info(ip, port, username, password):
    get_mem = "free -m | grep '^Mem' | awk '{print $2}'"
    get_cpu = "cat /proc/cpuinfo  | grep pro | wc -l"
    get_ip = "hostname -I"

    cpu = log_in(ip, port, username, password, get_cpu)
    mem = log_in(ip, port, username, password, get_mem)
    ip = log_in(ip, port, username, password, get_ip)

    dynamic = {"cpu": cpu, "mem": mem, "ip": ip}

    return json.dumps(dynamic)




if __name__ == '__main__':
    ip = "10.1.96.239"
    port = 22
    username = "root"
    password = "lambert"
    server_info(ip, port, username, password)