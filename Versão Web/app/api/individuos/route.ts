import { NextResponse } from "next/server"

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const page = Number.parseInt(searchParams.get("page") || "1")
  const limit = Number.parseInt(searchParams.get("limit") || "10")
  const regiaoId = searchParams.get("regiao_id")
  const idade = searchParams.get("idade")
  const genero = searchParams.get("genero")

  const baseUrl = process.env.NEXT_PUBLIC_DAC_API_URL || "http://localhost:8000"
  const url = new URL(`${baseUrl}/api/individuos`)
  url.searchParams.set("page", String(page))
  url.searchParams.set("limit", String(limit))
  if (regiaoId) url.searchParams.set("regiao_id", regiaoId)
  if (idade) url.searchParams.set("idade", idade)
  if (genero) url.searchParams.set("genero", genero)

  try {
    const res = await fetch(url, { cache: "no-store" })
    const data = await res.json()
    return NextResponse.json(data)
  } catch (e) {
    return NextResponse.json({ message: "Backend indisponível" }, { status: 503 })
  }
}
