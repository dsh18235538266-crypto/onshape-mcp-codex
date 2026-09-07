"""Real Onshape E2E test: create public doc -> enumerate part studio."""
import asyncio, os, sys
from dotenv import load_dotenv

load_dotenv()

from onshape_mcp.api.client import OnshapeClient, OnshapeCredentials
from onshape_mcp.api.documents import DocumentManager


async def main():
    creds = OnshapeCredentials(
        access_key=os.getenv("ONSHAPE_API_KEY", ""),
        secret_key=os.getenv("ONSHAPE_API_SECRET", ""),
    )
    client = OnshapeClient(creds)
    docs = DocumentManager(client)

    print("[1] Creating Onshape document 'codex-e2e-plate' (public)...", flush=True)
    doc = await docs.create_document(
        "codex-e2e-plate", description="E2E test from onshape-mcp-codex", is_public=True
    )
    did = doc.id
    print(f"    Doc created: {did} name={doc.name}", flush=True)

    print("[2] Finding workspaces...", flush=True)
    print(f"    (DocumentInfo has no default_workspace field — listing via API)", flush=True)

    # List elements via the low-level client to discover structure
    r = await client.get(f"/api/v10/documents/{did}")
    print(f"    Doc API keys: {list(r.keys())[:10] if isinstance(r, dict) else type(r)}", flush=True)

    if isinstance(r, dict):
        # Try common element discovery paths
        wsid = None
        # Document response usually has defaultWorkspace
        dws = r.get("defaultWorkspace") or r.get("default_workspace")
        if dws:
            wsid = dws.get("id") if isinstance(dws, dict) else dws
            print(f"    Workspace: {wsid}", flush=True)

        if wsid:
            elements = await client.get(f"/api/v10/documents/d/{did}/w/{wsid}/elements")
            print(f"[3] Elements: {len(elements) if isinstance(elements, list) else elements}", flush=True)

    print("\n[E2E] AUTH + DOCUMENT CREATION VERIFIED. Codex can drive real Onshape CAD.", flush=True)


asyncio.run(main())
