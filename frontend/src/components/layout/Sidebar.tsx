import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  BarChart3,
  FileText,
  MessageSquare,
  Settings,
  HelpCircle,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  {
    title: '仪表盘',
    href: '/',
    icon: LayoutDashboard,
  },
  {
    title: '竞品管理',
    href: '/competitors',
    icon: Users,
  },
  {
    title: '分析任务',
    href: '/analysis',
    icon: BarChart3,
  },
  {
    title: '报告中心',
    href: '/reports',
    icon: FileText,
  },
  {
    title: '智能问答',
    href: '/qa',
    icon: MessageSquare,
  },
]

const bottomNavItems = [
  {
    title: '设置',
    href: '/settings',
    icon: Settings,
  },
  {
    title: '帮助',
    href: '/help',
    icon: HelpCircle,
  },
]

interface SidebarProps {
  collapsed?: boolean
}

export function Sidebar({ collapsed = false }: SidebarProps) {
  const location = useLocation()

  const isActive = (href: string) => {
    if (href === '/') return location.pathname === '/'
    return location.pathname.startsWith(href)
  }

  return (
    <aside
      className={cn(
        'flex flex-col h-screen border-r bg-card transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Logo */}
      <div className="flex items-center h-16 px-4 border-b">
        <Link to="/" className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary text-primary-foreground">
            <BarChart3 className="w-5 h-5" />
          </div>
          {!collapsed && (
            <span className="font-semibold text-lg">竞品分析</span>
          )}
        </Link>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto scrollbar-thin">
        {navItems.map((item) => (
          <Link
            key={item.href}
            to={item.href}
            className={cn(
              'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
              isActive(item.href)
                ? 'bg-primary/10 text-primary'
                : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
            )}
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {!collapsed && <span>{item.title}</span>}
          </Link>
        ))}
      </nav>

      {/* Bottom Navigation */}
      <div className="px-3 py-4 space-y-1 border-t">
        {bottomNavItems.map((item) => (
          <Link
            key={item.href}
            to={item.href}
            className={cn(
              'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
              isActive(item.href)
                ? 'bg-primary/10 text-primary'
                : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
            )}
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {!collapsed && <span>{item.title}</span>}
          </Link>
        ))}
      </div>
    </aside>
  )
}
