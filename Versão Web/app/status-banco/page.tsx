import { DashboardHeader } from '@/components/dashboard-header'
import { DbStatusDashboard } from '@/components/db-status'

export default function StatusBancoPage() {
  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />
      <main className="container mx-auto px-4 py-8 space-y-8">
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-3">
            <div className="h-1 w-12 bg-primary rounded-full" />
            <span className="text-sm font-medium text-primary uppercase tracking-wider">Infraestrutura</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight">Status do Banco de Dados</h1>
          <p className="text-lg text-muted-foreground max-w-2xl">
            Painel com métricas principais do PostgreSQL do DAC (atualiza a cada acesso)
          </p>
        </div>

        <DbStatusDashboard />
      </main>
    </div>
  )
}
