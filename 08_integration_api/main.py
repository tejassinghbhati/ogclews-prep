import asyncio
import sys
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="OG-CLEWS Integration API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/convergence")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '04_convergence_prototype'))
    process = None
    
    try:
        # Execute the python script dynamically
        process = await asyncio.create_subprocess_exec(
            sys.executable, "run_convergence.py",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=script_dir
        )
        
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            
            decoded_line = line.decode('utf-8').strip()
            if decoded_line:
                await websocket.send_text(decoded_line)
            
        await process.wait()
        await websocket.send_text("[SYSTEM] Convergence loop finished. Disconnecting.")
    except WebSocketDisconnect:
        print("Client disconnected.")
        if process and process.returncode is None:
            process.terminate()
    except Exception as e:
        await websocket.send_text(f"[ERROR] {str(e)}")
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
