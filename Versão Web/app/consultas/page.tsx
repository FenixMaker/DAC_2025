import { DashboardHeader } from "@/components/dashboard-header"
import { ConsultasTable } from "@/components/consultas-table"
import { ConsultasFilters } from "@/components/consultas-filters"

export default function ConsultasPage() {
  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />
      <main className="container mx-auto px-4 py-8 space-y-8">
        <div className="flex flex-col gap-3 animate-fade-in">
          <div className="flex items-center gap-3">
            <div className="h-1 w-12 bg-accent rounded-full" />
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Pesquisa Avançada</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-balance">Consultas</h1>
          <p className="text-lg text-muted-foreground max-w-2xl text-pretty leading-relaxed">
            Pesquise e filtre dados de indivíduos e domicílios com filtros avançados
          </p>
        </div>

        <ConsultasFilters />
        <ConsultasTable />
      </main>
    </div>
  )
}
