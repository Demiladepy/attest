import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Live deploy hosts the public verifier only. Generation/console runs locally
// (the private signing key never touches a public host), so no assets here.
export async function GET() {
  return NextResponse.json([]);
}
