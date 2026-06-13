import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  Plus,
  Play,
  Clock,
  CheckCircle2,
  XCircle,
  Loader2,
  Eye,
  Trash2,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Checkbox } from '@/components/ui/checkbox'
import { Pagination } from '@/components/ui/pagination'
import { analysisApi, competitorApi } from '@/lib/api'
import { formatDate } from '@/lib/utils'
import { toast } from 'sonner'
import type { AnalysisTask, AnalysisSubmitRequest } from '@/types'

const analysisDimensions = [
  { id: 'features', label: '功能特性' },
  { id: 'pricing', label: '定价策略' },
  { id: 'swot', label: 'SWOT 分析' },
  { id: 'marketing', label: '营销策略' },
]

export default function AnalysisList() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [showDialog, setShowDialog] = useState(false)
  const [selectedCompetitors, setSelectedCompetitors] = useState<string[]>([])
  const [selectedDimensions, setSelectedDimensions] = useState<string[]>(['features', 'pricing', 'swot'])
  const [myProduct, setMyProduct] = useState('')
  const [deleteTarget, setDeleteTarget] = useState<AnalysisTask | null>(null)

  const { data: tasksData, isLoading } = useQuery({
    queryKey: ['analysis-tasks', page],
    queryFn: () => analysisApi.listTasks({ page, page_size: 10 }),
  })

  const { data: competitorsData } = useQuery({
    queryKey: ['competitors-all'],
    queryFn: () => competitorApi.list({ page: 1, page_size: 100 }),
  })

  const submitMutation = useMutation({
    mutationFn: (data: AnalysisSubmitRequest) => analysisApi.submit(data),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['analysis-tasks'] })
      toast.success('分析任务已提交')
      setShowDialog(false)
      resetForm()
      // 跳转到任务详情
      const taskId = response.data?.data?.task_id
      if (taskId) {
        navigate(`/analysis/${taskId}`)
      }
    },
    onError: (error: Error) => {
      toast.error(error.message)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (taskId: string) => analysisApi.deleteTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['analysis-tasks'] })
      toast.success('任务已删除')
      setDeleteTarget(null)
    },
    onError: (error: Error) => {
      toast.error(error.message)
    },
  })

  const tasks = tasksData?.data?.data || []
  const total = tasksData?.data?.total || 0
  const totalPages = Math.ceil(total / 10)
  const competitors = competitorsData?.data?.data || []

  const resetForm = () => {
    setSelectedCompetitors([])
    setSelectedDimensions(['features', 'pricing', 'swot'])
    setMyProduct('')
  }

  const handleSubmit = () => {
    if (selectedCompetitors.length === 0) {
      toast.error('请选择至少一个竞品')
      return
    }

    submitMutation.mutate({
      competitors: selectedCompetitors,
      dimensions: selectedDimensions,
      my_product: myProduct || undefined,
    })
  }

  const toggleCompetitor = (id: string) => {
    setSelectedCompetitors((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    )
  }

  const toggleDimension = (id: string) => {
    setSelectedDimensions((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id]
    )
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-4 w-4 text-muted-foreground" />
      case 'running':
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      default:
        return null
    }
  }

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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">分析任务</h1>
          <p className="text-muted-foreground mt-2">管理和查看竞品分析任务</p>
        </div>
        <Button onClick={() => setShowDialog(true)}>
          <Plus className="mr-2 h-4 w-4" />
          新建分析
        </Button>
      </div>

      {/* Tasks Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex items-center gap-4">
                  <Skeleton className="h-10 w-10 rounded" />
                  <div className="flex-1">
                    <Skeleton className="h-4 w-48 mb-2" />
                    <Skeleton className="h-3 w-32" />
                  </div>
                </div>
              ))}
            </div>
          ) : tasks.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <p className="text-muted-foreground mb-4">暂无分析任务</p>
              <Button variant="outline" onClick={() => setShowDialog(true)}>
                <Plus className="mr-2 h-4 w-4" />
                创建第一个任务
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>任务 ID</TableHead>
                  <TableHead>竞品</TableHead>
                  <TableHead>分析维度</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead>创建时间</TableHead>
                  <TableHead className="w-[100px]">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {tasks.map((task: AnalysisTask) => (
                  <TableRow key={task.id}>
                    <TableCell className="font-mono text-sm">
                      {task.id.slice(0, 8)}...
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1 flex-wrap">
                        {task.competitors.slice(0, 2).map((name) => (
                          <Badge key={name} variant="outline" className="text-xs">
                            {name}
                          </Badge>
                        ))}
                        {task.competitors.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{task.competitors.length - 2}
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1 flex-wrap">
                        {task.dimensions.map((dim) => (
                          <Badge key={dim} variant="secondary" className="text-xs">
                            {dim}
                          </Badge>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(task.status)}
                        {getStatusBadge(task.status)}
                      </div>
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {task.created_at ? formatDate(task.created_at) : '-'}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => navigate(`/analysis/${task.id}`)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-destructive hover:text-destructive"
                          onClick={() => setDeleteTarget(task)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}

          {totalPages > 1 && (
            <div className="py-4 border-t">
              <Pagination
                currentPage={page}
                totalPages={totalPages}
                onPageChange={setPage}
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>新建分析任务</DialogTitle>
            <DialogDescription>
              选择竞品和分析维度来创建新的分析任务
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 py-4">
            {/* Select Competitors */}
            <div className="space-y-3">
              <Label>选择竞品 *</Label>
              <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto p-2 border rounded-md">
                {competitors.map((competitor: { id: string; name: string }) => (
                  <div
                    key={competitor.id}
                    className="flex items-center space-x-2 p-2 rounded hover:bg-accent"
                  >
                    <Checkbox
                      id={competitor.id}
                      checked={selectedCompetitors.includes(competitor.name)}
                      onCheckedChange={() => toggleCompetitor(competitor.name)}
                    />
                    <label
                      htmlFor={competitor.id}
                      className="text-sm font-medium leading-none cursor-pointer"
                    >
                      {competitor.name}
                    </label>
                  </div>
                ))}
              </div>
              {selectedCompetitors.length > 0 && (
                <p className="text-sm text-muted-foreground">
                  已选择 {selectedCompetitors.length} 个竞品
                </p>
              )}
            </div>

            {/* Dimensions */}
            <div className="space-y-3">
              <Label>分析维度</Label>
              <div className="grid grid-cols-2 gap-2">
                {analysisDimensions.map((dim) => (
                  <div
                    key={dim.id}
                    className="flex items-center space-x-2 p-2 rounded hover:bg-accent"
                  >
                    <Checkbox
                      id={dim.id}
                      checked={selectedDimensions.includes(dim.id)}
                      onCheckedChange={() => toggleDimension(dim.id)}
                    />
                    <label
                      htmlFor={dim.id}
                      className="text-sm font-medium leading-none cursor-pointer"
                    >
                      {dim.label}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* My Product */}
            <div className="space-y-2">
              <Label htmlFor="myProduct">我方产品名称（可选）</Label>
              <Input
                id="myProduct"
                placeholder="输入您的产品名称，用于对比分析"
                value={myProduct}
                onChange={(e) => setMyProduct(e.target.value)}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowDialog(false)
                resetForm()
              }}
            >
              取消
            </Button>
            <Button onClick={handleSubmit} disabled={submitMutation.isPending}>
              {submitMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  提交中...
                </>
              ) : (
                <>
                  <Play className="mr-2 h-4 w-4" />
                  开始分析
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteTarget} onOpenChange={() => setDeleteTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
            <DialogDescription>
              确定要删除任务 {deleteTarget?.id.slice(0, 8)}... 吗？此操作不可撤销。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>
              取消
            </Button>
            <Button
              variant="destructive"
              onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? '删除中...' : '确认删除'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
