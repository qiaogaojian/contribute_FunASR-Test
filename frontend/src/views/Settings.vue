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
            <h1 class="text-2xl font-bold text-gray-900">设置</h1>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="space-y-8">
        <!-- 外观设置 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-6">外观设置</h2>
          
          <div class="space-y-6">
            <!-- 主题设置 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-3">主题</label>
              <div class="grid grid-cols-3 gap-3">
                <button
                  v-for="theme in themes"
                  :key="theme.value"
                  @click="updateTheme(theme.value)"
                  :class="[
                    'p-4 border-2 rounded-lg transition-all text-left',
                    appStore.theme === theme.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  ]"
                >
                  <div class="flex items-center space-x-3">
                    <component :is="theme.icon" class="w-5 h-5 text-gray-600" />
                    <div>
                      <h3 class="font-medium text-gray-900">{{ theme.label }}</h3>
                      <p class="text-sm text-gray-500">{{ theme.description }}</p>
                    </div>
                  </div>
                </button>
              </div>
            </div>
            
            <!-- 语言设置 -->
            <div>
              <label for="language" class="block text-sm font-medium text-gray-700 mb-2">语言</label>
              <select
                id="language"
                v-model="appStore.language"
                @change="updateLanguage"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="zh">中文</option>
                <option value="en">English</option>
              </select>
            </div>
          </div>
        </div>
        
        <!-- 音频设置 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-6">音频设置</h2>
          
          <div class="space-y-6">
            <!-- 麦克风设备 -->
            <div>
              <label for="microphone" class="block text-sm font-medium text-gray-700 mb-2">麦克风设备</label>
              <select
                id="microphone"
                v-model="audioSettings.microphoneId"
                @change="updateAudioSettings"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">默认设备</option>
                <option
                  v-for="device in audioDevices.microphones"
                  :key="device.deviceId"
                  :value="device.deviceId"
                >
                  {{ device.label || `麦克风 ${device.deviceId.slice(0, 8)}` }}
                </option>
              </select>
            </div>
            
            <!-- 扬声器设备 -->
            <div>
              <label for="speaker" class="block text-sm font-medium text-gray-700 mb-2">扬声器设备</label>
              <select
                id="speaker"
                v-model="audioSettings.speakerId"
                @change="updateAudioSettings"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">默认设备</option>
                <option
                  v-for="device in audioDevices.speakers"
                  :key="device.deviceId"
                  :value="device.deviceId"
                >
                  {{ device.label || `扬声器 ${device.deviceId.slice(0, 8)}` }}
                </option>
              </select>
            </div>
            
            <!-- 音频质量 -->
            <div>
              <label for="audioQuality" class="block text-sm font-medium text-gray-700 mb-2">默认录制质量</label>
              <select
                id="audioQuality"
                v-model="audioSettings.quality"
                @change="updateAudioSettings"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="high">高质量 (48kHz, 16bit)</option>
                <option value="medium">中等质量 (44.1kHz, 16bit)</option>
                <option value="low">低质量 (22kHz, 16bit)</option>
              </select>
            </div>
            
            <!-- 噪音抑制 -->
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-medium text-gray-900">噪音抑制</h3>
                <p class="text-sm text-gray-500">自动过滤背景噪音</p>
              </div>
              <button
                type="button"
                @click="toggleNoiseSuppression"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                  audioSettings.noiseSuppression ? 'bg-blue-600' : 'bg-gray-200'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                    audioSettings.noiseSuppression ? 'translate-x-6' : 'translate-x-1'
                  ]"
                ></span>
              </button>
            </div>
            
            <!-- 音频测试 -->
            <div>
              <h3 class="text-sm font-medium text-gray-700 mb-3">音频测试</h3>
              <div class="flex items-center space-x-4">
                <button
                  @click="testMicrophone"
                  :disabled="isTesting"
                  class="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
                >
                  <MicrophoneIcon class="w-5 h-5 mr-2" />
                  {{ isTesting ? '测试中...' : '测试麦克风' }}
                </button>
                
                <div v-if="isTesting" class="flex items-center space-x-2">
                  <div class="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      class="h-full bg-green-500 transition-all duration-100"
                      :style="{ width: `${audioLevel}%` }"
                    ></div>
                  </div>
                  <span class="text-sm text-gray-600">{{ Math.round(audioLevel) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 转录设置 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-6">转录设置</h2>
          
          <div class="space-y-6">
            <!-- 默认转录语言 -->
            <div>
              <label for="transcriptLanguage" class="block text-sm font-medium text-gray-700 mb-2">默认转录语言</label>
              <select
                id="transcriptLanguage"
                v-model="transcriptSettings.language"
                @change="updateTranscriptSettings"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="zh">中文</option>
                <option value="en">英文</option>
                <option value="auto">自动检测</option>
              </select>
            </div>
            
            <!-- 实时转录 -->
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-medium text-gray-900">默认开启实时转录</h3>
                <p class="text-sm text-gray-500">新建会议时默认开启实时转录</p>
              </div>
              <button
                type="button"
                @click="toggleRealtimeTranscription"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                  transcriptSettings.realtimeTranscription ? 'bg-blue-600' : 'bg-gray-200'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                    transcriptSettings.realtimeTranscription ? 'translate-x-6' : 'translate-x-1'
                  ]"
                ></span>
              </button>
            </div>
            
            <!-- 自动总结 -->
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-medium text-gray-900">默认开启自动总结</h3>
                <p class="text-sm text-gray-500">会议结束后自动生成总结</p>
              </div>
              <button
                type="button"
                @click="toggleAutoSummary"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                  transcriptSettings.autoSummary ? 'bg-blue-600' : 'bg-gray-200'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                    transcriptSettings.autoSummary ? 'translate-x-6' : 'translate-x-1'
                  ]"
                ></span>
              </button>
            </div>
            
            <!-- 说话人识别 -->
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-medium text-gray-900">说话人识别</h3>
                <p class="text-sm text-gray-500">自动识别不同的说话人</p>
              </div>
              <button
                type="button"
                @click="toggleSpeakerDiarization"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                  transcriptSettings.speakerDiarization ? 'bg-blue-600' : 'bg-gray-200'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                    transcriptSettings.speakerDiarization ? 'translate-x-6' : 'translate-x-1'
                  ]"
                ></span>
              </button>
            </div>
          </div>
        </div>
        
        <!-- 通知设置 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-6">通知设置</h2>
          
          <div class="space-y-6">
            <!-- 桌面通知 -->
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-medium text-gray-900">桌面通知</h3>
                <p class="text-sm text-gray-500">允许显示桌面通知</p>
              </div>
              <button
                type="button"
                @click="toggleDesktopNotifications"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                  notificationSettings.desktop ? 'bg-blue-600' : 'bg-gray-200'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                    notificationSettings.desktop ? 'translate-x-6' : 'translate-x-1'
                  ]"
                ></span>
              </button>
            </div>
            
            <!-- 声音通知 -->
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-medium text-gray-900">声音通知</h3>
                <p class="text-sm text-gray-500">播放通知声音</p>
              </div>
              <button
                type="button"
                @click="toggleSoundNotifications"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                  notificationSettings.sound ? 'bg-blue-600' : 'bg-gray-200'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                    notificationSettings.sound ? 'translate-x-6' : 'translate-x-1'
                  ]"
                ></span>
              </button>
            </div>
            
            <!-- 会议提醒 -->
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-medium text-gray-900">会议提醒</h3>
                <p class="text-sm text-gray-500">会议开始前提醒</p>
              </div>
              <button
                type="button"
                @click="toggleMeetingReminders"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                  notificationSettings.meetingReminders ? 'bg-blue-600' : 'bg-gray-200'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                    notificationSettings.meetingReminders ? 'translate-x-6' : 'translate-x-1'
                  ]"
                ></span>
              </button>
            </div>
          </div>
        </div>
        
        <!-- 存储设置 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-6">存储设置</h2>
          
          <div class="space-y-6">
            <!-- 自动清理 -->
            <div>
              <label for="autoCleanup" class="block text-sm font-medium text-gray-700 mb-2">自动清理旧文件</label>
              <select
                id="autoCleanup"
                v-model="storageSettings.autoCleanupDays"
                @change="updateStorageSettings"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="0">从不清理</option>
                <option value="30">30天后</option>
                <option value="60">60天后</option>
                <option value="90">90天后</option>
                <option value="180">180天后</option>
              </select>
            </div>
            
            <!-- 存储位置 -->
            <div>
              <label for="storagePath" class="block text-sm font-medium text-gray-700 mb-2">本地存储位置</label>
              <div class="flex items-center space-x-2">
                <input
                  id="storagePath"
                  v-model="storageSettings.localPath"
                  type="text"
                  readonly
                  class="flex-1 border border-gray-300 rounded-lg px-4 py-3 bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  @click="selectStoragePath"
                  class="px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  选择
                </button>
              </div>
            </div>
            
            <!-- 存储使用情况 -->
            <div>
              <h3 class="text-sm font-medium text-gray-700 mb-3">存储使用情况</h3>
              <div class="space-y-2">
                <div class="flex justify-between text-sm">
                  <span class="text-gray-600">已使用空间</span>
                  <span class="text-gray-900">{{ formatFileSize(storageUsage.used) }}</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-blue-600 h-2 rounded-full transition-all"
                    :style="{ width: `${(storageUsage.used / storageUsage.total) * 100}%` }"
                  ></div>
                </div>
                <div class="flex justify-between text-sm text-gray-500">
                  <span>总空间: {{ formatFileSize(storageUsage.total) }}</span>
                  <span>可用: {{ formatFileSize(storageUsage.available) }}</span>
                </div>
              </div>
              
              <button
                @click="cleanupStorage"
                class="mt-4 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                清理缓存
              </button>
            </div>
          </div>
        </div>
        
        <!-- 高级设置 -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-6">高级设置</h2>
          
          <div class="space-y-6">
            <!-- 开发者模式 -->
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-medium text-gray-900">开发者模式</h3>
                <p class="text-sm text-gray-500">显示调试信息和高级选项</p>
              </div>
              <button
                type="button"
                @click="toggleDeveloperMode"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                  advancedSettings.developerMode ? 'bg-blue-600' : 'bg-gray-200'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                    advancedSettings.developerMode ? 'translate-x-6' : 'translate-x-1'
                  ]"
                ></span>
              </button>
            </div>
            
            <!-- 数据导出 -->
            <div>
              <h3 class="text-sm font-medium text-gray-700 mb-3">数据管理</h3>
              <div class="flex space-x-3">
                <button
                  @click="exportData"
                  class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  导出数据
                </button>
                <button
                  @click="importData"
                  class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  导入数据
                </button>
                <button
                  @click="resetSettings"
                  class="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                >
                  重置设置
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 保存按钮 -->
        <div class="flex justify-end">
          <button
            @click="saveSettings"
            :disabled="isSaving"
            class="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <span v-if="isSaving" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
            {{ isSaving ? '保存中...' : '保存设置' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  ArrowLeftIcon,
  SunIcon,
  MoonIcon,
  ComputerDesktopIcon,
  MicrophoneIcon
} from '@heroicons/vue/24/outline'

import { useAppStore } from '@/stores/app'
import { formatFileSize } from '@/utils'

const appStore = useAppStore()

// 主题选项
const themes = [
  {
    value: 'light' as const,
    label: '浅色',
    description: '浅色主题',
    icon: SunIcon
  },
  {
    value: 'dark' as const,
    label: '深色',
    description: '深色主题',
    icon: MoonIcon
  },
  {
    value: 'auto' as const,
    label: '跟随系统',
    description: '跟随系统设置',
    icon: ComputerDesktopIcon
  }
]

// 设置数据
const audioSettings = ref({
  microphoneId: '',
  speakerId: '',
  quality: 'high',
  noiseSuppression: true
})

const transcriptSettings = ref({
  language: 'zh',
  realtimeTranscription: true,
  autoSummary: true,
  speakerDiarization: true
})

const notificationSettings = ref({
  desktop: true,
  sound: true,
  meetingReminders: true
})

const storageSettings = ref({
  autoCleanupDays: 90,
  localPath: ''
})

const advancedSettings = ref({
  developerMode: false
})

// 状态
const isSaving = ref(false)
const isTesting = ref(false)
const audioLevel = ref(0)
const audioDevices = ref({
  microphones: [] as MediaDeviceInfo[],
  speakers: [] as MediaDeviceInfo[]
})

const storageUsage = ref({
  used: 0,
  total: 0,
  available: 0
})

// 方法
const loadSettings = () => {
  // 从本地存储加载设置
  const saved = localStorage.getItem('app_settings')
  if (saved) {
    try {
      const settings = JSON.parse(saved)
      audioSettings.value = { ...audioSettings.value, ...settings.audio }
      transcriptSettings.value = { ...transcriptSettings.value, ...settings.transcript }
      notificationSettings.value = { ...notificationSettings.value, ...settings.notification }
      storageSettings.value = { ...storageSettings.value, ...settings.storage }
      advancedSettings.value = { ...advancedSettings.value, ...settings.advanced }
    } catch (error) {
      console.error('加载设置失败:', error)
    }
  }
}

const saveSettings = async () => {
  try {
    isSaving.value = true
    
    const settings = {
      audio: audioSettings.value,
      transcript: transcriptSettings.value,
      notification: notificationSettings.value,
      storage: storageSettings.value,
      advanced: advancedSettings.value
    }
    
    localStorage.setItem('app_settings', JSON.stringify(settings))
    
    appStore.addNotification({
      type: 'success',
      title: '设置已保存',
      message: '所有设置已成功保存'
    })
  } catch (error) {
    console.error('保存设置失败:', error)
    appStore.addNotification({
      type: 'error',
      title: '保存失败',
      message: '保存设置时发生错误'
    })
  } finally {
    isSaving.value = false
  }
}

const updateTheme = (theme: 'light' | 'dark' | 'auto') => {
  appStore.setTheme(theme)
}

const updateLanguage = () => {
  // 语言更新逻辑
}

const updateAudioSettings = () => {
  // 音频设置更新逻辑
}

const updateTranscriptSettings = () => {
  // 转录设置更新逻辑
}

const updateStorageSettings = () => {
  // 存储设置更新逻辑
}

const toggleNoiseSuppression = () => {
  audioSettings.value.noiseSuppression = !audioSettings.value.noiseSuppression
  updateAudioSettings()
}

const toggleRealtimeTranscription = () => {
  transcriptSettings.value.realtimeTranscription = !transcriptSettings.value.realtimeTranscription
  updateTranscriptSettings()
}

const toggleAutoSummary = () => {
  transcriptSettings.value.autoSummary = !transcriptSettings.value.autoSummary
  updateTranscriptSettings()
}

const toggleSpeakerDiarization = () => {
  transcriptSettings.value.speakerDiarization = !transcriptSettings.value.speakerDiarization
  updateTranscriptSettings()
}

const toggleDesktopNotifications = async () => {
  if (!notificationSettings.value.desktop) {
    // 请求通知权限
    const permission = await Notification.requestPermission()
    if (permission === 'granted') {
      notificationSettings.value.desktop = true
    }
  } else {
    notificationSettings.value.desktop = false
  }
}

const toggleSoundNotifications = () => {
  notificationSettings.value.sound = !notificationSettings.value.sound
}

const toggleMeetingReminders = () => {
  notificationSettings.value.meetingReminders = !notificationSettings.value.meetingReminders
}

const toggleDeveloperMode = () => {
  advancedSettings.value.developerMode = !advancedSettings.value.developerMode
}

const loadAudioDevices = async () => {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices()
    audioDevices.value.microphones = devices.filter(device => device.kind === 'audioinput')
    audioDevices.value.speakers = devices.filter(device => device.kind === 'audiooutput')
  } catch (error) {
    console.error('获取音频设备失败:', error)
  }
}

const testMicrophone = async () => {
  try {
    isTesting.value = true
    audioLevel.value = 0
    
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        deviceId: audioSettings.value.microphoneId || undefined
      }
    })
    
    const audioContext = new AudioContext()
    const analyser = audioContext.createAnalyser()
    const microphone = audioContext.createMediaStreamSource(stream)
    const dataArray = new Uint8Array(analyser.frequencyBinCount)
    
    microphone.connect(analyser)
    analyser.fftSize = 256
    
    const updateLevel = () => {
      if (!isTesting.value) return
      
      analyser.getByteFrequencyData(dataArray)
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length
      audioLevel.value = (average / 255) * 100
      
      requestAnimationFrame(updateLevel)
    }
    
    updateLevel()
    
    // 5秒后停止测试
    setTimeout(() => {
      isTesting.value = false
      stream.getTracks().forEach(track => track.stop())
      audioContext.close()
    }, 5000)
    
  } catch (error) {
    console.error('麦克风测试失败:', error)
    isTesting.value = false
    appStore.addNotification({
      type: 'error',
      title: '测试失败',
      message: '无法访问麦克风设备'
    })
  }
}

const selectStoragePath = () => {
  // 选择存储路径（需要Electron支持）
  if (window.electronAPI) {
    window.electronAPI.selectDirectory().then((path: string) => {
      if (path) {
        storageSettings.value.localPath = path
      }
    })
  }
}

const loadStorageUsage = () => {
  // 模拟存储使用情况
  storageUsage.value = {
    used: 1024 * 1024 * 500, // 500MB
    total: 1024 * 1024 * 1024 * 10, // 10GB
    available: 1024 * 1024 * 1024 * 9.5 // 9.5GB
  }
}

const cleanupStorage = () => {
  // 清理存储
  appStore.addNotification({
    type: 'success',
    title: '清理完成',
    message: '缓存已清理'
  })
}

const exportData = () => {
  // 导出数据
  const data = {
    settings: {
      audio: audioSettings.value,
      transcript: transcriptSettings.value,
      notification: notificationSettings.value,
      storage: storageSettings.value,
      advanced: advancedSettings.value
    },
    timestamp: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `meeting-assistant-settings-${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
}

const importData = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = (e) => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target?.result as string)
          if (data.settings) {
            audioSettings.value = { ...audioSettings.value, ...data.settings.audio }
            transcriptSettings.value = { ...transcriptSettings.value, ...data.settings.transcript }
            notificationSettings.value = { ...notificationSettings.value, ...data.settings.notification }
            storageSettings.value = { ...storageSettings.value, ...data.settings.storage }
            advancedSettings.value = { ...advancedSettings.value, ...data.settings.advanced }
            
            appStore.addNotification({
              type: 'success',
              title: '导入成功',
              message: '设置已成功导入'
            })
          }
        } catch (error) {
          console.error('导入失败:', error)
          appStore.addNotification({
            type: 'error',
            title: '导入失败',
            message: '文件格式不正确'
          })
        }
      }
      reader.readAsText(file)
    }
  }
  input.click()
}

const resetSettings = () => {
  if (confirm('确定要重置所有设置吗？此操作不可恢复。')) {
    localStorage.removeItem('app_settings')
    location.reload()
  }
}

// 生命周期
onMounted(() => {
  loadSettings()
  loadAudioDevices()
  loadStorageUsage()
})
</script>

<style scoped>
/* 自定义样式 */
</style>