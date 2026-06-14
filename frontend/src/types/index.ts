// 竞品
export interface Competitor {
  id: string
  name: string
  website?: string
  industry?: string
  tags: string[]
  notes?: string
  created_at?: string
  updated_at?: string
}

export interface CompetitorCreateRequest {
  name: string
  website?: string
  industry?: string
  tags: string[]
  notes?: string
}

export interface CompetitorUpdateRequest {
  name?: string
  website?: string
  industry?: string
  tags?: string[]
  notes?: string
}

// 分析任务
export interface AnalysisSubmitRequest {
  competitors: string[]
  analysis_type?: string
  dimensions?: string[]
  my_product?: string
}

export interface AnalysisTask {
  id: string
  competitors: string[]
  analysis_type: string
  dimensions: string[]
  my_product?: string
  status: 'pending' | 'running' | 'planning' | 'collecting' | 'completed' | 'failed'
  result?: Record<string, unknown>
  error_message?: string
  created_at?: string
  completed_at?: string
}

// 报告
export interface Report {
  id: string
  analysis_id: string
  title: string
  report_type: string
  format: string
  content: string
  file_path?: string
  created_at?: string
}

// 智能问答
export interface QARequest {
  question: string
  competitors?: string[]
}

export interface QAResponse {
  answer: string
  sources: string[]
}

// 通用响应
export interface ApiResponse<T = unknown> {
  code: number
  data: T
  message: string
}

export interface PaginatedResponse<T = unknown> {
  code: number
  data: T[]
  total: number
  page: number
  page_size: number
  message: string
}

// 统计数据
export interface DashboardStats {
  totalCompetitors: number
  monitoring: number
  totalTasks: number
  totalReports: number
}

// 时间线事件
export interface TimelineEvent {
  id: string
  type: 'analysis' | 'report'
  title: string
  description: string
  timestamp: string
}

// 图表数据
export interface ChartData {
  name: string
  value: number
}
