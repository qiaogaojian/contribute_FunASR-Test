import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import { apiClient } from '@/utils/api'

export interface AppState {
  isLoading: boolean
  isOnline: boolean
  theme: 'light' | 'dark' | 'auto'
  language: 'zh-CN' | 'en-US'
  notifications: Notification[]
  modals: Modal[]
}

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
  actions?: NotificationAction[]
}

export interface NotificationAction {
  label: string
  action: () => void
  style?: 'primary' | 'secondary'
}

export interface Modal {
  id: string
  component?: string
  title?: string
  content?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  class?: string
  closable?: boolean
  actions?: ModalAction[]
  props?: Record<string, any>
  options?: ModalOptions
}

export interface ModalAction {
  label: string
  type?: 'primary' | 'secondary' | 'danger'
  handler?: () => void
  close?: boolean
}

export interface ModalOptions {
  closable?: boolean
  maskClosable?: boolean
  width?: string
  height?: string
  zIndex?: number
}

export const useAppStore = defineStore('app', () => {
  // 状态
  const isLoading: Ref<boolean> = ref(false)
  const isOnline: Ref<boolean> = ref(navigator.onLine)
  const theme: Ref<'light' | 'dark' | 'auto'> = ref('auto')
  const language: Ref<'zh-CN' | 'en-US'> = ref('zh-CN')
  const notifications: Ref<Notification[]> = ref([])
  const modals: Ref<Modal[]> = ref([])
  const appInfo: Ref<any> = ref(null)

  // 计算属性
  const currentTheme = computed(() => {
    if (theme.value === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return theme.value
  })

  const hasNotifications = computed(() => notifications.value.length > 0)
  const hasModals = computed(() => modals.value.length > 0)

  // 动作
  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  const setOnlineStatus = (online: boolean) => {
    isOnline.value = online
  }

  const setTheme = (newTheme: 'light' | 'dark' | 'auto') => {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    applyTheme()
  }

  const setLanguage = (newLanguage: 'zh-CN' | 'en-US') => {
    language.value = newLanguage
    localStorage.setItem('language', newLanguage)
  }

  const applyTheme = () => {
    const root = document.documentElement
    const isDark = currentTheme.value === 'dark'
    
    if (isDark) {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  }

  // 通知管理
  const addNotification = (notification: Omit<Notification, 'id'>) => {
    const id = Date.now().toString()
    const newNotification: Notification = {
      id,
      duration: 5000,
      ...notification
    }
    
    notifications.value.push(newNotification)
    
    // 自动移除通知
    if (newNotification.duration && newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, newNotification.duration)
    }
    
    return id
  }

  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearNotifications = () => {
    notifications.value = []
  }

  // 便捷通知方法
  const showSuccess = (title: string, message?: string, duration?: number) => {
    return addNotification({ type: 'success', title, message, duration })
  }

  const showError = (title: string, message?: string, duration?: number) => {
    return addNotification({ type: 'error', title, message, duration: duration || 0 })
  }

  const showWarning = (title: string, message?: string, duration?: number) => {
    return addNotification({ type: 'warning', title, message, duration })
  }

  const showInfo = (title: string, message?: string, duration?: number) => {
    return addNotification({ type: 'info', title, message, duration })
  }

  // 模态框管理
  const openModal = (component: string, props?: Record<string, any>, options?: ModalOptions) => {
    const id = Date.now().toString()
    const modal: Modal = {
      id,
      component,
      props,
      options: {
        closable: true,
        maskClosable: true,
        ...options
      }
    }
    
    modals.value.push(modal)
    return id
  }

  const addModal = (modal: Omit<Modal, 'id'>) => {
    const id = Date.now().toString()
    const newModal: Modal = {
      id,
      ...modal
    }
    
    modals.value.push(newModal)
    return id
  }

  const closeModal = (id: string) => {
    const index = modals.value.findIndex(m => m.id === id)
    if (index > -1) {
      modals.value.splice(index, 1)
    }
  }

  const closeAllModals = () => {
    modals.value = []
  }

  // 应用初始化
  const initialize = async () => {
    try {
      setLoading(true)
      
      // 从本地存储恢复设置
      const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'auto'
      if (savedTheme) {
        theme.value = savedTheme
      }
      
      const savedLanguage = localStorage.getItem('language') as 'zh-CN' | 'en-US'
      if (savedLanguage) {
        language.value = savedLanguage
      }
      
      // 应用主题
      applyTheme()
      
      // 获取应用信息
      const response = await apiClient.get('/api/health')
      appInfo.value = response.data
      
      console.log('应用初始化成功')
    } catch (error) {
      console.error('应用初始化失败:', error)
      showError('初始化失败', '应用初始化时发生错误，请刷新页面重试')
    } finally {
      setLoading(false)
    }
  }

  // 监听系统主题变化
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.addEventListener('change', () => {
    if (theme.value === 'auto') {
      applyTheme()
    }
  })

  return {
    // 状态
    isLoading,
    isOnline,
    theme,
    language,
    notifications,
    modals,
    appInfo,
    
    // 计算属性
    currentTheme,
    hasNotifications,
    hasModals,
    
    // 动作
    setLoading,
    setOnlineStatus,
    setTheme,
    setLanguage,
    applyTheme,
    
    // 通知
    addNotification,
    removeNotification,
    clearNotifications,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    
    // 模态框
    openModal,
    addModal,
    closeModal,
    closeAllModals,
    
    // 初始化
    initialize
  }
})