<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <!-- 导航栏 -->
    <nav class="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
              <MicrophoneIcon class="w-5 h-5 text-white" />
            </div>
            <h1 class="text-xl font-bold text-gray-900">智能会议助手</h1>
          </div>
          
          <div class="flex items-center space-x-4">
            <!-- 在线状态 -->
            <div class="flex items-center space-x-2">
              <div :class="[
                'w-2 h-2 rounded-full',
                appStore.isOnline ? 'bg-green-500' : 'bg-red-500'
              ]"></div>
              <span class="text-sm text-gray-600">
                {{ appStore.isOnline ? '在线' : '离线' }}
              </span>
            </div>
            
            <!-- 主题切换 -->
            <button
              @click="toggleTheme"
              class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <SunIcon v-if="appStore.theme === 'dark'" class="w-5 h-5 text-gray-600" />
              <MoonIcon v-else class="w-5 h-5 text-gray-600" />
            </button>
            
            <!-- 设置 -->
            <router-link
              to="/settings"
              class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <CogIcon class="w-5 h-5 text-gray-600" />
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主要内容 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 欢迎区域 -->
      <div class="text-center mb-12">
        <h2 class="text-4xl font-bold text-gray-900 mb-4">
          欢迎使用智能会议助手
        </h2>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto">
          基于先进的语音识别技术，为您提供实时转录、智能总结和会议管理服务
        </p>
      </div>

      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">总会议数</p>
              <p class="text-3xl font-bold text-gray-900">{{ stats.totalMeetings }}</p>
            </div>
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <CalendarIcon class="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">进行中</p>
              <p class="text-3xl font-bold text-green-600">{{ stats.activeMeetings }}</p>
            </div>
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <PlayIcon class="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">总时长</p>
              <p class="text-3xl font-bold text-purple-600">{{ formatTime.duration(stats.totalDuration) }}</p>
            </div>
            <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <ClockIcon class="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      <!-- 快速操作 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
        <!-- 新建会议 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <div class="text-center">
            <div class="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <PlusIcon class="w-8 h-8 text-white" />
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-2">创建新会议</h3>
            <p class="text-gray-600 mb-6">开始一个新的会议录制和转录</p>
            <router-link
              to="/meetings/new"
              class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-medium rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all duration-200 transform hover:scale-105"
            >
              <PlusIcon class="w-5 h-5 mr-2" />
              创建会议
            </router-link>
          </div>
        </div>
        
        <!-- 会议列表 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <div class="text-center">
            <div class="w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <DocumentTextIcon class="w-8 h-8 text-white" />
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-2">查看会议</h3>
            <p class="text-gray-600 mb-6">浏览和管理您的会议记录</p>
            <router-link
              to="/meetings"
              class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-medium rounded-lg hover:from-green-600 hover:to-emerald-700 transition-all duration-200 transform hover:scale-105"
            >
              <DocumentTextIcon class="w-5 h-5 mr-2" />
              查看会议
            </router-link>
          </div>
        </div>
      </div>

      <!-- 最近会议 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">最近会议</h3>
            <router-link
              to="/meetings"
              class="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              查看全部
            </router-link>
          </div>
        </div>
        
        <div v-if="isLoading" class="p-8 text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p class="text-gray-500 mt-2">加载中...</p>
        </div>
        
        <div v-else-if="recentMeetings.length === 0" class="p-8 text-center">
          <CalendarIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p class="text-gray-500">暂无会议记录</p>
          <router-link
            to="/meetings/new"
            class="text-blue-600 hover:text-blue-700 text-sm font-medium mt-2 inline-block"
          >
            创建第一个会议
          </router-link>
        </div>
        
        <div v-else class="divide-y divide-gray-200">
          <div
            v-for="meeting in recentMeetings"
            :key="meeting.id"
            class="p-6 hover:bg-gray-50 transition-colors cursor-pointer"
            @click="$router.push(`/meetings/${meeting.id}`)"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-3">
                  <h4 class="text-lg font-medium text-gray-900">{{ meeting.title }}</h4>
                  <span :class="[
                    'px-2 py-1 text-xs font-medium rounded-full',
                    meeting.status === 'recording' ? 'bg-green-100 text-green-800' :
                    meeting.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  ]">
                    {{ getStatusText(meeting.status) }}
                  </span>
                </div>
                <p v-if="meeting.description" class="text-gray-600 mt-1">{{ meeting.description }}</p>
                <div class="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                  <span class="flex items-center">
                    <CalendarIcon class="w-4 h-4 mr-1" />
                    {{ formatTime.datetime(meeting.created_at, 'MM-DD HH:mm') }}
                  </span>
                  <span v-if="meeting.duration" class="flex items-center">
                    <ClockIcon class="w-4 h-4 mr-1" />
                    {{ formatTime.duration(meeting.duration) }}
                  </span>
                  <span class="flex items-center">
                    <UsersIcon class="w-4 h-4 mr-1" />
                    {{ meeting.participants.length }} 人
                  </span>
                </div>
              </div>
              
              <div class="flex items-center space-x-2">
                <button
                  v-if="meeting.status === 'recording'"
                  @click.stop="stopMeeting(meeting.id)"
                  class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="停止会议"
                >
                  <StopIcon class="w-5 h-5" />
                </button>
                
                <ChevronRightIcon class="w-5 h-5 text-gray-400" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="bg-white border-t border-gray-200 mt-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="text-center text-gray-500">
          <p>&copy; 2024 智能会议助手. 基于 FunASR 技术驱动</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  MicrophoneIcon,
  CalendarIcon,
  PlayIcon,
  ClockIcon,
  PlusIcon,
  DocumentTextIcon,
  UsersIcon,
  ChevronRightIcon,
  StopIcon,
  SunIcon,
  MoonIcon,
  CogIcon
} from '@heroicons/vue/24/outline'

import { useAppStore } from '@/stores/app'
import { useMeetingStore } from '@/stores/meeting'
import { formatTime } from '@/utils'
import type { Meeting } from '@/stores/meeting'

const router = useRouter()
const appStore = useAppStore()
const meetingStore = useMeetingStore()

// 响应式数据
const isLoading = ref(false)

// 计算属性
const recentMeetings = computed(() => {
  return meetingStore.meetings
    .slice(0, 5)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
})

const stats = computed(() => {
  const meetings = meetingStore.meetings
  return {
    totalMeetings: meetings.length,
    activeMeetings: meetings.filter(m => m.status === 'recording').length,
    totalDuration: meetings.reduce((total, meeting) => total + (meeting.duration || 0), 0)
  }
})

// 方法
const loadData = async () => {
  try {
    isLoading.value = true
    await meetingStore.fetchMeetings(10, 0)
  } catch (error) {
    console.error('加载数据失败:', error)
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

const stopMeeting = async (meetingId: string) => {
  try {
    await meetingStore.endMeeting(meetingId)
  } catch (error) {
    console.error('停止会议失败:', error)
  }
}

const toggleTheme = () => {
  const newTheme = appStore.theme === 'light' ? 'dark' : 'light'
  appStore.setTheme(newTheme)
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
/* 自定义样式 */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>