"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, Line, LineChart, ResponsiveContainer, XAxis, YAxis, Legend, CartesianGrid } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Download, TrendingUp } from "lucide-react"
import { Button } from "@/components/ui/button"

const regionData = [
  { name: "Norte", individuos: 45234, domicilios: 15678 },
  { name: "Nordeste", individuos: 52341, domicilios: 18234 },
  { name: "Centro-Oeste", individuos: 38567, domicilios: 13456 },
  { name: "Sudeste", individuos: 48923, domicilios: 16789 },
  { name: "Sul", individuos: 28782, domicilios: 8301 },
]

const timeData = [
  { mes: "Jan", individuos: 198234, dispositivos: 142345 },
  { mes: "Fev", individuos: 201456, dispositivos: 145678 },
  { mes: "Mar", individuos: 205789, dispositivos: 149234 },
  { mes: "Abr", individuos: 208123, dispositivos: 152456 },
  { mes: "Mai", individuos: 210456, dispositivos: 154789 },
  { mes: "Jun", individuos: 213847, dispositivos: 156234 },
]

export function ChartsSection() {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card
        className="group transition-all hover:shadow-lg hover:shadow-primary/5 border-border/50 animate-slide-up"
        style={{ animationDelay: "0.5s" }}
      >
        <CardHeader className="space-y-3">
          <div className="flex items-start justify-between">
            <div className="space-y-1.5">
              <CardTitle className="text-xl">Distribuição por Região</CardTitle>
              <CardDescription className="text-sm leading-relaxed">
                Análise comparativa de indivíduos e domicílios por região geográfica
              </CardDescription>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <Download className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <TrendingUp className="h-3.5 w-3.5 text-green-500" />
            <span>Nordeste lidera com 52.3k indivíduos</span>
          </div>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              individuos: {
                label: "Indivíduos",
                color: "hsl(var(--chart-1))",
              },
              domicilios: {
                label: "Domicílios",
                color: "hsl(var(--chart-2))",
              },
            }}
            className="h-[320px]"
          >
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={regionData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted/30" vertical={false} />
                <XAxis
                  dataKey="name"
                  className="text-xs"
                  tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  className="text-xs"
                  tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />
                <ChartTooltip content={<ChartTooltipContent />} cursor={{ fill: "hsl(var(--muted))", opacity: 0.1 }} />
                <Legend wrapperStyle={{ paddingTop: "20px" }} iconType="circle" />
                <Bar dataKey="individuos" fill="hsl(var(--chart-1))" radius={[8, 8, 0, 0]} maxBarSize={60} />
                <Bar dataKey="domicilios" fill="hsl(var(--chart-2))" radius={[8, 8, 0, 0]} maxBarSize={60} />
              </BarChart>
            </ResponsiveContainer>
          </ChartContainer>
        </CardContent>
      </Card>

      <Card
        className="group transition-all hover:shadow-lg hover:shadow-primary/5 border-border/50 animate-slide-up"
        style={{ animationDelay: "0.6s" }}
      >
        <CardHeader className="space-y-3">
          <div className="flex items-start justify-between">
            <div className="space-y-1.5">
              <CardTitle className="text-xl">Evolução Temporal</CardTitle>
              <CardDescription className="text-sm leading-relaxed">
                Crescimento progressivo de indivíduos e dispositivos ao longo do tempo
              </CardDescription>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <Download className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <TrendingUp className="h-3.5 w-3.5 text-green-500" />
            <span>Crescimento de 7.8% nos últimos 6 meses</span>
          </div>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              individuos: {
                label: "Indivíduos",
                color: "hsl(var(--chart-3))",
              },
              dispositivos: {
                label: "Dispositivos",
                color: "hsl(var(--chart-4))",
              },
            }}
            className="h-[320px]"
          >
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted/30" vertical={false} />
                <XAxis
                  dataKey="mes"
                  className="text-xs"
                  tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  className="text-xs"
                  tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Legend wrapperStyle={{ paddingTop: "20px" }} iconType="circle" />
                <Line
                  type="monotone"
                  dataKey="individuos"
                  stroke="hsl(var(--chart-3))"
                  strokeWidth={3}
                  dot={{ fill: "hsl(var(--chart-3))", r: 5, strokeWidth: 2, stroke: "hsl(var(--card))" }}
                  activeDot={{ r: 7, strokeWidth: 2 }}
                />
                <Line
                  type="monotone"
                  dataKey="dispositivos"
                  stroke="hsl(var(--chart-4))"
                  strokeWidth={3}
                  dot={{ fill: "hsl(var(--chart-4))", r: 5, strokeWidth: 2, stroke: "hsl(var(--card))" }}
                  activeDot={{ r: 7, strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartContainer>
        </CardContent>
      </Card>
    </div>
  )
}
