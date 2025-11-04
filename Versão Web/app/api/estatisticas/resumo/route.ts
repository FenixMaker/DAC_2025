import { NextResponse } from "next/server"

export async function GET() {
  const baseUrl = process.env.NEXT_PUBLIC_DAC_API_URL || "http://localhost:8000"
  try {
    const res = await fetch(`${baseUrl}/api/estatisticas/resumo`, { cache: "no-store" })
    const data = await res.json()
    return NextResponse.json(data)
  } catch (e) {
    return NextResponse.json({ message: "Backend indisponível" }, { status: 503 })
  }
}
