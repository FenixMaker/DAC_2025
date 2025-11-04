"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { MapPin, Home, Users, Smartphone, Wifi, TrendingUp, TrendingDown } from "lucide-react"

interface Stats {
  regioes: number
  domicilios: number
  individuos: number
  dispositivos: number
  internet: number
  crescimento: {
    regioes: number
    domicilios: number
    individuos: number
    dispositivos: number
    internet: number
  }
}

export function StatsCards() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  
  const defaultStats: Stats = {
    regioes: 0,
    domicilios: 0,
    individuos: 0,
    dispositivos: 0,
    internet: 0,
    crescimento: {
      regioes: 0,
      domicilios: 0,
      individuos: 0,
      dispositivos: 0,
      internet: 0,
    },
  }

  const formatNumber = (n: unknown) => (typeof n === "number" ? n.toLocaleString("pt-BR") : "0")

  useEffect(() => {
    fetch("/api/estatisticas/resumo")
      .then((res) => (res.ok ? res.json() : Promise.reject(res)))
      .then((data) => {
        // Sanitizar e mesclar com valores padrão para evitar undefined
        const partial = (data || {}) as Partial<Stats>
        const merged: Stats = {
          ...defaultStats,
          ...partial,
          crescimento: {
            ...defaultStats.crescimento,
            ...(partial.crescimento || {}),
          },
        }
        setStats(merged)
        setLoading(false)
      })
      .catch(() => {
        setStats(defaultStats)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        {[...Array(5)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="h-4 w-20 bg-muted rounded" />
              <div className="h-4 w-4 bg-muted rounded" />
            </CardHeader>
            <CardContent>
              <div className="h-8 w-24 bg-muted rounded mb-1" />
              <div className="h-3 w-16 bg-muted rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (!stats) return null

  const cards = [
    {
      title: "Regiões",
      value: formatNumber(stats.regioes),
      change: typeof stats.crescimento.regioes === "number" ? stats.crescimento.regioes : 0,
      icon: MapPin,
      color: "text-chart-1",
      bgColor: "bg-chart-1/10",
    },
    {
      title: "Domicílios",
      value: formatNumber(stats.domicilios),
      change: typeof stats.crescimento.domicilios === "number" ? stats.crescimento.domicilios : 0,
      icon: Home,
      color: "text-chart-2",
      bgColor: "bg-chart-2/10",
    },
    {
      title: "Indivíduos",
      value: formatNumber(stats.individuos),
      change: typeof stats.crescimento.individuos === "number" ? stats.crescimento.individuos : 0,
      icon: Users,
      color: "text-chart-3",
      bgColor: "bg-chart-3/10",
    },
    {
      title: "Dispositivos",
      value: formatNumber(stats.dispositivos),
      change: typeof stats.crescimento.dispositivos === "number" ? stats.crescimento.dispositivos : 0,
      icon: Smartphone,
      color: "text-chart-4",
      bgColor: "bg-chart-4/10",
    },
    {
      title: "Internet",
      value: formatNumber(stats.internet),
      change: typeof stats.crescimento.internet === "number" ? stats.crescimento.internet : 0,
      icon: Wifi,
      color: "text-chart-5",
      bgColor: "bg-chart-5/10",
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
      {cards.map((card, index) => {
        const Icon = card.icon
        const isPositive = card.change > 0
        const TrendIcon = isPositive ? TrendingUp : TrendingDown

        return (
          <Card
            key={card.title}
            className="group relative overflow-hidden transition-all hover:shadow-lg hover:shadow-primary/5 hover:-translate-y-1 animate-slide-up border-border/50"
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity" />

            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">{card.title}</CardTitle>
              <div
                className={`flex h-10 w-10 items-center justify-center rounded-lg ${card.bgColor} transition-transform group-hover:scale-110`}
              >
                <Icon className={`h-5 w-5 ${card.color}`} />
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="text-3xl font-bold tracking-tight">{card.value}</div>
              {card.change !== 0 && (
                <div className="flex items-center gap-1.5">
                  <div
                    className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                      isPositive
                        ? "bg-green-500/10 text-green-600 dark:text-green-400"
                        : "bg-red-500/10 text-red-600 dark:text-red-400"
                    }`}
                  >
                    <TrendIcon className="h-3 w-3" />
                    <span>{Math.abs(card.change)}%</span>
                  </div>
                  <span className="text-xs text-muted-foreground">vs mês anterior</span>
                </div>
              )}
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
