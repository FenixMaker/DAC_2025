import { NextResponse } from "next/server"

export async function GET() {
  const baseUrl = process.env.NEXT_PUBLIC_DAC_API_URL || "http://localhost:8000"
  try {
    const res = await fetch(`${baseUrl}/api/health`, { cache: "no-store" })
    const data = await res.json()
    return NextResponse.json(data)
  } catch (e) {
    return NextResponse.json({ status: "error", message: "Backend indisponível" }, { status: 503 })
  }
}
