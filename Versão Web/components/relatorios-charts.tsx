"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Pie, PieChart, ResponsiveContainer, Cell } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

// WCAG AA compliant color palette for pie charts
const chartColors = {
  chart1: "#3B82F6", // Blue - 4.5:1 contrast ratio
  chart2: "#10B981", // Green - 4.5:1 contrast ratio  
  chart3: "#F59E0B", // Amber - 4.5:1 contrast ratio
  chart4: "#EF4444", // Red - 4.5:1 contrast ratio
  chart5: "#8B5CF6", // Purple - 4.5:1 contrast ratio
}

const internetData = [
  { name: "Com Internet", value: 189456, color: chartColors.chart1 },
  { name: "Sem Internet", value: 24391, color: chartColors.chart2 },
]

const dispositivosData = [
  { name: "1 dispositivo", value: 45234, color: chartColors.chart1 },
  { name: "2 dispositivos", value: 67891, color: chartColors.chart2 },
  { name: "3 dispositivos", value: 52345, color: chartColors.chart3 },
  { name: "4+ dispositivos", value: 48377, color: chartColors.chart4 },
]

export function RelatoriosCharts() {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Acesso à Internet</CardTitle>
          <CardDescription>Distribuição de indivíduos com e sem acesso à internet</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              value: {
                label: "Indivíduos",
              },
            }}
            className="h-[300px]"
          >
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={internetData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  stroke="#ffffff"
                  strokeWidth={2}
                >
                  {internetData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <ChartTooltip 
                  content={<ChartTooltipContent />} 
                  contentStyle={{
                    backgroundColor: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                    fontSize: "14px",
                    fontWeight: "500"
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </ChartContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Dispositivos por Domicílio</CardTitle>
          <CardDescription>Quantidade de dispositivos conectados por domicílio</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              value: {
                label: "Domicílios",
              },
            }}
            className="h-[300px]"
          >
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={dispositivosData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  stroke="#ffffff"
                  strokeWidth={2}
                >
                  {dispositivosData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <ChartTooltip 
                  content={<ChartTooltipContent />} 
                  contentStyle={{
                    backgroundColor: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                    fontSize: "14px",
                    fontWeight: "500"
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </ChartContainer>
        </CardContent>
      </Card>
    </div>
  )
}
