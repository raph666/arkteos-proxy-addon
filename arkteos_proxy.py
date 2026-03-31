#!/usr/bin/env python3
# Proxy TCP pour PAC Arkteos REG3
# Permet les connexions simultanées de Node-RED et de l'app mobile Arkteos
# Usage : arkteos_proxy.py <pac_host> <pac_port> <proxy_port>

import socket
import threading
import sys
import time
import logging

# Configuration depuis les arguments (injectés par run.sh depuis les options HA)
PAC_HOST  = sys.argv[1] if len(sys.argv) > 1 else "192.168.X.X"
PAC_PORT  = int(sys.argv[2]) if len(sys.argv) > 2 else 9641
PROXY_PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 9641

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

stop_event = threading.Event()
clients = []
clients_lock = threading.Lock()

def log(msg):
    logger.info(msg)

def connect_to_pac():
    while not stop_event.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect((PAC_HOST, PAC_PORT))
            log(f"Connecté à la PAC {PAC_HOST}:{PAC_PORT}")
            return s
        except Exception as e:
            log(f"Échec connexion PAC : {e}. Nouvelle tentative dans 10s...")
            time.sleep(10)
    return None

def pac_reader(pac_socket):
    log("Démarrage thread lecture PAC")
    try:
        while not stop_event.is_set():
            try:
                data = pac_socket.recv(4096)
            except Exception as e:
                log(f"Erreur lecture PAC : {e}")
                break
            if not data:
                log("PAC a fermé la connexion")
                break

            dead_clients = []
            with clients_lock:
                for c in clients:
                    try:
                        c.sendall(data)
                    except Exception:
                        dead_clients.append(c)

            if dead_clients:
                with clients_lock:
                    for c in dead_clients:
                        try:
                            c.close()
                        except Exception:
                            pass
                        if c in clients:
                            clients.remove(c)
                        log("Client déconnecté nettoyé")
    finally:
        log("Arrêt thread lecture PAC")
        pac_socket.close()

def pac_keepalive(pac_socket):
    log("Démarrage thread keepalive PAC")
    while not stop_event.is_set():
        time.sleep(300)
        try:
            pac_socket.sendall(b'\x00')
            log("Keepalive envoyé à la PAC")
        except Exception as e:
            log(f"Erreur keepalive PAC : {e}")
            break
    log("Arrêt thread keepalive PAC")

def handle_client(client_socket, client_addr, pac_socket):
    log(f"Nouveau client : {client_addr}")
    with clients_lock:
        clients.append(client_socket)
    try:
        while not stop_event.is_set():
            try:
                data = client_socket.recv(1024)
            except Exception:
                break
            if not data:
                break
            try:
                pac_socket.sendall(data)
            except Exception as e:
                log(f"Erreur envoi PAC depuis {client_addr} : {e}")
                break
    finally:
        with clients_lock:
            if client_socket in clients:
                clients.remove(client_socket)
        try:
            client_socket.close()
        except Exception:
            pass
        log(f"Client déconnecté : {client_addr}")

def start_proxy():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', PROXY_PORT))
    server_socket.listen(5)
    log(f"Proxy en écoute sur 0.0.0.0:{PROXY_PORT}")

    pac_socket = connect_to_pac()
    if pac_socket is None:
        log("Impossible de se connecter à la PAC. Arrêt.")
        return

    reader_thread = threading.Thread(target=pac_reader, args=(pac_socket,), daemon=True)
    reader_thread.start()

    keepalive_thread = threading.Thread(target=pac_keepalive, args=(pac_socket,), daemon=True)
    keepalive_thread.start()

    try:
        while not stop_event.is_set():
            server_socket.settimeout(1)
            try:
                client_socket, addr = server_socket.accept()
                t = threading.Thread(target=handle_client, args=(client_socket, addr, pac_socket), daemon=True)
                t.start()
            except socket.timeout:
                pass

            # Reconnexion si la PAC s'est déconnectée
            if not reader_thread.is_alive():
                log("Thread lecture PAC mort, reconnexion...")
                with clients_lock:
                    for c in clients:
                        try:
                            c.close()
                        except Exception:
                            pass
                    clients.clear()
                pac_socket = connect_to_pac()
                if pac_socket is None:
                    break
                reader_thread = threading.Thread(target=pac_reader, args=(pac_socket,), daemon=True)
                reader_thread.start()
                keepalive_thread = threading.Thread(target=pac_keepalive, args=(pac_socket,), daemon=True)
                keepalive_thread.start()
    except Exception as e:
        log(f"Erreur serveur proxy : {e}")
    finally:
        stop_event.set()
        server_socket.close()
        try:
            pac_socket.close()
        except Exception:
            pass
        log("Proxy arrêté.")

if __name__ == "__main__":
    try:
        start_proxy()
    except KeyboardInterrupt:
        log("Arrêt demandé")
        stop_event.set()
        sys.exit(0)
