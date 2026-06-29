const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Asset = {
  id: string;
  title: string;
  brief: string;
  status: string;
  run_id: string | null;
  parent_run_id: string | null;
  asset_url: string | null;
  manifest_url: string | null;
  sha256: string | null;
  created_at: string;
};

export type VerificationCheck = {
  id: string;
  label: string;
  status: "pass" | "fail" | "warn" | "skip";
  detail: string;
};

export type VerificationResult = {
  asset_url: string;
  overall: "pass" | "fail" | "warn";
  checks: VerificationCheck[];
  lineage: Array<{
    run_id: string;
    parent_run_id: string | null;
    status: string;
    created_at: string;
  }>;
};

export async function fetchAssets(): Promise<Asset[]> {
  const res = await fetch(`${API_BASE}/api/assets`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load assets");
  return res.json();
}

export async function generateAsset(brief: string, title?: string): Promise<Asset> {
  const res = await fetch(`${API_BASE}/api/assets/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ brief, title: title ?? "New generation" }),
  });
  if (!res.ok) throw new Error("Generation failed");
  return res.json();
}

export async function verifyAsset(assetUrl: string, manifestUrl?: string): Promise<VerificationResult> {
  const res = await fetch(`${API_BASE}/api/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ asset_url: assetUrl, manifest_url: manifestUrl }),
  });
  if (!res.ok) throw new Error("Verification failed");
  return res.json();
}

export async function fetchAuditLog(): Promise<
  Array<{
    id: string;
    event_type: string;
    detail: string;
    created_at: string;
    b2_object_key: string | null;
  }>
> {
  const res = await fetch(`${API_BASE}/api/audit`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load audit log");
  return res.json();
}

export function streamGeneration(
  brief: string,
  title: string,
  onEvent: (event: Record<string, unknown>) => void,
): () => void {
  const controller = new AbortController();
  const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  (async () => {
    const res = await fetch(`${API}/api/assets/generate/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ brief, title }),
      signal: controller.signal,
    });
    if (!res.ok || !res.body) return;

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            onEvent(JSON.parse(line.slice(6)));
          } catch {
            /* skip malformed */
          }
        }
      }
    }
  })();

  return () => controller.abort();
}
