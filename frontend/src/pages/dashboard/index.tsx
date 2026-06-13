import { useQuery } from '@tanstack/react-query'
import {
  Users,
  Activity,
  FileText,
  TrendingUp,
  Clock,
  ArrowUpRight,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { competitorApi, analysisApi, reportApi } from '@/lib/api'
import { formatRelativeTime } from '@/lib/utils'
import type { Competitor, AnalysisTask, Report } from '@/types'

export default function Dashboard() {
  const { data: competitorsData, isLoading: loadingCompetitors } = useQuery({
    queryKey: ['competitors'],
    queryFn: () => competitorApi.list({ page: 1, page_size: 100 }),
  })

  const { data: tasksData, isLoading: loadingTasks } = useQuery({
    queryKey: ['analysis-tasks'],
    queryFn: () => analysisApi.listTasks({ page: 1, page_size: 100 }),
  })

  const { data: reportsData, isLoading: loadingReports } = useQuery({
    queryKey: ['reports'],
    queryFn: () => reportApi.list({ page: 1, page_size: 100 }),
  })

  const competitors = competitorsData?.data?.data || []
  const tasks = tasksData?.data?.data || []
  const reports = reportsData?.data?.data || []

  const stats = [
    {
      title: '竞品总数',
      value: competitors.length,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/30',
    },
    {
      title: '监控中',
      value: competitors.filter((c: Competitor) => c.website).length,
      icon: Activity,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/30',
    },
    {
      title: '分析任务',
      value: tasks.length,
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100 dark:bg-purple-900/30',
    },
    {
      title: '生成报告',
      value: reports.length,
      icon: FileText,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100 dark:bg-orange-900/30',
    },
  ]

  const recentTasks = tasks.slice(0, 5)
  const recentReports = reports.slice(0, 5)

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'success' | 'warning'> = {
      pending: 'secondary',
      running: 'warning',
      completed: 'success',
      failed: 'destructive',
    }
    const labels: Record<string, string> = {
      pending: '待执行',
      running: '执行中',
      completed: '已完成',
      failed: '失败',
    }
    return (
      <Badge variant={variants[status] || 'default'}>
        {labels[status] || status}
      </Badge>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">仪表盘</h1>
        <p className="text-muted-foreground mt-2">
          欢迎回来，这是您的竞品分析概览
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {loadingCompetitors || loadingTasks || loadingReports ? (
          <>
            {[...Array(4)].map((_, i) => (
              <Card key={i}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <Skeleton className="h-4 w-20" />
                  <Skeleton className="h-8 w-8 rounded-full" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-8 w-16" />
                </CardContent>
              </Card>
            ))}
          </>
        ) : (
          <>
            {stats.map((stat) => (
              <Card key={stat.title}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {stat.title}
                  </CardTitle>
                  <div className={`${stat.bgColor} p-2 rounded-full`}>
                    <stat.icon className={`h-4 w-4 ${stat.color}`} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{stat.value}</div>
                </CardContent>
              </Card>
            ))}
          </>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Tasks */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">最近任务</CardTitle>
              <a
                href="/analysis"
                className="text-sm text-primary hover:underline flex items-center gap-1"
              >
                查看全部
                <ArrowUpRight className="h-3 w-3" />
              </a>
            </div>
          </CardHeader>
          <CardContent>
            {loadingTasks ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <Skeleton className="h-10 w-10 rounded" />
                    <div className="flex-1">
                      <Skeleton className="h-4 w-32 mb-1" />
                      <Skeleton className="h-3 w-24" />
                    </div>
                  </div>
                ))}
              </div>
            ) : recentTasks.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">
                暂无分析任务
              </p>
            ) : (
              <div className="space-y-4">
                {recentTasks.map((task: AnalysisTask) => (
                  <div
                    key={task.id}
                    className="flex items-center gap-4 p-3 rounded-lg hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {task.competitors.join(', ')}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        {getStatusBadge(task.status)}
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {task.created_at ? formatRelativeTime(task.created_at) : '-'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Reports */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">最近报告</CardTitle>
              <a
                href="/reports"
                className="text-sm text-primary hover:underline flex items-center gap-1"
              >
                查看全部
                <ArrowUpRight className="h-3 w-3" />
              </a>
            </div>
          </CardHeader>
          <CardContent>
            {loadingReports ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <Skeleton className="h-10 w-10 rounded" />
                    <div className="flex-1">
                      <Skeleton className="h-4 w-40 mb-1" />
                      <Skeleton className="h-3 w-28" />
                    </div>
                  </div>
                ))}
              </div>
            ) : recentReports.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">
                暂无分析报告
              </p>
            ) : (
              <div className="space-y-4">
                {recentReports.map((report: Report) => (
                  <div
                    key={report.id}
                    className="flex items-center gap-4 p-3 rounded-lg hover:bg-accent/50 transition-colors"
                  >
                    <div className="w-10 h-10 rounded bg-primary/10 flex items-center justify-center">
                      <FileText className="h-5 w-5 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {report.title}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline">{report.report_type}</Badge>
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {report.created_at ? formatRelativeTime(report.created_at) : '-'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
