<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 页面头部 -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-4">
            <button
              @click="$router.go(-1)"
              class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <ArrowLeftIcon class="w-5 h-5 text-gray-600" />
            </button>
            <div>
              <h1 class="text-2xl font-bold text-gray-900">{{ meeting?.title || '会议详情' }}</h1>
              <div v-if="meeting" class="flex items-center space-x-4 mt-1">
                <span :class="[
                  'px-2 py-1 text-xs font-medium rounded-full',
                  getStatusClass(meeting.status)
                ]">
                  {{ getStatusText(meeting.status) }}
                </span>
                <span class="text-sm text-gray-500">
                  {{ formatTime.datetime(meeting.created_at) }}
                </span>
              </div>
            </div>
          </div>
          
          <div v-if="meeting" class="flex items-center space-x-3">
            <!-- 会议控制按钮 -->
            <button
              v-if="meeting.status === 'waiting'"
              @click="startMeeting"
              :disabled="isStarting"
              class="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
            >
              <PlayIcon class="w-5 h-5 mr-2" />
              {{ isStarting ? '启动中...' : '开始会议' }}
            </button>
            
            <button
              v-if="meeting.status === 'recording'"
              @click="stopMeeting"
              :disabled="isStopping"
              class="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 transition-colors"
            >
              <StopIcon class="w-5 h-5 mr-2" />
              {{ isStopping ? '停止中...' : '停止会议' }}
            </button>
            
            <!-- 更多操作 -->
            <div class="relative" ref="dropdownRef">
              <button
                @click="showDropdown = !showDropdown"
                class="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <EllipsisVerticalIcon class="w-5 h-5" />
              </button>
              
              <div
                v-if="showDropdown"
                class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10"
              >
                <button
                  @click="downloadFiles"
                  class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                >
                  <ArrowDownTrayIcon class="w-4 h-4 mr-2" />
                  下载文件
                </button>
                <button
                  @click="shareMeeting"
                  class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                >
                  <ShareIcon class="w-4 h-4 mr-2" />
                  分享会议
                </button>
                <button
                  @click="editMeeting"
                  class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                >
                  <PencilIcon class="w-4 h-4 mr-2" />
                  编辑会议
                </button>
                <hr class="my-1" />
                <button
                  @click="deleteMeeting"
                  class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center"
                >
                  <TrashIcon class="w-4 h-4 mr-2" />
                  删除会议
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-500">加载中...</p>
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="text-center py-12">
        <ExclamationTriangleIcon class="w-16 h-16 text-red-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">加载失败</h3>
        <p class="text-gray-500 mb-6">{{ error }}</p>
        <button
          @click="loadMeeting"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          重试
        </button>
      </div>
      
      <!-- 会议内容 -->
      <div v-else-if="meeting" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- 主要内容区域 -->
        <div class="lg:col-span-2 space-y-6">
          <!-- 会议信息 -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-medium text-gray-900 mb-4">会议信息</h2>
            
            <div class="space-y-4">
              <div v-if="meeting.description">
                <h3 class="text-sm font-medium text-gray-700">描述</h3>
                <p class="text-gray-600 mt-1">{{ meeting.description }}</p>
              </div>
              
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <h3 class="text-sm font-medium text-gray-700">创建时间</h3>
                  <p class="text-gray-600 mt-1">{{ formatTime.datetime(meeting.created_at) }}</p>
                </div>
                
                <div v-if="meeting.start_time">
                  <h3 class="text-sm font-medium text-gray-700">开始时间</h3>
                  <p class="text-gray-600 mt-1">{{ formatTime.datetime(meeting.start_time) }}</p>
                </div>
                
                <div v-if="meeting.end_time">
                  <h3 class="text-sm font-medium text-gray-700">结束时间</h3>
                  <p class="text-gray-600 mt-1">{{ formatTime.datetime(meeting.end_time) }}</p>
                </div>
                
                <div v-if="meeting.duration">
                  <h3 class="text-sm font-medium text-gray-700">会议时长</h3>
                  <p class="text-gray-600 mt-1">{{ formatTime.duration(meeting.duration) }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 实时转录 -->
          <div v-if="meeting.status === 'recording'" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-medium text-gray-900">实时转录</h2>
              <div class="flex items-center space-x-2">
                <div class="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                <span class="text-sm text-red-600">录制中</span>
              </div>
            </div>
            
            <div class="space-y-3 max-h-96 overflow-y-auto">
              <div
                v-for="transcript in realtimeTranscripts"
                :key="transcript.id"
                class="p-3 bg-gray-50 rounded-lg"
              >
                <div class="flex items-center justify-between mb-1">
                  <span class="text-sm font-medium text-gray-700">{{ transcript.speaker || '未知发言人' }}</span>
                  <span class="text-xs text-gray-500">{{ formatTime.time(transcript.timestamp) }}</span>
                </div>
                <p class="text-gray-800">{{ transcript.text }}</p>
              </div>
              
              <div v-if="realtimeTranscripts.length === 0" class="text-center py-8 text-gray-500">
                等待转录内容...
              </div>
            </div>
          </div>
          
          <!-- 转录记录 -->
          <div v-if="meeting.status === 'completed'" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-medium text-gray-900">转录记录</h2>
              <div class="flex space-x-2">
                <button
                  @click="exportTranscript('txt')"
                  class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                >
                  导出TXT
                </button>
                <button
                  @click="exportTranscript('json')"
                  class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                >
                  导出JSON
                </button>
              </div>
            </div>
            
            <div v-if="transcripts.length > 0" class="space-y-3 max-h-96 overflow-y-auto">
              <div
                v-for="transcript in transcripts"
                :key="transcript.id"
                class="p-3 border border-gray-200 rounded-lg"
              >
                <div class="flex items-center justify-between mb-1">
                  <span class="text-sm font-medium text-gray-700">{{ transcript.speaker || '未知发言人' }}</span>
                  <span class="text-xs text-gray-500">{{ formatTime.time(transcript.timestamp) }}</span>
                </div>
                <p class="text-gray-800">{{ transcript.text }}</p>
              </div>
            </div>
            
            <div v-else class="text-center py-8 text-gray-500">
              暂无转录记录
            </div>
          </div>
          
          <!-- 会议总结 -->
          <div v-if="meeting.status === 'completed' && summary" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-medium text-gray-900">会议总结</h2>
              <button
                @click="exportSummary"
                class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 transition-colors"
              >
                导出总结
              </button>
            </div>
            
            <div class="prose max-w-none">
              <div v-if="summary.key_points?.length" class="mb-4">
                <h3 class="text-sm font-medium text-gray-700 mb-2">关键要点</h3>
                <ul class="list-disc list-inside space-y-1">
                  <li v-for="point in summary.key_points" :key="point" class="text-gray-600">{{ point }}</li>
                </ul>
              </div>
              
              <div v-if="summary.action_items?.length" class="mb-4">
                <h3 class="text-sm font-medium text-gray-700 mb-2">行动项</h3>
                <ul class="list-disc list-inside space-y-1">
                  <li v-for="item in summary.action_items" :key="item" class="text-gray-600">{{ item }}</li>
                </ul>
              </div>
              
              <div v-if="summary.summary">
                <h3 class="text-sm font-medium text-gray-700 mb-2">总结</h3>
                <p class="text-gray-600">{{ summary.summary }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 侧边栏 -->
        <div class="space-y-6">
          <!-- 参与者 -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-medium text-gray-900 mb-4">参与者 ({{ meeting.participants.length }})</h2>
            
            <div class="space-y-3">
              <div
                v-for="participant in meeting.participants"
                :key="participant"
                class="flex items-center space-x-3"
              >
                <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span class="text-sm font-medium text-blue-600">{{ participant.charAt(0).toUpperCase() }}</span>
                </div>
                <span class="text-gray-700">{{ participant }}</span>
              </div>
            </div>
          </div>
          
          <!-- 会议设置 -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-medium text-gray-900 mb-4">会议设置</h2>
            
            <div class="space-y-3 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">录制质量</span>
                <span class="text-gray-900">{{ getQualityText(meeting.settings?.recordQuality) }}</span>
              </div>
              
              <div class="flex justify-between">
                <span class="text-gray-600">转录语言</span>
                <span class="text-gray-900">{{ getLanguageText(meeting.settings?.language) }}</span>
              </div>
              
              <div class="flex justify-between">
                <span class="text-gray-600">实时转录</span>
                <span class="text-gray-900">{{ meeting.settings?.realtimeTranscription ? '开启' : '关闭' }}</span>
              </div>
              
              <div class="flex justify-between">
                <span class="text-gray-600">自动总结</span>
                <span class="text-gray-900">{{ meeting.settings?.autoSummary ? '开启' : '关闭' }}</span>
              </div>
              
              <div class="flex justify-between">
                <span class="text-gray-600">噪音抑制</span>
                <span class="text-gray-900">{{ meeting.settings?.noiseSuppression ? '开启' : '关闭' }}</span>
              </div>
            </div>
          </div>
          
          <!-- 快速操作 -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-medium text-gray-900 mb-4">快速操作</h2>
            
            <div class="space-y-2">
              <button
                @click="copyMeetingLink"
                class="w-full flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
              >
                <LinkIcon class="w-4 h-4 mr-2" />
                复制会议链接
              </button>
              
              <button
                v-if="meeting.status === 'completed'"
                @click="downloadAll"
                class="w-full flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
              >
                <ArrowDownTrayIcon class="w-4 h-4 mr-2" />
                下载所有文件
              </button>
              
              <button
                @click="generateReport"
                class="w-full flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
              >
                <DocumentTextIcon class="w-4 h-4 mr-2" />
                生成报告
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeftIcon,
  PlayIcon,
  StopIcon,
  EllipsisVerticalIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  PencilIcon,
  TrashIcon,
  ExclamationTriangleIcon,
  UsersIcon,
  LinkIcon,
  DocumentTextIcon
} from '@heroicons/vue/24/outline'

import { useAppStore } from '@/stores/app'
import { useMeetingStore } from '@/stores/meeting'
import { useWebSocketStore } from '@/stores/websocket'
import { formatTime } from '@/utils'
import type { Meeting, Transcript, Summary } from '@/stores/meeting'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const meetingStore = useMeetingStore()
const wsStore = useWebSocketStore()

// 响应式数据
const meeting = ref<Meeting | null>(null)
const transcripts = ref<Transcript[]>([])
const realtimeTranscripts = ref<Transcript[]>([])
const summary = ref<Summary | null>(null)
const isLoading = ref(false)
const error = ref('')
const isStarting = ref(false)
const isStopping = ref(false)
const showDropdown = ref(false)
const dropdownRef = ref<HTMLElement>()

// 计算属性
const meetingId = computed(() => route.params.id as string)

// 方法
const loadMeeting = async () => {
  try {
    isLoading.value = true
    error.value = ''
    
    // 获取会议详情
    await meetingStore.fetchMeeting(meetingId.value)
    meeting.value = meetingStore.currentMeeting
    
    // 如果会议已完成，获取转录记录和总结
    if (meeting.value?.status === 'completed') {
      try {
        await meetingStore.fetchTranscripts(meetingId.value)
        transcripts.value = meetingStore.transcripts
      } catch (err) {
        console.warn('获取转录记录失败:', err)
      }
      
      try {
        await meetingStore.fetchSummary(meetingId.value)
        summary.value = meetingStore.summary
      } catch (err) {
        console.warn('获取会议总结失败:', err)
      }
    }
    
    // 如果会议正在录制，连接WebSocket获取实时转录
    if (meeting.value?.status === 'recording') {
      await wsStore.joinMeeting(meetingId.value)
    }
    
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载会议详情失败'
    console.error('加载会议详情失败:', err)
  } finally {
    isLoading.value = false
  }
}

const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    waiting: '等待中',
    recording: '录制中',
    completed: '已完成'
  }
  return statusMap[status] || status
}

const getStatusClass = (status: string): string => {
  const classMap: Record<string, string> = {
    waiting: 'bg-yellow-100 text-yellow-800',
    recording: 'bg-green-100 text-green-800',
    completed: 'bg-blue-100 text-blue-800'
  }
  return classMap[status] || 'bg-gray-100 text-gray-800'
}

const getQualityText = (quality?: string): string => {
  const qualityMap: Record<string, string> = {
    high: '高质量',
    medium: '中等质量',
    low: '低质量'
  }
  return qualityMap[quality || 'high'] || '高质量'
}

const getLanguageText = (language?: string): string => {
  const languageMap: Record<string, string> = {
    zh: '中文',
    en: '英文',
    auto: '自动检测'
  }
  return languageMap[language || 'zh'] || '中文'
}

const startMeeting = async () => {
  if (!meeting.value) return
  
  try {
    isStarting.value = true
    await meetingStore.startMeeting(meeting.value.id)
    meeting.value.status = 'recording'
    meeting.value.start_time = new Date().toISOString()
    
    // 连接WebSocket
    await wsStore.joinMeeting(meeting.value.id)
    
    appStore.addNotification({
      type: 'success',
      title: '会议已开始',
      message: '会议录制已开始'
    })
  } catch (err) {
    console.error('开始会议失败:', err)
    appStore.addNotification({
      type: 'error',
      title: '开始失败',
      message: err instanceof Error ? err.message : '开始会议失败'
    })
  } finally {
    isStarting.value = false
  }
}

const stopMeeting = async () => {
  if (!meeting.value) return
  
  try {
    isStopping.value = true
    await meetingStore.endMeeting(meeting.value.id)
    meeting.value.status = 'completed'
    meeting.value.end_time = new Date().toISOString()
    
    // 断开WebSocket
    await wsStore.leaveMeeting()
    
    // 重新加载数据获取转录记录和总结
    await loadMeeting()
    
    appStore.addNotification({
      type: 'success',
      title: '会议已结束',
      message: '会议录制已停止，正在生成转录记录和总结'
    })
  } catch (err) {
    console.error('停止会议失败:', err)
    appStore.addNotification({
      type: 'error',
      title: '停止失败',
      message: err instanceof Error ? err.message : '停止会议失败'
    })
  } finally {
    isStopping.value = false
  }
}

const downloadFiles = () => {
  showDropdown.value = false
  // 显示下载选项模态框
  appStore.addModal({
    title: '下载文件',
    component: 'DownloadModal',
    props: { meetingId: meetingId.value }
  })
}

const shareMeeting = async () => {
  showDropdown.value = false
  const url = `${window.location.origin}/meetings/${meetingId.value}`
  
  try {
    await navigator.clipboard.writeText(url)
    appStore.addNotification({
      type: 'success',
      title: '链接已复制',
      message: '会议链接已复制到剪贴板'
    })
  } catch (err) {
    console.error('复制链接失败:', err)
  }
}

const editMeeting = () => {
  showDropdown.value = false
  router.push(`/meetings/${meetingId.value}/edit`)
}

const deleteMeeting = async () => {
  showDropdown.value = false
  
  if (!confirm('确定要删除这个会议吗？此操作不可恢复。')) {
    return
  }
  
  try {
    await meetingStore.deleteMeeting(meetingId.value)
    appStore.addNotification({
      type: 'success',
      title: '会议已删除',
      message: '会议已成功删除'
    })
    router.push('/meetings')
  } catch (err) {
    console.error('删除会议失败:', err)
    appStore.addNotification({
      type: 'error',
      title: '删除失败',
      message: err instanceof Error ? err.message : '删除会议失败'
    })
  }
}

const exportTranscript = async (format: 'txt' | 'json') => {
  try {
    await meetingStore.downloadFile(meetingId.value, format === 'txt' ? 'transcript_text' : 'transcript')
  } catch (err) {
    console.error('导出转录失败:', err)
  }
}

const exportSummary = async () => {
  try {
    await meetingStore.downloadFile(meetingId.value, 'summary')
  } catch (err) {
    console.error('导出总结失败:', err)
  }
}

const copyMeetingLink = async () => {
  const url = `${window.location.origin}/meetings/${meetingId.value}`
  
  try {
    await navigator.clipboard.writeText(url)
    appStore.addNotification({
      type: 'success',
      title: '链接已复制',
      message: '会议链接已复制到剪贴板'
    })
  } catch (err) {
    console.error('复制链接失败:', err)
  }
}

const downloadAll = async () => {
  try {
    const files = ['transcript', 'transcript_text', 'summary', 'audio']
    for (const file of files) {
      try {
        await meetingStore.downloadFile(meetingId.value, file as 'audio' | 'transcript' | 'transcript_text' | 'summary')
      } catch (err) {
        console.warn(`下载 ${file} 失败:`, err)
      }
    }
  } catch (err) {
    console.error('批量下载失败:', err)
  }
}

const generateReport = () => {
  // 生成会议报告
  appStore.addModal({
    title: '生成会议报告',
    component: 'ReportModal',
    props: { meetingId: meetingId.value }
  })
}

// 处理实时转录
const handleRealtimeTranscript = (transcript: Transcript) => {
  realtimeTranscripts.value.push(transcript)
  // 保持最新的50条记录
  if (realtimeTranscripts.value.length > 50) {
    realtimeTranscripts.value = realtimeTranscripts.value.slice(-50)
  }
}

// 点击外部关闭下拉菜单
const handleClickOutside = (event: Event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    showDropdown.value = false
  }
}

// 生命周期
onMounted(() => {
  loadMeeting()
  document.addEventListener('click', handleClickOutside)
  
  // 监听WebSocket连接状态
  watch(() => wsStore.isConnected, (connected: boolean) => {
    if (connected && meetingId.value) {
      wsStore.joinMeeting(meetingId.value)
    }
  })
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  // 如果正在录制，离开会议
  if (meeting.value?.status === 'recording') {
    wsStore.leaveMeeting()
  }
})
</script>

<style scoped>
.prose {
  max-width: none;
}

.prose h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.prose ul {
  margin-top: 0.5rem;
  margin-bottom: 1rem;
}

.prose p {
  margin-top: 0.5rem;
  margin-bottom: 0;
}
</style>