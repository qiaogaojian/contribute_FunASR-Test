import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

// 扩展 dayjs 插件
dayjs.extend(duration)
dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

// 时间格式化工具
export const formatTime = {
  // 格式化日期时间
  datetime: (date: string | Date | number, format = 'YYYY-MM-DD HH:mm:ss'): string => {
    return dayjs(date).format(format)
  },
  
  // 格式化日期
  date: (date: string | Date | number, format = 'YYYY-MM-DD'): string => {
    return dayjs(date).format(format)
  },
  
  // 格式化时间
  time: (date: string | Date | number, format = 'HH:mm:ss'): string => {
    return dayjs(date).format(format)
  },
  
  // 相对时间
  relative: (date: string | Date | number): string => {
    return dayjs(date).fromNow()
  },
  
  // 格式化持续时间（秒）
  duration: (seconds: number): string => {
    const duration = dayjs.duration(seconds, 'seconds')
    const hours = Math.floor(duration.asHours())
    const minutes = duration.minutes()
    const secs = duration.seconds()
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    } else {
      return `${minutes}:${secs.toString().padStart(2, '0')}`
    }
  },
  
  // 格式化持续时间（毫秒）
  durationMs: (milliseconds: number): string => {
    return formatTime.duration(Math.floor(milliseconds / 1000))
  }
}

// 兼容性函数 - formatDate
export const formatDate = (date: string | Date | number, format = 'YYYY-MM-DD HH:mm:ss'): string => {
  return dayjs(date).format(format)
}

// 文件大小格式化
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 防抖函数
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  immediate = false
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null
  
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      if (!immediate) func(...args)
    }
    
    const callNow = immediate && !timeout
    
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(later, wait)
    
    if (callNow) func(...args)
  }
}

// 节流函数
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean
  
  return function executedFunction(this: any, ...args: Parameters<T>) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

// 深拷贝
export const deepClone = <T>(obj: T): T => {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime()) as unknown as T
  }
  
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as unknown as T
  }
  
  if (typeof obj === 'object') {
    const clonedObj = {} as { [key: string]: any }
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj as T
  }
  
  return obj
}

// 生成唯一 ID
export const generateId = (prefix = ''): string => {
  const timestamp = Date.now().toString(36)
  const randomStr = Math.random().toString(36).substr(2, 9)
  return `${prefix}${timestamp}${randomStr}`
}

// 生成 UUID
export const generateUUID = (): string => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

// 数组去重
export const uniqueArray = <T>(array: T[], key?: keyof T): T[] => {
  if (!key) {
    return [...new Set(array)]
  }
  
  const seen = new Set()
  return array.filter(item => {
    const value = item[key]
    if (seen.has(value)) {
      return false
    }
    seen.add(value)
    return true
  })
}

// 数组分组
export const groupBy = <T, K extends keyof T>(
  array: T[],
  key: K
): Record<string, T[]> => {
  return array.reduce((groups, item) => {
    const group = String(item[key])
    groups[group] = groups[group] || []
    groups[group].push(item)
    return groups
  }, {} as Record<string, T[]>)
}

// 数组排序
export const sortBy = <T>(
  array: T[],
  key: keyof T,
  order: 'asc' | 'desc' = 'asc'
): T[] => {
  return [...array].sort((a, b) => {
    const aVal = a[key]
    const bVal = b[key]
    
    if (aVal < bVal) return order === 'asc' ? -1 : 1
    if (aVal > bVal) return order === 'asc' ? 1 : -1
    return 0
  })
}

// 字符串工具
export const stringUtils = {
  // 首字母大写
  capitalize: (str: string): string => {
    return str.charAt(0).toUpperCase() + str.slice(1)
  },
  
  // 驼峰转短横线
  kebabCase: (str: string): string => {
    return str.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').toLowerCase()
  },
  
  // 短横线转驼峰
  camelCase: (str: string): string => {
    return str.replace(/-([a-z])/g, (g) => g[1].toUpperCase())
  },
  
  // 截断文本
  truncate: (str: string, length: number, suffix = '...'): string => {
    if (str.length <= length) return str
    return str.slice(0, length) + suffix
  },
  
  // 移除 HTML 标签
  stripHtml: (str: string): string => {
    return str.replace(/<[^>]*>/g, '')
  },
  
  // 转义 HTML
  escapeHtml: (str: string): string => {
    const div = document.createElement('div')
    div.textContent = str
    return div.innerHTML
  }
}

// 数字工具
export const numberUtils = {
  // 格式化数字（添加千分位分隔符）
  format: (num: number, decimals = 0): string => {
    return num.toLocaleString('zh-CN', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    })
  },
  
  // 格式化百分比
  percentage: (num: number, decimals = 1): string => {
    return (num * 100).toFixed(decimals) + '%'
  },
  
  // 随机数
  random: (min: number, max: number): number => {
    return Math.floor(Math.random() * (max - min + 1)) + min
  },
  
  // 限制数字范围
  clamp: (num: number, min: number, max: number): number => {
    return Math.min(Math.max(num, min), max)
  }
}

// URL 工具
export const urlUtils = {
  // 获取查询参数
  getQuery: (name: string, url?: string): string | null => {
    const urlObj = new URL(url || window.location.href)
    return urlObj.searchParams.get(name)
  },
  
  // 设置查询参数
  setQuery: (params: Record<string, string>, url?: string): string => {
    const urlObj = new URL(url || window.location.href)
    Object.entries(params).forEach(([key, value]) => {
      urlObj.searchParams.set(key, value)
    })
    return urlObj.toString()
  },
  
  // 移除查询参数
  removeQuery: (names: string[], url?: string): string => {
    const urlObj = new URL(url || window.location.href)
    names.forEach(name => {
      urlObj.searchParams.delete(name)
    })
    return urlObj.toString()
  }
}

// 本地存储工具
export const storage = {
  // 设置本地存储
  set: (key: string, value: any): void => {
    try {
      localStorage.setItem(key, JSON.stringify(value))
    } catch (error) {
      console.error('设置本地存储失败:', error)
    }
  },
  
  // 获取本地存储
  get: <T = any>(key: string, defaultValue?: T): T | null => {
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : defaultValue || null
    } catch (error) {
      console.error('获取本地存储失败:', error)
      return defaultValue || null
    }
  },
  
  // 移除本地存储
  remove: (key: string): void => {
    try {
      localStorage.removeItem(key)
    } catch (error) {
      console.error('移除本地存储失败:', error)
    }
  },
  
  // 清空本地存储
  clear: (): void => {
    try {
      localStorage.clear()
    } catch (error) {
      console.error('清空本地存储失败:', error)
    }
  }
}

// 会话存储工具
export const sessionStorage = {
  // 设置会话存储
  set: (key: string, value: any): void => {
    try {
      window.sessionStorage.setItem(key, JSON.stringify(value))
    } catch (error) {
      console.error('设置会话存储失败:', error)
    }
  },
  
  // 获取会话存储
  get: <T = any>(key: string, defaultValue?: T): T | null => {
    try {
      const item = window.sessionStorage.getItem(key)
      return item ? JSON.parse(item) : defaultValue || null
    } catch (error) {
      console.error('获取会话存储失败:', error)
      return defaultValue || null
    }
  },
  
  // 移除会话存储
  remove: (key: string): void => {
    try {
      window.sessionStorage.removeItem(key)
    } catch (error) {
      console.error('移除会话存储失败:', error)
    }
  },
  
  // 清空会话存储
  clear: (): void => {
    try {
      window.sessionStorage.clear()
    } catch (error) {
      console.error('清空会话存储失败:', error)
    }
  }
}

// 设备检测
export const device = {
  // 是否为移动设备
  isMobile: (): boolean => {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent
    )
  },
  
  // 是否为平板设备
  isTablet: (): boolean => {
    return /iPad|Android(?!.*Mobile)/i.test(navigator.userAgent)
  },
  
  // 是否为桌面设备
  isDesktop: (): boolean => {
    return !device.isMobile() && !device.isTablet()
  },
  
  // 是否为 iOS
  isIOS: (): boolean => {
    return /iPad|iPhone|iPod/.test(navigator.userAgent)
  },
  
  // 是否为 Android
  isAndroid: (): boolean => {
    return /Android/.test(navigator.userAgent)
  },
  
  // 获取设备类型
  getType: (): 'mobile' | 'tablet' | 'desktop' => {
    if (device.isMobile()) return 'mobile'
    if (device.isTablet()) return 'tablet'
    return 'desktop'
  }
}

// 颜色工具
export const colorUtils = {
  // 十六进制转 RGB
  hexToRgb: (hex: string): { r: number; g: number; b: number } | null => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result
      ? {
          r: parseInt(result[1], 16),
          g: parseInt(result[2], 16),
          b: parseInt(result[3], 16)
        }
      : null
  },
  
  // RGB 转十六进制
  rgbToHex: (r: number, g: number, b: number): string => {
    return '#' + [r, g, b].map(x => {
      const hex = x.toString(16)
      return hex.length === 1 ? '0' + hex : hex
    }).join('')
  },
  
  // 生成随机颜色
  random: (): string => {
    return '#' + Math.floor(Math.random() * 16777215).toString(16)
  }
}

// 验证工具
export const validate = {
  // 邮箱验证
  email: (email: string): boolean => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return re.test(email)
  },
  
  // 手机号验证（中国）
  phone: (phone: string): boolean => {
    const re = /^1[3-9]\d{9}$/
    return re.test(phone)
  },
  
  // URL 验证
  url: (url: string): boolean => {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  },
  
  // 身份证验证（中国）
  idCard: (idCard: string): boolean => {
    const re = /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/
    return re.test(idCard)
  }
}

export default {
  formatTime,
  formatFileSize,
  debounce,
  throttle,
  deepClone,
  generateId,
  generateUUID,
  uniqueArray,
  groupBy,
  sortBy,
  stringUtils,
  numberUtils,
  urlUtils,
  storage,
  sessionStorage,
  device,
  colorUtils,
  validate
}