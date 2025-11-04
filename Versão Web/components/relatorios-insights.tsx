import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp, AlertCircle, CheckCircle } from "lucide-react"

export function RelatoriosInsights() {
  const insights = [
    {
      title: "Crescimento de Dispositivos",
      description: "Aumento de 5.2% no número de dispositivos conectados",
      trend: "up",
      icon: TrendingUp,
      color: "text-green-500",
    },
    {
      title: "Acesso à Internet",
      description: "88.6% dos indivíduos possuem acesso à internet",
      trend: "up",
      icon: CheckCircle,
      color: "text-blue-500",
    },
    {
      title: "Região com Menor Cobertura",
      description: "Sul apresenta menor taxa de conectividade (78.3%)",
      trend: "down",
      icon: AlertCircle,
      color: "text-yellow-500",
    },
    {
      title: "Média de Dispositivos",
      description: "2.16 dispositivos por domicílio em média",
      trend: "neutral",
      icon: CheckCircle,
      color: "text-primary",
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {insights.map((insight) => {
        const Icon = insight.icon
        return (
          <Card key={insight.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-pretty">{insight.title}</CardTitle>
              <Icon className={`h-4 w-4 ${insight.color}`} />
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground text-pretty">{insight.description}</p>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
