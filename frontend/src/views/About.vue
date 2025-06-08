<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 页面头部 -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-4">
            <button
              @click="$router.go(-1)"
              class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <ArrowLeftIcon class="w-5 h-5 text-gray-600" />
            </button>
            <h1 class="text-2xl font-bold text-gray-900">关于</h1>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="space-y-8">
        <!-- 应用信息 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
          <div class="flex justify-center mb-6">
            <div class="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center">
              <MicrophoneIcon class="w-12 h-12 text-white" />
            </div>
          </div>
          
          <h2 class="text-3xl font-bold text-gray-900 mb-2">{{ appInfo.name }}</h2>
          <p class="text-lg text-gray-600 mb-4">{{ appInfo.description }}</p>
          
          <div class="flex justify-center items-center space-x-4 text-sm text-gray-500">
            <span>版本 {{ appInfo.version }}</span>
            <span>•</span>
            <span>构建 {{ appInfo.build }}</span>
          </div>
        </div>
        
        <!-- 功能特性 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-6">主要功能</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div v-for="feature in features" :key="feature.title" class="flex items-start space-x-3">
              <div class="flex-shrink-0">
                <component :is="feature.icon" class="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h4 class="font-medium text-gray-900">{{ feature.title }}</h4>
                <p class="text-sm text-gray-600">{{ feature.description }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 技术栈 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-6">技术栈</h3>
          
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div v-for="tech in technologies" :key="tech.name" class="text-center p-4 border border-gray-200 rounded-lg">
              <div class="text-2xl mb-2">{{ tech.icon }}</div>
              <h4 class="font-medium text-gray-900 text-sm">{{ tech.name }}</h4>
              <p class="text-xs text-gray-500">{{ tech.version }}</p>
            </div>
          </div>
        </div>
        
        <!-- 系统信息 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-6">系统信息</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">操作系统</span>
                <span class="text-sm text-gray-900">{{ systemInfo.os }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">浏览器</span>
                <span class="text-sm text-gray-900">{{ systemInfo.browser }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">屏幕分辨率</span>
                <span class="text-sm text-gray-900">{{ systemInfo.screen }}</span>
              </div>
            </div>
            
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">内存使用</span>
                <span class="text-sm text-gray-900">{{ systemInfo.memory }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">网络状态</span>
                <span class="text-sm text-gray-900">
                  <span :class="appStore.isOnline ? 'text-green-600' : 'text-red-600'">
                    {{ appStore.isOnline ? '在线' : '离线' }}
                  </span>
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">WebSocket</span>
                <span class="text-sm text-gray-900">
                  <span :class="wsStore.isConnected ? 'text-green-600' : 'text-red-600'">
                    {{ wsStore.isConnected ? '已连接' : '未连接' }}
                  </span>
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 更新日志 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-6">更新日志</h3>
          
          <div class="space-y-6">
            <div v-for="version in changelog" :key="version.version" class="border-l-4 border-blue-500 pl-4">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-medium text-gray-900">v{{ version.version }}</h4>
                <span class="text-sm text-gray-500">{{ formatDate(version.date) }}</span>
              </div>
              
              <div class="space-y-2">
                <template v-for="(changeList, type) in (version as ChangelogEntry).changes" :key="type">
                  <div v-if="changeList && (changeList as string[]).length > 0">
                    <h5 class="text-sm font-medium text-gray-700 capitalize">{{ getChangeTypeLabel(type as string) }}</h5>
                    <ul class="list-disc list-inside space-y-1 ml-4">
                      <li v-for="change in changeList" :key="change" class="text-sm text-gray-600">
                        {{ change }}
                      </li>
                    </ul>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 许可证和法律信息 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-6">许可证和法律信息</h3>
          
          <div class="space-y-4">
            <div>
              <h4 class="font-medium text-gray-900 mb-2">开源许可证</h4>
              <p class="text-sm text-gray-600">
                本软件基于 MIT 许可证开源，您可以自由使用、修改和分发。
              </p>
            </div>
            
            <div>
              <h4 class="font-medium text-gray-900 mb-2">第三方组件</h4>
              <div class="space-y-2">
                <div v-for="license in licenses" :key="license.name" class="flex justify-between items-center">
                  <span class="text-sm text-gray-900">{{ license.name }}</span>
                  <span class="text-sm text-gray-500">{{ license.license }}</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 class="font-medium text-gray-900 mb-2">隐私政策</h4>
              <p class="text-sm text-gray-600">
                我们重视您的隐私。所有音频数据仅在本地处理，不会上传到服务器。
                <a href="#" class="text-blue-600 hover:text-blue-800">查看完整隐私政策</a>
              </p>
            </div>
          </div>
        </div>
        
        <!-- 联系和支持 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-6">联系和支持</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 class="font-medium text-gray-900 mb-3">获取帮助</h4>
              <div class="space-y-2">
                <a href="#" class="flex items-center text-sm text-blue-600 hover:text-blue-800">
                  <DocumentTextIcon class="w-4 h-4 mr-2" />
                  用户手册
                </a>
                <a href="#" class="flex items-center text-sm text-blue-600 hover:text-blue-800">
                  <QuestionMarkCircleIcon class="w-4 h-4 mr-2" />
                  常见问题
                </a>
                <a href="#" class="flex items-center text-sm text-blue-600 hover:text-blue-800">
                  <ChatBubbleLeftRightIcon class="w-4 h-4 mr-2" />
                  在线支持
                </a>
              </div>
            </div>
            
            <div>
              <h4 class="font-medium text-gray-900 mb-3">反馈和建议</h4>
              <div class="space-y-2">
                <a href="#" class="flex items-center text-sm text-blue-600 hover:text-blue-800">
                  <BugAntIcon class="w-4 h-4 mr-2" />
                  报告问题
                </a>
                <a href="#" class="flex items-center text-sm text-blue-600 hover:text-blue-800">
                  <LightBulbIcon class="w-4 h-4 mr-2" />
                  功能建议
                </a>
                <a href="#" class="flex items-center text-sm text-blue-600 hover:text-blue-800">
                  <StarIcon class="w-4 h-4 mr-2" />
                  给我们评分
                </a>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 检查更新 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-medium text-gray-900">软件更新</h3>
              <p class="text-sm text-gray-600 mt-1">
                {{ updateStatus.checking ? '正在检查更新...' : updateStatus.message }}
              </p>
            </div>
            
            <button
              @click="checkForUpdates"
              :disabled="updateStatus.checking"
              class="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
            >
              <span v-if="updateStatus.checking" class="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></span>
              <ArrowPathIcon v-else class="w-4 h-4 mr-2" />
              {{ updateStatus.checking ? '检查中...' : '检查更新' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  ArrowLeftIcon,
  MicrophoneIcon,
  DocumentTextIcon,
  QuestionMarkCircleIcon,
  ChatBubbleLeftRightIcon,
  BugAntIcon,
  LightBulbIcon,
  StarIcon,
  ArrowPathIcon,
  SpeakerWaveIcon,
  DocumentDuplicateIcon,
  CloudIcon,
  ShieldCheckIcon,
  CpuChipIcon,
  GlobeAltIcon
} from '@heroicons/vue/24/outline'

import { useAppStore } from '@/stores/app'
import { useWebSocketStore } from '@/stores/websocket'
import { formatDate } from '@/utils'

const appStore = useAppStore()
const wsStore = useWebSocketStore()

// 应用信息
const appInfo = ref({
  name: 'FunASR 会议助手',
  description: '基于 FunASR 的实时语音转录和会议记录工具',
  version: '1.0.0',
  build: '20241201'
})

// 功能特性
const features = [
  {
    icon: SpeakerWaveIcon,
    title: '实时语音转录',
    description: '基于 FunASR Paraformer 模型的高精度实时语音识别'
  },
  {
    icon: DocumentDuplicateIcon,
    title: '会议记录',
    description: '自动记录会议内容，支持多种格式导出'
  },
  {
    icon: CloudIcon,
    title: '云端同步',
    description: '会议数据云端同步，多设备访问'
  },
  {
    icon: ShieldCheckIcon,
    title: '隐私保护',
    description: '本地处理音频数据，保护用户隐私'
  },
  {
    icon: CpuChipIcon,
    title: '高性能',
    description: '优化的算法和架构，低延迟高准确率'
  },
  {
    icon: GlobeAltIcon,
    title: '多语言支持',
    description: '支持中文、英文等多种语言识别'
  }
]

// 技术栈
const technologies = [
  { name: 'Vue.js', version: '3.3.0', icon: '🟢' },
  { name: 'TypeScript', version: '5.0.0', icon: '🔷' },
  { name: 'Vite', version: '4.4.0', icon: '⚡' },
  { name: 'Tailwind CSS', version: '3.3.0', icon: '🎨' },
  { name: 'Pinia', version: '2.1.0', icon: '🍍' },
  { name: 'FunASR', version: '1.0.0', icon: '🎤' },
  { name: 'WebSocket', version: 'Native', icon: '🔌' },
  { name: 'Web Audio API', version: 'Native', icon: '🔊' }
]

// 系统信息
const systemInfo = ref({
  os: '',
  browser: '',
  screen: '',
  memory: '',
  userAgent: ''
})

// 更新日志
interface ChangelogEntry {
  version: string
  date: string
  changes: {
    added?: string[]
    improved?: string[]
    fixed?: string[]
    removed?: string[]
  }
}

const changelog: ChangelogEntry[] = [
  {
    version: '1.0.0',
    date: '2024-12-01',
    changes: {
      added: [
        '实时语音转录功能',
        '会议记录和管理',
        '多语言支持',
        '云端同步功能'
      ],
      improved: [
        '优化用户界面设计',
        '提升转录准确率',
        '改进音频处理性能'
      ],
      fixed: [
        '修复音频设备切换问题',
        '解决WebSocket连接异常',
        '修复导出功能bug'
      ]
    }
  },
  {
    version: '0.9.0',
    date: '2024-11-15',
    changes: {
      added: [
        '基础语音转录功能',
        '会议创建和管理',
        '音频录制功能'
      ],
      improved: [
        '优化转录算法',
        '改进用户体验'
      ],
      fixed: [
        '修复音频播放问题',
        '解决数据存储异常'
      ]
    }
  }
]

// 许可证信息
const licenses = [
  { name: 'Vue.js', license: 'MIT' },
  { name: 'TypeScript', license: 'Apache-2.0' },
  { name: 'Tailwind CSS', license: 'MIT' },
  { name: 'Heroicons', license: 'MIT' },
  { name: 'Axios', license: 'MIT' },
  { name: 'Day.js', license: 'MIT' },
  { name: 'FunASR', license: 'Apache-2.0' }
]

// 更新状态
const updateStatus = ref({
  checking: false,
  message: '当前版本是最新版本'
})

// 方法
const getSystemInfo = () => {
  const ua = navigator.userAgent
  
  // 操作系统
  let os = 'Unknown'
  if (ua.includes('Windows')) os = 'Windows'
  else if (ua.includes('Mac')) os = 'macOS'
  else if (ua.includes('Linux')) os = 'Linux'
  else if (ua.includes('Android')) os = 'Android'
  else if (ua.includes('iOS')) os = 'iOS'
  
  // 浏览器
  let browser = 'Unknown'
  if (ua.includes('Chrome')) browser = 'Chrome'
  else if (ua.includes('Firefox')) browser = 'Firefox'
  else if (ua.includes('Safari')) browser = 'Safari'
  else if (ua.includes('Edge')) browser = 'Edge'
  
  // 屏幕分辨率
  const screen = `${window.screen.width} × ${window.screen.height}`
  
  // 内存信息（如果支持）
  let memory = 'Unknown'
  if ('memory' in performance) {
    const memInfo = (performance as any).memory
    const used = Math.round(memInfo.usedJSHeapSize / 1024 / 1024)
    const total = Math.round(memInfo.totalJSHeapSize / 1024 / 1024)
    memory = `${used}MB / ${total}MB`
  }
  
  systemInfo.value = {
    os,
    browser,
    screen,
    memory,
    userAgent: ua
  }
}

const getChangeTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    added: '新增功能',
    improved: '功能改进',
    fixed: '问题修复',
    removed: '移除功能'
  }
  return labels[type] || type
}

const checkForUpdates = async () => {
  try {
    updateStatus.value.checking = true
    updateStatus.value.message = '正在检查更新...'
    
    // 模拟检查更新
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 这里应该调用实际的更新检查API
    const hasUpdate = Math.random() > 0.8 // 20%概率有更新
    
    if (hasUpdate) {
      updateStatus.value.message = '发现新版本 v1.0.1，点击下载更新'
      appStore.addNotification({
        type: 'info',
        title: '发现新版本',
        message: '新版本 v1.0.1 已发布，包含性能优化和bug修复'
      })
    } else {
      updateStatus.value.message = '当前版本是最新版本'
    }
  } catch (error) {
    console.error('检查更新失败:', error)
    updateStatus.value.message = '检查更新失败，请稍后重试'
  } finally {
    updateStatus.value.checking = false
  }
}

// 生命周期
onMounted(() => {
  getSystemInfo()
})
</script>

<style scoped>
/* 自定义样式 */
</style>