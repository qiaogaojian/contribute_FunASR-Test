import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosResponse } from 'axios'
import { useAppStore } from '@/stores/app'

// API 基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_TIMEOUT = 30000 // 30秒超时

// 用于存储请求时间的Map
const requestTimeMap = new Map<string, Date>()

// 创建 axios 实例
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 添加请求时间戳
    const requestId = `${config.method}-${config.url}-${Date.now()}`
    requestTimeMap.set(requestId, new Date())
    config.headers['X-Request-ID'] = requestId
    
    // 可以在这里添加认证 token
    // const token = localStorage.getItem('auth_token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    
    return config
  },
  (error) => {
    console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // 计算请求耗时
    const endTime = new Date()
    const requestId = response.config.headers['X-Request-ID'] as string
    const startTime = requestTimeMap.get(requestId)
    if (startTime) {
      const duration = endTime.getTime() - startTime.getTime()
      console.log(`API 请求耗时: ${duration}ms - ${response.config.method?.toUpperCase()} ${response.config.url}`)
      // 清理已完成的请求记录
      requestTimeMap.delete(requestId)
    }
    
    return response
  },
  (error) => {
    const appStore = useAppStore()
    
    // 处理网络错误
    if (!error.response) {
      console.error('网络错误:', error.message)
      appStore.showError('网络错误', '请检查网络连接')
      return Promise.reject(new Error('网络连接失败'))
    }
    
    // 处理 HTTP 错误状态码
    const { status, data } = error.response
    let errorMessage = '请求失败'
    
    switch (status) {
      case 400:
        errorMessage = data?.message || '请求参数错误'
        break
      case 401:
        errorMessage = '未授权访问'
        // 可以在这里处理登录过期
        // router.push('/login')
        break
      case 403:
        errorMessage = '访问被拒绝'
        break
      case 404:
        errorMessage = '请求的资源不存在'
        break
      case 422:
        errorMessage = data?.message || '数据验证失败'
        break
      case 429:
        errorMessage = '请求过于频繁，请稍后再试'
        break
      case 500:
        errorMessage = '服务器内部错误'
        break
      case 502:
        errorMessage = '网关错误'
        break
      case 503:
        errorMessage = '服务暂时不可用'
        break
      default:
        errorMessage = data?.message || `请求失败 (${status})`
    }
    
    console.error('API 错误:', {
      status,
      message: errorMessage,
      url: error.config?.url,
      method: error.config?.method,
      data: error.config?.data
    })
    
    return Promise.reject(new Error(errorMessage))
  }
)

// API 响应类型
export interface APIResponse<T = any> {
  success: boolean
  message: string
  data?: T
  error?: string
}

// 通用 API 方法
export class ApiService {
  // GET 请求
  static async get<T = any>(url: string, config?: InternalAxiosRequestConfig): Promise<APIResponse<T>> {
    try {
      const response = await apiClient.get<APIResponse<T>>(url, config)
      return response.data
    } catch (error: any) {
      return {
        success: false,
        message: error.message || '请求失败',
        error: error.message
      }
    }
  }
  
  // POST 请求
  static async post<T = any>(url: string, data?: any, config?: InternalAxiosRequestConfig): Promise<APIResponse<T>> {
    try {
      const response = await apiClient.post<APIResponse<T>>(url, data, config)
      return response.data
    } catch (error: any) {
      return {
        success: false,
        message: error.message || '请求失败',
        error: error.message
      }
    }
  }
  
  // PUT 请求
  static async put<T = any>(url: string, data?: any, config?: InternalAxiosRequestConfig): Promise<APIResponse<T>> {
    try {
      const response = await apiClient.put<APIResponse<T>>(url, data, config)
      return response.data
    } catch (error: any) {
      return {
        success: false,
        message: error.message || '请求失败',
        error: error.message
      }
    }
  }
  
  // DELETE 请求
  static async delete<T = any>(url: string, config?: InternalAxiosRequestConfig): Promise<APIResponse<T>> {
    try {
      const response = await apiClient.delete<APIResponse<T>>(url, config)
      return response.data
    } catch (error: any) {
      return {
        success: false,
        message: error.message || '请求失败',
        error: error.message
      }
    }
  }
  
  // PATCH 请求
  static async patch<T = any>(url: string, data?: any, config?: InternalAxiosRequestConfig): Promise<APIResponse<T>> {
    try {
      const response = await apiClient.patch<APIResponse<T>>(url, data, config)
      return response.data
    } catch (error: any) {
      return {
        success: false,
        message: error.message || '请求失败',
        error: error.message
      }
    }
  }
}

// 文件上传
export const uploadFile = async (file: File, onProgress?: (progress: number) => void): Promise<APIResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await apiClient.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
    
    return response.data
  } catch (error: any) {
    return {
      success: false,
      message: error.message || '文件上传失败',
      error: error.message
    }
  }
}

// 文件下载
export const downloadFile = async (url: string, filename?: string): Promise<void> => {
  try {
    const response = await apiClient.get(url, {
      responseType: 'blob',
    })
    
    // 创建下载链接
    const downloadUrl = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = downloadUrl
    
    // 设置文件名
    if (filename) {
      link.setAttribute('download', filename)
    } else {
      // 尝试从响应头获取文件名
      const contentDisposition = response.headers['content-disposition']
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/)
        if (filenameMatch) {
          link.setAttribute('download', filenameMatch[1])
        }
      }
    }
    
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(downloadUrl)
  } catch (error: any) {
    console.error('文件下载失败:', error)
    throw new Error(error.message || '文件下载失败')
  }
}

// 健康检查
export const healthCheck = async (): Promise<boolean> => {
  try {
    const response = await apiClient.get('/api/health', { timeout: 5000 })
    return response.status === 200
  } catch (error) {
    console.error('健康检查失败:', error)
    return false
  }
}



export default apiClient