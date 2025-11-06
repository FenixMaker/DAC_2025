"use client"

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Activity, Database, Server, Users, Table as TableIcon, Layers, HardDrive, Clock } from 'lucide-react'

interface DbStatus {
  connected: boolean
  version?: string
  user?: string
  database?: string
  server_time?: string
  uptime?: string
  totals?: {
    tables: number
    indexes: number
    connections: number
    db_bytes: number
    tables_bytes: number
  }
  top_tables?: { name: string; total_bytes: number }[]
  error?: string
}

function formatBytes(n?: number) {
  if (!n && n !== 0) return '—'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0
  let v = n
  while (v >= 1024 && i < units.length - 1) {
    v /= 1024
    i++
  }
  return `${v.toFixed(1)} ${units[i]}`
}

export function DbStatusDashboard() {
  const [status, setStatus] = useState<DbStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/db/status', { cache: 'no-store' })
      .then((r) => (r.ok ? r.json() : Promise.reject(r)))
      .then((data: DbStatus) => setStatus(data))
      .catch(() => setStatus({ connected: false, error: 'Não foi possível obter status' }))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 w-24 bg-muted rounded" />
            </CardHeader>
            <CardContent>
              <div className="h-8 w-32 bg-muted rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (!status) return null
  const ok = status.connected

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Badge variant={ok ? 'default' : 'destructive'} className="gap-1">
          <Activity className={`h-3.5 w-3.5 ${ok ? 'text-green-500' : 'text-red-500'}`} />
          {ok ? 'Conectado' : 'Offline'}
        </Badge>
        {status.version && <span className="text-sm text-muted-foreground">{status.version}</span>}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground flex items-center gap-2"><Database className="h-4 w-4"/>Banco</CardTitle></CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{status.database || '—'}</div>
            <div className="text-sm text-muted-foreground">Usuário: {status.user || '—'}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground flex items-center gap-2"><Server className="h-4 w-4"/>Servidor</CardTitle></CardHeader>
          <CardContent>
            {(() => {
              const d = status.server_time ? new Date(status.server_time) : null
              const valid = d && !isNaN(d.getTime())
              const text = valid ? d!.toLocaleString('pt-BR') : '—'
              return (
                <div className="text-2xl font-bold">{text}</div>
              )
            })()}
            <div className="text-sm text-muted-foreground flex items-center gap-2"><Clock className="h-4 w-4"/>Uptime: {status.uptime || '—'}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground flex items-center gap-2"><Users className="h-4 w-4"/>Conexões</CardTitle></CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{status.totals?.connections ?? '—'}</div>
            <div className="text-sm text-muted-foreground">Ativas no banco atual</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground flex items-center gap-2"><Layers className="h-4 w-4"/>Tabelas/Índices</CardTitle></CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{status.totals ? `${status.totals.tables} / ${status.totals.indexes}` : '—'}</div>
            <div className="text-sm text-muted-foreground">Público</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground flex items-center gap-2"><HardDrive className="h-4 w-4"/>Tamanho</CardTitle></CardHeader>
          <CardContent className="space-y-1">
            <div className="text-lg">Banco: <b>{formatBytes(status.totals?.db_bytes)}</b></div>
            <div className="text-sm text-muted-foreground">Tabelas (soma): {formatBytes(status.totals?.tables_bytes)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground flex items-center gap-2"><TableIcon className="h-4 w-4"/>Maiores tabelas</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-2">
              {(status.top_tables || []).map((t) => (
                <div key={t.name} className="flex items-center justify-between gap-4">
                  <span className="truncate max-w-[60%]" title={t.name}>{t.name}</span>
                  <span className="text-sm text-muted-foreground">{formatBytes(t.total_bytes)}</span>
                </div>
              ))}
              {(!status.top_tables || status.top_tables.length === 0) && (
                <div className="text-sm text-muted-foreground">Sem dados</div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {!ok && status.error && (
        <div className="text-sm text-destructive">{status.error}</div>
      )}
    </div>
  )
}
