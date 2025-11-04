import { NextResponse } from 'next/server'
import { query } from '@/lib/db'

async function getDbStatusDirect() {
  // Executa diversas consultas para coletar status do banco
  const [{ rows: [basic] }, { rows: [tables] }, { rows: [indexes] }, { rows: [conns] }, { rows: [sizes] }, { rows: topTables }] = await Promise.all([
    query<{ version: string, user: string, database: string, server_time: string, uptime: string }>(
      `select version(), current_user as user, current_database() as database, now() as server_time, 
              to_char(date_trunc('second', now() - pg_postmaster_start_time()), 'DD "d" HH24:MI:SS') as uptime`
    ),
    query<{ count: number }>(
      `select count(*)::int from information_schema.tables where table_schema='public' and table_type='BASE TABLE'`
    ),
    query<{ count: number }>(
      `select count(*)::int from pg_indexes where schemaname='public'`
    ),
    query<{ count: number }>(
      `select count(*)::int from pg_stat_activity where datname = current_database()`
    ),
    query<{ db_bytes: string, tables_bytes: string }>(
      `select pg_database_size(current_database())::bigint as db_bytes,
              coalesce(sum(pg_total_relation_size(format('%I.%I', n.nspname, c.relname))),0)::bigint as tables_bytes
       from pg_class c
       join pg_namespace n on n.oid = c.relnamespace
       where n.nspname = 'public' and c.relkind='r'`
    ),
    query<{ name: string, total_bytes: string }>(
      `select c.relname as name, pg_total_relation_size(c.oid)::bigint as total_bytes
       from pg_class c
       join pg_namespace n on n.oid = c.relnamespace
       where n.nspname='public' and c.relkind='r'
       order by pg_total_relation_size(c.oid) desc
       limit 5`
    ),
  ])

  return {
    connected: true,
    version: basic.version,
    user: basic.user,
    database: basic.database,
    server_time: basic.server_time,
    uptime: basic.uptime,
    totals: {
      tables: tables.count,
      indexes: indexes.count,
      connections: conns.count,
      db_bytes: Number(sizes.db_bytes),
      tables_bytes: Number(sizes.tables_bytes),
    },
    top_tables: topTables.map((t) => ({ name: t.name, total_bytes: Number(t.total_bytes) })),
  }
}

export async function GET() {
  const baseUrl = process.env.NEXT_PUBLIC_DAC_API_URL || 'http://localhost:8000'
  // Tenta consultar o backend Python se tiver um endpoint compatível; caso falhe, usa acesso direto ao Postgres
  try {
    const res = await fetch(`${baseUrl}/api/db/status`, { cache: 'no-store' })
    if (res.ok) {
      const data = await res.json()
      return NextResponse.json(data)
    }
  } catch {}

  try {
    const data = await getDbStatusDirect()
    return NextResponse.json(data)
  } catch (e: any) {
    return NextResponse.json({ connected: false, error: e?.message || 'Falha ao obter status do banco' }, { status: 500 })
  }
}
