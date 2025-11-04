import Link from "next/link"
import { BarChart3, Menu, Activity } from "lucide-react"
import { Button } from "@/components/ui/button"

export function DashboardHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-border/40 glass-effect bg-background/70">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-3 group">
              <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-accent shadow-lg shadow-primary/20 transition-all group-hover:shadow-xl group-hover:shadow-primary/30 group-hover:scale-105">
                <BarChart3 className="h-5 w-5 text-primary-foreground" />
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              <div className="flex flex-col">
                <span className="text-xl font-bold tracking-tight">DAC</span>
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Digital Analysis</span>
              </div>
            </Link>

            <nav className="hidden md:flex items-center gap-1">
              <Link
                href="/"
                className="relative px-4 py-2 text-sm font-medium transition-colors hover:text-foreground rounded-lg hover:bg-secondary/50 text-foreground"
              >
                Dashboard
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 h-0.5 w-8 bg-primary rounded-full" />
              </Link>
              <Link
                href="/consultas"
                className="px-4 py-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground rounded-lg hover:bg-secondary/50"
              >
                Consultas
              </Link>
              <Link
                href="/relatorios"
                className="px-4 py-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground rounded-lg hover:bg-secondary/50"
              >
                Relatórios
              </Link>
              <Link
                href="/status-banco"
                className="px-4 py-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground rounded-lg hover:bg-secondary/50"
              >
                Status do Banco
              </Link>
            </nav>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-secondary/50 border border-border/50">
              <Activity className="h-3.5 w-3.5 text-green-500 animate-pulse" />
              <span className="text-xs font-medium text-muted-foreground">Sistema Online</span>
            </div>
            <Button variant="ghost" size="icon" className="md:hidden">
              <Menu className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}
