import { DashboardHeader } from "@/components/dashboard-header"
import { StatsCards } from "@/components/stats-cards"
import { ChartsSection } from "@/components/charts-section"

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />
      <main className="container mx-auto px-4 py-8 space-y-8">
        <div className="flex flex-col gap-3 animate-fade-in">
          <div className="flex items-center gap-3">
            <div className="h-1 w-12 bg-primary rounded-full" />
            <span className="text-sm font-medium text-primary uppercase tracking-wider">Sistema DAC</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-balance">Dashboard de Análise</h1>
          <p className="text-lg text-muted-foreground max-w-2xl text-pretty leading-relaxed">
            Visão geral completa das estatísticas e métricas do sistema de controle digital
          </p>
        </div>

        <StatsCards />
        <ChartsSection />
      </main>
    </div>
  )
}
