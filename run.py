import socket, subprocess, sys
from pathlib import Path

root=Path(__file__).parent

def free_port(start=8501,end=8599):
    for p in range(start,end+1):
        with socket.socket() as s:
            try: s.bind(('127.0.0.1',p)); return p
            except OSError: pass
    raise RuntimeError('No free port in 8501-8599')

port=free_port()
print(f'Starting FisherGuard on http://localhost:{port}')
subprocess.run([sys.executable,'-m','streamlit','run','app.py','--server.port',str(port)],cwd=root,check=False)
