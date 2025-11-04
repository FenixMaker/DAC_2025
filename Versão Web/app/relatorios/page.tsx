import { DashboardHeader } from "@/components/dashboard-header"
import { RelatoriosCharts } from "@/components/relatorios-charts"
import { RelatoriosInsights } from "@/components/relatorios-insights"

export default function RelatoriosPage() {
  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />
      <main className="container mx-auto px-4 py-8 space-y-8">
        <div className="flex flex-col gap-3 animate-fade-in">
          <div className="flex items-center gap-3">
            <div className="h-1 w-12 bg-chart-5 rounded-full" />
            <span className="text-sm font-medium text-chart-5 uppercase tracking-wider">Análise de Dados</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-balance">Relatórios</h1>
          <p className="text-lg text-muted-foreground max-w-2xl text-pretty leading-relaxed">
            Análises detalhadas e insights estratégicos dos dados coletados
          </p>
        </div>

        <RelatoriosCharts />
        <RelatoriosInsights />
      </main>
    </div>
  )
}
