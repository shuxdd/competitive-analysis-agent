import { useLocation } from 'react-router-dom'
import { Sun, Moon, Bell, Menu, Search, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useTheme } from '@/hooks/useTheme'
import { useAuth } from '@/contexts/AuthContext'

interface TopbarProps {
  onToggleSidebar: () => void
}

export function Topbar({ onToggleSidebar }: TopbarProps) {
  const { theme, toggleTheme } = useTheme()
  const { user, logout } = useAuth()
  const location = useLocation()

  const getBreadcrumb = () => {
    const path = location.pathname
    if (path === '/') return '仪表盘'
    if (path.startsWith('/competitors')) return '竞品管理'
    if (path.startsWith('/analysis')) return '分析任务'
    if (path.startsWith('/reports')) return '报告中心'
    if (path.startsWith('/qa')) return '智能问答'
    return '首页'
  }

  return (
    <header className="sticky top-0 z-40 flex items-center h-16 px-6 border-b bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60">
      <div className="flex items-center gap-4 flex-1">
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onToggleSidebar}
        >
          <Menu className="w-5 h-5" />
        </Button>

        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>首页</span>
          <span>/</span>
          <span className="text-foreground font-medium">{getBreadcrumb()}</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <div className="relative hidden md:block">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="搜索..."
            className="w-64 pl-8"
          />
        </div>

        <Button variant="ghost" size="icon" className="relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
        </Button>

        <Button variant="ghost" size="icon" onClick={toggleTheme}>
          {theme === 'light' ? (
            <Moon className="w-5 h-5" />
          ) : (
            <Sun className="w-5 h-5" />
          )}
        </Button>

        <div className="flex items-center gap-2 ml-2 pl-2 border-l">
          <span className="text-sm text-muted-foreground hidden md:inline">
            {user?.display_name || user?.username}
          </span>
          <Button variant="ghost" size="icon" onClick={logout} title="退出登录">
            <LogOut className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </header>
  )
}
