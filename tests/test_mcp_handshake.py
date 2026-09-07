"""MCP stdio handshake test for onshape-mcp-codex (readline-safe)."""
import json, asyncio, os, sys

async def read_json(stream):
    """Read one newline-delimited JSON message, handling large lines."""
    buf = b""
    while True:
        chunk = await stream.read(65536)
        if not chunk:
            return None
        buf += chunk
        try:
            idx = buf.index(b"\n")
            line = buf[:idx]
            return json.loads(line.decode("utf-8"))
        except ValueError:
            continue  # incomplete, keep reading
        except json.JSONDecodeError:
            # skip any stderr-ish noise line and continue
            buf = buf[buf.index(b"\n") + 1:] if b"\n" in buf else b""
            continue

async def main():
    env = dict(os.environ)
    env["PYTHONPATH"] = "."
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "onshape_mcp.server",
        env=env,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    init = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                       "clientInfo": {"name": "codex-test", "version": "0.1"}}}
    proc.stdin.write((json.dumps(init) + "\n").encode())
    await proc.stdin.drain()
    resp = await asyncio.wait_for(read_json(proc.stdout), timeout=30)
    si = resp.get("result", {}).get("serverInfo", {})
    instr = resp.get("result", {}).get("instructions", "")
    print("serverInfo:", si)
    print("instructions present:", bool(instr), f"({len(instr)} chars)")

    proc.stdin.write((json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n").encode())
    await proc.stdin.drain()
    await asyncio.sleep(0.5)

    lst = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    proc.stdin.write((json.dumps(lst) + "\n").encode())
    await proc.stdin.drain()
    resp = await asyncio.wait_for(read_json(proc.stdout), timeout=60)
    tools = resp.get("result", {}).get("tools", [])
    print(f"Tools listed: {len(tools)}")
    for t in tools[:6]:
        print(f"  - {t['name']}")
    print("  ...")
    proc.terminate()
    await proc.wait()

asyncio.run(main())
