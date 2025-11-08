import Link from "next/link"
import { Logo } from "@/components/logo"
import { Menu, Activity } from "lucide-react"
import { Button } from "@/components/ui/button"

export function DashboardHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-border/40 glass-effect bg-background/70">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center group">
              <Logo variant="simplified" size={64} priority className="shrink-0" />
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
