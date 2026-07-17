import queue
import threading
import time

from network_utils import check_port, grab_banner, resolve_host

COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Proxy",
}


class PortScanner:
    def __init__(self, target, start_port=1, end_port=1024, threads=100, timeout=1.0, grab_banners=False):
        self.target = target
        self.start_port = start_port
        self.end_port = end_port
        self.threads = threads
        self.timeout = timeout
        self.grab_banners = grab_banners
        self.open_ports = []
        self.lock = threading.Lock()
        self.q = queue.Queue()

    def worker(self, ip):
        while not self.q.empty():
            try:
                port = self.q.get_nowait()
            except queue.Empty:
                return
            if check_port(ip, port, self.timeout):
                service = COMMON_PORTS.get(port, "unknown")
                banner = grab_banner(ip, port, self.timeout) if self.grab_banners else ""
                with self.lock:
                    self.open_ports.append((port, service, banner))
            self.q.task_done()

    def run(self):
        ip = resolve_host(self.target)
        if ip is None:
            return None

        for port in range(self.start_port, self.end_port + 1):
            self.q.put(port)

        start_time = time.time()
        thread_list = []
        for _ in range(min(self.threads, self.end_port - self.start_port + 1)):
            t = threading.Thread(target=self.worker, args=(ip,))
            t.daemon = True
            t.start()
            thread_list.append(t)

        for t in thread_list:
            t.join()

        elapsed = time.time() - start_time
        self.open_ports.sort(key=lambda x: x[0])
        return {
            "target": self.target,
            "ip": ip,
            "open_ports": self.open_ports,
            "elapsed": elapsed,
        }