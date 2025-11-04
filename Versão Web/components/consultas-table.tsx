"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight, CheckCircle2, XCircle } from "lucide-react"

interface Individuo {
  id: number
  nome: string
  idade: number
  regiao: string
  domicilio: string
  dispositivos: number
  internet: boolean
}

export function ConsultasTable() {
  const [data, setData] = useState<Individuo[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    setLoading(true)
    fetch(`/api/individuos?page=${page}&limit=10`)
      .then((res) => res.json())
      .then((result) => {
        const rows = Array.isArray(result?.data) ? result.data : []
        const total = result?.pagination?.totalPages ?? 1
        setData(rows)
        setTotalPages(total)
        setLoading(false)
      })
  }, [page])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Resultados</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-muted rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Resultados da Consulta</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Nome</TableHead>
                <TableHead>Idade</TableHead>
                <TableHead>Região</TableHead>
                <TableHead>Domicílio</TableHead>
                <TableHead>Dispositivos</TableHead>
                <TableHead>Internet</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((individuo) => (
                <TableRow key={individuo.id}>
                  <TableCell className="font-mono text-sm">{individuo.id}</TableCell>
                  <TableCell className="font-medium">{individuo.nome ?? `Indivíduo ${individuo.id}`}</TableCell>
                  <TableCell>{individuo.idade}</TableCell>
                  <TableCell>{individuo.regiao ?? "—"}</TableCell>
                  <TableCell className="font-mono text-sm">{individuo.domicilio ?? "—"}</TableCell>
                  <TableCell>{typeof individuo.dispositivos === "number" ? individuo.dispositivos : 0}</TableCell>
                  <TableCell>
                    {Boolean(individuo.internet) ? (
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                    ) : (
                      <XCircle className="h-4 w-4 text-red-500" />
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-muted-foreground">
            Página {page} de {totalPages}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              <ChevronLeft className="h-4 w-4" />
              Anterior
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              Próxima
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
