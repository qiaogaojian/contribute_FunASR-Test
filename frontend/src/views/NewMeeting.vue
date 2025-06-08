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
            <h1 class="text-2xl font-bold text-gray-900">新建会议</h1>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <form @submit.prevent="createMeeting" class="space-y-8">
        <!-- 基本信息 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-6">基本信息</h2>
          
          <div class="space-y-6">
            <!-- 会议标题 -->
            <div>
              <label for="title" class="block text-sm font-medium text-gray-700 mb-2">
                会议标题 <span class="text-red-500">*</span>
              </label>
              <input
                id="title"
                v-model="form.title"
                type="text"
                required
                placeholder="请输入会议标题"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-300': errors.title }"
              />
              <p v-if="errors.title" class="mt-1 text-sm text-red-600">{{ errors.title }}</p>
            </div>
            
            <!-- 会议描述 -->
            <div>
              <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
                会议描述
              </label>
              <textarea
                id="description"
                v-model="form.description"
                rows="4"
                placeholder="请输入会议描述（可选）"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              ></textarea>
            </div>
            
            <!-- 会议类型 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                会议类型
              </label>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div
                  v-for="type in meetingTypes"
                  :key="type.value"
                  @click="form.type = type.value"
                  :class="[
                    'p-4 border-2 rounded-lg cursor-pointer transition-all',
                    form.type === type.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  ]"
                >
                  <div class="flex items-center space-x-3">
                    <component :is="type.icon" class="w-6 h-6 text-gray-600" />
                    <div>
                      <h3 class="font-medium text-gray-900">{{ type.label }}</h3>
                      <p class="text-sm text-gray-500">{{ type.description }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 录制设置 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-6">录制设置</h2>
          
          <div class="space-y-6">
            <!-- 自动录制 -->
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-medium text-gray-900">自动开始录制</h3>
                <p class="text-sm text-gray-500">会议开始时自动开始录制</p>
              </div>
              <button
                type="button"
                @click="form.autoRecord = !form.autoRecord"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                  form.autoRecord ? 'bg-blue-600' : 'bg-gray-200'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                    form.autoRecord ? 'translate-x-6' : 'translate-x-1'
                  ]"
                ></span>
              </button>
            </div>
            
            <!-- 录制质量 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                录制质量
              </label>
              <select
                v-model="form.recordQuality"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="high">高质量 (48kHz, 16bit)</option>
                <option value="medium">中等质量 (44.1kHz, 16bit)</option>
                <option value="low">低质量 (22kHz, 16bit)</option>
              </select>
            </div>
            
            <!-- 转录语言 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                转录语言
              </label>
              <select
                v-model="form.language"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="zh">中文</option>
                <option value="en">英文</option>
                <option value="auto">自动检测</option>
              </select>
            </div>
          </div>
        </div>
        
        <!-- 参与者设置 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-6">参与者设置</h2>
          
          <div class="space-y-6">
            <!-- 最大参与者数量 -->
            <div>
              <label for="maxParticipants" class="block text-sm font-medium text-gray-700 mb-2">
                最大参与者数量
              </label>
              <input
                id="maxParticipants"
                v-model.number="form.maxParticipants"
                type="number"
                min="1"
                max="100"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <!-- 邀请参与者 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                邀请参与者
              </label>
              <div class="space-y-3">
                <div
                  v-for="(participant, index) in form.participants"
                  :key="index"
                  class="flex items-center space-x-3"
                >
                  <input
                    v-model="participant.name"
                    type="text"
                    placeholder="参与者姓名"
                    class="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    v-model="participant.email"
                    type="email"
                    placeholder="邮箱地址（可选）"
                    class="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    type="button"
                    @click="removeParticipant(index)"
                    class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <TrashIcon class="w-5 h-5" />
                  </button>
                </div>
                
                <button
                  type="button"
                  @click="addParticipant"
                  class="flex items-center px-4 py-2 text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
                >
                  <PlusIcon class="w-5 h-5 mr-2" />
                  添加参与者
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 高级设置 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-6">高级设置</h2>
          
          <div class="space-y-6">
            <!-- 实时转录 -->
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-medium text-gray-900">实时转录</h3>
                <p class="text-sm text-gray-500">在会议过程中显示实时转录结果</p>
              </div>
              <button
                type="button"
                @click="form.realtimeTranscription = !form.realtimeTranscription"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                  form.realtimeTranscription ? 'bg-blue-600' : 'bg-gray-200'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                    form.realtimeTranscription ? 'translate-x-6' : 'translate-x-1'
                  ]"
                ></span>
              </button>
            </div>
            
            <!-- 自动总结 -->
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-medium text-gray-900">自动生成总结</h3>
                <p class="text-sm text-gray-500">会议结束后自动生成会议总结</p>
              </div>
              <button
                type="button"
                @click="form.autoSummary = !form.autoSummary"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                  form.autoSummary ? 'bg-blue-600' : 'bg-gray-200'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                    form.autoSummary ? 'translate-x-6' : 'translate-x-1'
                  ]"
                ></span>
              </button>
            </div>
            
            <!-- 噪音抑制 -->
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-medium text-gray-900">噪音抑制</h3>
                <p class="text-sm text-gray-500">自动过滤背景噪音</p>
              </div>
              <button
                type="button"
                @click="form.noiseSuppression = !form.noiseSuppression"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                  form.noiseSuppression ? 'bg-blue-600' : 'bg-gray-200'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                    form.noiseSuppression ? 'translate-x-6' : 'translate-x-1'
                  ]"
                ></span>
              </button>
            </div>
            
            <!-- 会议密码 -->
            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                会议密码（可选）
              </label>
              <input
                id="password"
                v-model="form.password"
                type="password"
                placeholder="设置会议密码以增强安全性"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="flex items-center justify-between">
          <button
            type="button"
            @click="$router.go(-1)"
            class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            取消
          </button>
          
          <div class="flex space-x-3">
            <button
              type="button"
              @click="saveDraft"
              class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              保存草稿
            </button>
            
            <button
              type="submit"
              :disabled="isSubmitting || !isFormValid"
              class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
            >
              <span v-if="isSubmitting" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
              {{ isSubmitting ? '创建中...' : '创建会议' }}
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  ArrowLeftIcon,
  PlusIcon,
  TrashIcon,
  VideoCameraIcon,
  MicrophoneIcon,
  DocumentTextIcon
} from '@heroicons/vue/24/outline'

import { useAppStore } from '@/stores/app'
import { useMeetingStore } from '@/stores/meeting'
import { useRouter } from 'vue-router'

const appStore = useAppStore()
const meetingStore = useMeetingStore()
const router = useRouter()

// 会议类型选项
const meetingTypes = [
  {
    value: 'general',
    label: '常规会议',
    description: '适用于日常工作会议',
    icon: VideoCameraIcon
  },
  {
    value: 'interview',
    label: '面试会议',
    description: '适用于招聘面试',
    icon: MicrophoneIcon
  },
  {
    value: 'presentation',
    label: '演示会议',
    description: '适用于产品演示或培训',
    icon: DocumentTextIcon
  }
]

// 表单数据
const form = ref({
  title: '',
  description: '',
  type: 'general',
  autoRecord: true,
  recordQuality: 'high',
  language: 'zh',
  maxParticipants: 10,
  participants: [] as Array<{ name: string; email: string }>,
  realtimeTranscription: true,
  autoSummary: true,
  noiseSuppression: true,
  password: ''
})

// 表单验证错误
const errors = ref<Record<string, string>>({})

// 状态
const isSubmitting = ref(false)

// 计算属性
const isFormValid = computed(() => {
  return form.value.title.trim().length > 0
})

// 方法
const validateForm = (): boolean => {
  errors.value = {}
  
  if (!form.value.title.trim()) {
    errors.value.title = '请输入会议标题'
  }
  
  if (form.value.title.length > 100) {
    errors.value.title = '会议标题不能超过100个字符'
  }
  
  return Object.keys(errors.value).length === 0
}

const addParticipant = () => {
  form.value.participants.push({ name: '', email: '' })
}

const removeParticipant = (index: number) => {
  form.value.participants.splice(index, 1)
}

const saveDraft = () => {
  // 保存到本地存储
  localStorage.setItem('meeting_draft', JSON.stringify(form.value))
  appStore.addNotification({
    type: 'success',
    title: '草稿已保存',
    message: '会议草稿已保存到本地'
  })
}

const loadDraft = () => {
  const draft = localStorage.getItem('meeting_draft')
  if (draft) {
    try {
      const draftData = JSON.parse(draft)
      form.value = { ...form.value, ...draftData }
    } catch (error) {
      console.error('加载草稿失败:', error)
    }
  }
}

const createMeeting = async () => {
  if (!validateForm()) {
    return
  }
  
  try {
    isSubmitting.value = true
    
    // 准备会议数据
    const meetingData = {
      title: form.value.title.trim(),
      description: form.value.description.trim(),
      type: form.value.type,
      settings: {
        autoRecord: form.value.autoRecord,
        recordQuality: form.value.recordQuality,
        language: form.value.language,
        maxParticipants: form.value.maxParticipants,
        realtimeTranscription: form.value.realtimeTranscription,
        autoSummary: form.value.autoSummary,
        noiseSuppression: form.value.noiseSuppression,
        password: form.value.password
      },
      participants: form.value.participants
        .filter(p => p.name.trim())
        .map(p => p.name.trim())
    }
    
    // 创建会议
    const meeting = await meetingStore.createMeeting(meetingData)
    
    if (!meeting) {
      throw new Error('创建会议失败')
    }
    
    // 清除草稿
    localStorage.removeItem('meeting_draft')
    
    // 显示成功通知
    appStore.addNotification({
      type: 'success',
      title: '会议创建成功',
      message: `会议「${meeting.title}」已创建`
    })
    
    // 跳转到会议详情页
    router.push(`/meetings/${meeting.id}`)
    
  } catch (error) {
    console.error('创建会议失败:', error)
    appStore.addNotification({
      type: 'error',
      title: '创建失败',
      message: error instanceof Error ? error.message : '创建会议时发生错误'
    })
  } finally {
    isSubmitting.value = false
  }
}

// 生命周期
onMounted(() => {
  loadDraft()
})
</script>

<style scoped>
/* 自定义样式 */
</style>