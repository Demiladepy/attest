import { NextRequest, NextResponse } from "next/server";
import { verifyAssetUrl } from "@/lib/verify-core";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  let body: { asset_url?: string; manifest_url?: string; expected_sha256?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ detail: "Invalid JSON" }, { status: 400 });
  }
  if (!body.asset_url) {
    return NextResponse.json({ detail: "asset_url is required" }, { status: 422 });
  }
  const result = await verifyAssetUrl(body.asset_url, body.manifest_url, body.expected_sha256);
  return NextResponse.json(result);
}
