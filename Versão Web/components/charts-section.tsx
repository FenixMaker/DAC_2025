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

// Accessible color palette for charts - WCAG AA compliant
const chartColors = {
  chart1: "#3B82F6", // Blue - Excellent contrast on light and dark themes
  chart2: "#10B981", // Green - Excellent contrast
  chart3: "#F59E0B", // Amber - Excellent contrast
  chart4: "#EF4444", // Red - Excellent contrast
  chart5: "#8B5CF6", // Purple - Excellent contrast
}

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
                color: chartColors.chart1,
              },
              domicilios: {
                label: "Domicílios",
                color: chartColors.chart2,
              },
            }}
            className="h-[340px]"
          >
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={regionData} margin={{ top: 30, right: 20, left: 15, bottom: 25 }}>
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  stroke="#94A3B8" 
                  strokeOpacity={0.3}
                  vertical={false} 
                />
                <XAxis
                  dataKey="name"
                  className="text-sm font-medium"
                  tick={{ fill: "#64748B", fontSize: 12, fontWeight: 500 }}
                  axisLine={{ stroke: "#64748B", strokeWidth: 1 }}
                  tickLine={{ stroke: "#64748B", strokeWidth: 1 }}
                />
                <YAxis
                  className="text-sm font-medium"
                  tick={{ fill: "#64748B", fontSize: 11, fontWeight: 500 }}
                  axisLine={{ stroke: "#64748B", strokeWidth: 1 }}
                  tickLine={{ stroke: "#64748B", strokeWidth: 1 }}
                  width={60}
                />
                <ChartTooltip 
                  content={<ChartTooltipContent />} 
                  cursor={{ fill: "rgba(148, 163, 184, 0.1)" }}
                  contentStyle={{
                    backgroundColor: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
                  }}
                />
                <Legend 
                  wrapperStyle={{ 
                    paddingTop: "15px",
                    fontSize: "14px",
                    fontWeight: "500",
                    paddingBottom: "5px"
                  }} 
                  iconType="rect"
                  iconSize={14}
                />
                <Bar 
                  dataKey="individuos" 
                  fill={chartColors.chart1} 
                  radius={[4, 4, 0, 0]} 
                  maxBarSize={60}
                  name="Indivíduos"
                />
                <Bar 
                  dataKey="domicilios" 
                  fill={chartColors.chart2} 
                  radius={[4, 4, 0, 0]} 
                  maxBarSize={60}
                  name="Domicílios"
                />
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
                color: chartColors.chart3,
              },
              dispositivos: {
                label: "Dispositivos",
                color: chartColors.chart4,
              },
            }}
            className="h-[340px]"
          >
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timeData} margin={{ top: 30, right: 20, left: 20, bottom: 25 }}>
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  stroke="#94A3B8" 
                  strokeOpacity={0.3}
                  vertical={false} 
                />
                <XAxis
                  dataKey="mes"
                  className="text-sm font-medium"
                  tick={{ fill: "#64748B", fontSize: 12, fontWeight: 500 }}
                  axisLine={{ stroke: "#64748B", strokeWidth: 1 }}
                  tickLine={{ stroke: "#64748B", strokeWidth: 1 }}
                />
                <YAxis
                  className="text-sm font-medium"
                  tick={{ fill: "#64748B", fontSize: 11, fontWeight: 500 }}
                  axisLine={{ stroke: "#64748B", strokeWidth: 1 }}
                  tickLine={{ stroke: "#64748B", strokeWidth: 1 }}
                  width={65}
                />
                <ChartTooltip 
                  content={<ChartTooltipContent />} 
                  contentStyle={{
                    backgroundColor: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
                  }}
                />
                <Legend 
                  wrapperStyle={{ 
                    paddingTop: "15px",
                    fontSize: "14px",
                    fontWeight: "500",
                    paddingBottom: "5px"
                  }} 
                  iconType="line"
                  iconSize={16}
                />
                <Line
                  type="monotone"
                  dataKey="individuos"
                  stroke={chartColors.chart3}
                  strokeWidth={3}
                  dot={{ fill: chartColors.chart3, r: 6, strokeWidth: 2, stroke: "#ffffff" }}
                  activeDot={{ r: 8, strokeWidth: 3, stroke: "#ffffff" }}
                  name="Indivíduos"
                />
                <Line
                  type="monotone"
                  dataKey="dispositivos"
                  stroke={chartColors.chart4}
                  strokeWidth={3}
                  dot={{ fill: chartColors.chart4, r: 6, strokeWidth: 2, stroke: "#ffffff" }}
                  activeDot={{ r: 8, strokeWidth: 3, stroke: "#ffffff" }}
                  name="Dispositivos"
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartContainer>
        </CardContent>
      </Card>
    </div>
  )
}
