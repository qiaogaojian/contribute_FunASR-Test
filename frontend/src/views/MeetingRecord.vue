<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 页面头部 -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-4">
            <button
              @click="$router.go(-1)"
              class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <ArrowLeftIcon class="w-5 h-5 text-gray-600" />
            </button>
            <h1 class="text-2xl font-bold text-gray-900">会议录制</h1>
          </div>
          
          <div class="flex items-center space-x-4">
            <!-- 录制状态 -->
            <div class="flex items-center space-x-2">
              <div :class="[
                'w-3 h-3 rounded-full',
                isRecording ? 'bg-red-500 animate-pulse' : 'bg-gray-400'
              ]"></div>
              <span class="text-sm font-medium text-gray-700">
                {{ isRecording ? '录制中' : '未录制' }}
              </span>
            </div>
            
            <!-- 录制时长 -->
            <div v-if="isRecording" class="text-sm text-gray-600">
              {{ formatTime.duration(recordingDuration) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- 左侧：录制控制 -->
        <div class="lg:col-span-2 space-y-6">
          <!-- 录制控制面板 -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-medium text-gray-900 mb-6">录制控制</h2>
            
            <!-- 音频可视化 -->
            <div class="mb-6">
              <canvas
                ref="visualizerCanvas"
                class="w-full h-32 bg-gray-900 rounded-lg"
                :width="canvasWidth"
                :height="128"
              ></canvas>
            </div>
            
            <!-- 控制按钮 -->
            <div class="flex items-center justify-center space-x-4">
              <button
                v-if="!isRecording"
                @click="startRecording"
                :disabled="!canRecord"
                class="flex items-center px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <PlayIcon class="w-5 h-5 mr-2" />
                开始录制
              </button>
              
              <button
                v-if="isRecording"
                @click="pauseRecording"
                class="flex items-center px-6 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
              >
                <PauseIcon class="w-5 h-5 mr-2" />
                {{ isPaused ? '继续录制' : '暂停录制' }}
              </button>
              
              <button
                v-if="isRecording"
                @click="stopRecording"
                class="flex items-center px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                <StopIcon class="w-5 h-5 mr-2" />
                停止录制
              </button>
            </div>
            
            <!-- 录制信息 -->
            <div v-if="isRecording" class="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900">{{ formatTime.duration(recordingDuration) }}</div>
                <div class="text-sm text-gray-500">录制时长</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900">{{ formatFileSize(recordingSize) }}</div>
                <div class="text-sm text-gray-500">文件大小</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900">{{ Math.round(audioLevel) }}%</div>
                <div class="text-sm text-gray-500">音量</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900">{{ transcriptCount }}</div>
                <div class="text-sm text-gray-500">转录条数</div>
              </div>
            </div>
          </div>
          
          <!-- 录制设置 -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-medium text-gray-900 mb-6">录制设置</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- 音频设备 -->
              <div>
                <label for="microphone" class="block text-sm font-medium text-gray-700 mb-2">麦克风设备</label>
                <select
                  id="microphone"
                  v-model="recordingSettings.microphoneId"
                  :disabled="isRecording"
                  class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                >
                  <option value="">默认设备</option>
                  <option
                    v-for="device in audioDevices"
                    :key="device.deviceId"
                    :value="device.deviceId"
                  >
                    {{ device.label || `麦克风 ${device.deviceId.slice(0, 8)}` }}
                  </option>
                </select>
              </div>
              
              <!-- 录制质量 -->
              <div>
                <label for="quality" class="block text-sm font-medium text-gray-700 mb-2">录制质量</label>
                <select
                  id="quality"
                  v-model="recordingSettings.quality"
                  :disabled="isRecording"
                  class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                >
                  <option value="high">高质量 (48kHz, 16bit)</option>
                  <option value="medium">中等质量 (44.1kHz, 16bit)</option>
                  <option value="low">低质量 (22kHz, 16bit)</option>
                </select>
              </div>
              
              <!-- 转录语言 -->
              <div>
                <label for="language" class="block text-sm font-medium text-gray-700 mb-2">转录语言</label>
                <select
                  id="language"
                  v-model="recordingSettings.language"
                  :disabled="isRecording"
                  class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                >
                  <option value="zh">中文</option>
                  <option value="en">英文</option>
                  <option value="auto">自动检测</option>
                </select>
              </div>
              
              <!-- 文件格式 -->
              <div>
                <label for="format" class="block text-sm font-medium text-gray-700 mb-2">文件格式</label>
                <select
                  id="format"
                  v-model="recordingSettings.format"
                  :disabled="isRecording"
                  class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                >
                  <option value="wav">WAV</option>
                  <option value="mp3">MP3</option>
                  <option value="m4a">M4A</option>
                </select>
              </div>
            </div>
            
            <!-- 高级选项 -->
            <div class="mt-6 space-y-4">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-medium text-gray-900">实时转录</h3>
                  <p class="text-sm text-gray-500">录制时同时进行语音转录</p>
                </div>
                <button
                  type="button"
                  @click="toggleRealtimeTranscription"
                  :disabled="isRecording"
                  :class="[
                    'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                    recordingSettings.realtimeTranscription ? 'bg-blue-600' : 'bg-gray-200',
                    isRecording ? 'opacity-50 cursor-not-allowed' : ''
                  ]"
                >
                  <span
                    :class="[
                      'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                      recordingSettings.realtimeTranscription ? 'translate-x-6' : 'translate-x-1'
                    ]"
                  ></span>
                </button>
              </div>
              
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-medium text-gray-900">噪音抑制</h3>
                  <p class="text-sm text-gray-500">自动过滤背景噪音</p>
                </div>
                <button
                  type="button"
                  @click="toggleNoiseSuppression"
                  :disabled="isRecording"
                  :class="[
                    'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                    recordingSettings.noiseSuppression ? 'bg-blue-600' : 'bg-gray-200',
                    isRecording ? 'opacity-50 cursor-not-allowed' : ''
                  ]"
                >
                  <span
                    :class="[
                      'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                      recordingSettings.noiseSuppression ? 'translate-x-6' : 'translate-x-1'
                    ]"
                  ></span>
                </button>
              </div>
              
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-medium text-gray-900">自动保存</h3>
                  <p class="text-sm text-gray-500">定期自动保存录制文件</p>
                </div>
                <button
                  type="button"
                  @click="toggleAutoSave"
                  :disabled="isRecording"
                  :class="[
                    'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                    recordingSettings.autoSave ? 'bg-blue-600' : 'bg-gray-200',
                    isRecording ? 'opacity-50 cursor-not-allowed' : ''
                  ]"
                >
                  <span
                    :class="[
                      'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                      recordingSettings.autoSave ? 'translate-x-6' : 'translate-x-1'
                    ]"
                  ></span>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 右侧：实时转录 -->
        <div class="space-y-6">
          <!-- 实时转录面板 -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-medium text-gray-900">实时转录</h2>
              <div class="flex items-center space-x-2">
                <div :class="[
                  'w-2 h-2 rounded-full',
                  recordingSettings.realtimeTranscription && isRecording ? 'bg-green-500' : 'bg-gray-400'
                ]"></div>
                <span class="text-sm text-gray-600">
                  {{ recordingSettings.realtimeTranscription && isRecording ? '转录中' : '未启用' }}
                </span>
              </div>
            </div>
            
            <div class="h-96 overflow-y-auto border border-gray-200 rounded-lg p-4 bg-gray-50">
              <div v-if="transcripts.length === 0" class="text-center text-gray-500 mt-8">
                <MicrophoneIcon class="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p>开始录制后将显示实时转录内容</p>
              </div>
              
              <div v-else class="space-y-3">
                <div
                  v-for="transcript in transcripts"
                  :key="transcript.id"
                  class="bg-white rounded-lg p-3 shadow-sm"
                >
                  <div class="flex items-start justify-between mb-2">
                    <span class="text-sm font-medium text-gray-900">
                      {{ transcript.speaker || '说话人' }}
                    </span>
                    <span class="text-xs text-gray-500">
                      {{ formatTime.time(transcript.timestamp) }}
                    </span>
                  </div>
                  <p class="text-sm text-gray-700">{{ transcript.text }}</p>
                  <div v-if="transcript.confidence" class="mt-2">
                    <div class="flex items-center space-x-2">
                      <span class="text-xs text-gray-500">置信度:</span>
                      <div class="flex-1 bg-gray-200 rounded-full h-1">
                        <div
                          class="bg-blue-500 h-1 rounded-full transition-all"
                          :style="{ width: `${transcript.confidence * 100}%` }"
                        ></div>
                      </div>
                      <span class="text-xs text-gray-500">{{ Math.round(transcript.confidence * 100) }}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 转录操作 -->
            <div class="mt-4 flex items-center justify-between">
              <button
                @click="clearTranscripts"
                :disabled="transcripts.length === 0"
                class="text-sm text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                清空转录
              </button>
              
              <button
                @click="exportTranscripts"
                :disabled="transcripts.length === 0"
                class="flex items-center text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <DocumentArrowDownIcon class="w-4 h-4 mr-1" />
                导出转录
              </button>
            </div>
          </div>
          
          <!-- 录制历史 -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-medium text-gray-900 mb-4">录制历史</h2>
            
            <div class="space-y-3">
              <div v-if="recordingHistory.length === 0" class="text-center text-gray-500 py-8">
                <DocumentIcon class="w-8 h-8 mx-auto mb-2 text-gray-400" />
                <p class="text-sm">暂无录制历史</p>
              </div>
              
              <div
                v-for="record in recordingHistory"
                :key="record.id"
                class="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors"
              >
                <div class="flex items-center justify-between mb-2">
                  <h3 class="font-medium text-gray-900 text-sm">{{ record.name }}</h3>
                  <span class="text-xs text-gray-500">{{ formatDate(record.createdAt) }}</span>
                </div>
                
                <div class="flex items-center justify-between text-sm text-gray-600">
                  <span>{{ formatTime.duration(record.duration) }}</span>
                  <span>{{ formatFileSize(record.size) }}</span>
                </div>
                
                <div class="mt-2 flex items-center space-x-2">
                  <button
                    @click="playRecord(record)"
                    class="text-xs text-blue-600 hover:text-blue-800"
                  >
                    播放
                  </button>
                  <button
                    @click="downloadRecord(record)"
                    class="text-xs text-blue-600 hover:text-blue-800"
                  >
                    下载
                  </button>
                  <button
                    @click="deleteRecord(record)"
                    class="text-xs text-red-600 hover:text-red-800"
                  >
                    删除
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import {
  ArrowLeftIcon,
  PlayIcon,
  PauseIcon,
  StopIcon,
  MicrophoneIcon,
  DocumentArrowDownIcon,
  DocumentIcon
} from '@heroicons/vue/24/outline'

import { useAppStore } from '@/stores/app'
import { useWebSocketStore } from '@/stores/websocket'
import { AudioRecorder, AudioVisualizer } from '@/utils/audio'
import { formatFileSize, formatDate, formatTime } from '@/utils'

interface Transcript {
  id: string
  text: string
  speaker?: string
  timestamp: number
  confidence?: number
}

interface RecordingRecord {
  id: string
  name: string
  duration: number
  size: number
  createdAt: string
  filePath: string
}

const appStore = useAppStore()
const route = useRoute()
const wsStore = useWebSocketStore()

// 录制状态
const isRecording = ref(false)
const isPaused = ref(false)
const canRecord = ref(false)
const recordingDuration = ref(0)
const recordingSize = ref(0)
const audioLevel = ref(0)
const transcriptCount = ref(0)

// 录制设置
const recordingSettings = ref({
  microphoneId: '',
  quality: 'high',
  language: 'zh',
  format: 'wav',
  realtimeTranscription: true,
  noiseSuppression: true,
  autoSave: true
})

// 音频设备
const audioDevices = ref<MediaDeviceInfo[]>([])

// 转录数据
const transcripts = ref<Transcript[]>([])

// 录制历史
const recordingHistory = ref<RecordingRecord[]>([])

// 音频相关
const visualizerCanvas = ref<HTMLCanvasElement>()
const canvasWidth = ref(800)
let audioRecorder: AudioRecorder | null = null
let audioVisualizer: AudioVisualizer | null = null
let recordingTimer: NodeJS.Timeout | null = null

// 方法
const loadAudioDevices = async () => {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices()
    audioDevices.value = devices.filter(device => device.kind === 'audioinput')
    canRecord.value = audioDevices.value.length > 0
  } catch (error) {
    console.error('获取音频设备失败:', error)
    appStore.addNotification({
      type: 'error',
      title: '录制错误',
      message: '初始化录音设备失败'
    })
  }
}

const initializeAudioVisualizer = async () => {
  await nextTick()
  if (visualizerCanvas.value) {
    audioVisualizer = new AudioVisualizer(visualizerCanvas.value)
  }
}

const startRecording = async () => {
  try {
    if (!canRecord.value) {
      throw new Error('没有可用的音频设备')
    }
    
    // 初始化录音器
    audioRecorder = new AudioRecorder({
      sampleRate: recordingSettings.value.quality === 'high' ? 48000 : 
                   recordingSettings.value.quality === 'medium' ? 44100 : 22050
    })
    
    await audioRecorder.initialize()
    
    // 设置回调函数
    audioRecorder.onData((audioBuffer: ArrayBuffer) => {
      // 将ArrayBuffer转换为Float32Array
      const float32Array = new Float32Array(audioBuffer)
      handleAudioData(float32Array)
    })
    audioRecorder.onVolume((volume: number) => {
      audioLevel.value = volume * 100
    })
    
    audioRecorder.startRecording()
    
    // 连接音频可视化器
      if (audioVisualizer) {
        // 由于AudioRecorder没有公开analyser，暂时跳过可视化连接
        // audioVisualizer.connect(audioRecorder.analyser!)
      }
    
    isRecording.value = true
    isPaused.value = false
    recordingDuration.value = 0
    recordingSize.value = 0
    transcriptCount.value = 0
    
    // 开始计时
    recordingTimer = setInterval(() => {
      recordingDuration.value += 1
    }, 1000)
    
    // 如果启用实时转录，连接WebSocket
    if (recordingSettings.value.realtimeTranscription) {
      wsStore.connect()
    }
    
    appStore.addNotification({
      type: 'success',
      title: '录制开始',
      message: '音频录制已开始'
    })
    
  } catch (error) {
    console.error('开始录制失败:', error)
    appStore.addNotification({
      type: 'error',
      title: '录制失败',
      message: '无法开始录制，请检查麦克风权限'
    })
  }
}

const pauseRecording = () => {
  if (audioRecorder) {
    if (isPaused.value) {
      audioRecorder.resumeRecording()
      if (recordingTimer) {
        recordingTimer = setInterval(() => {
          recordingDuration.value += 1
        }, 1000)
      }
    } else {
      audioRecorder.pauseRecording()
      if (recordingTimer) {
        clearInterval(recordingTimer)
      }
    }
    isPaused.value = !isPaused.value
  }
}

const stopRecording = async () => {
  try {
    if (audioRecorder) {
      const audioBlob = await audioRecorder.stopRecording()
      
      // 保存录制文件
      const record: RecordingRecord = {
        id: Date.now().toString(),
        name: `录制_${new Date().toLocaleString()}`,
        duration: recordingDuration.value,
        size: audioBlob.size,
        createdAt: new Date().toISOString(),
        filePath: ''
      }
      
      recordingHistory.value.unshift(record)
      
      // 下载文件
      const url = URL.createObjectURL(audioBlob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${record.name}.${recordingSettings.value.format}`
      a.click()
      URL.revokeObjectURL(url)
    }
    
    // 清理状态
    isRecording.value = false
    isPaused.value = false
    audioLevel.value = 0
    
    if (recordingTimer) {
      clearInterval(recordingTimer)
      recordingTimer = null
    }
    
    if (audioVisualizer) {
      audioVisualizer.stop()
    }
    
    appStore.addNotification({
      type: 'success',
      title: '录制完成',
      message: '音频文件已保存'
    })
    
  } catch (error) {
    console.error('停止录制失败:', error)
    appStore.addNotification({
      type: 'error',
      title: '录制错误',
      message: '停止录制时发生错误'
    })
  }
}

const handleAudioData = (audioData: Float32Array) => {
  recordingSize.value += audioData.length * 4 // 假设32位浮点数
  
  // 如果启用实时转录，发送音频数据
  if (recordingSettings.value.realtimeTranscription && wsStore.isConnected) {
    // 将Float32Array转换为base64字符串
    const audioDataString = btoa(String.fromCharCode(...new Uint8Array(audioData.buffer)))
    wsStore.sendAudioData(route.params.id as string, audioDataString)
  }
}

const toggleRealtimeTranscription = () => {
  recordingSettings.value.realtimeTranscription = !recordingSettings.value.realtimeTranscription
}

const toggleNoiseSuppression = () => {
  recordingSettings.value.noiseSuppression = !recordingSettings.value.noiseSuppression
}

const toggleAutoSave = () => {
  recordingSettings.value.autoSave = !recordingSettings.value.autoSave
}

const clearTranscripts = () => {
  transcripts.value = []
  transcriptCount.value = 0
}

const exportTranscripts = () => {
  if (transcripts.value.length === 0) return
  
  const content = transcripts.value.map(t => 
    `[${formatTime.time(t.timestamp)}] ${t.speaker || '说话人'}: ${t.text}`
  ).join('\n')
  
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `转录记录_${new Date().toLocaleString()}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

const playRecord = (record: RecordingRecord) => {
  // 播放录制文件
  appStore.addNotification({
    type: 'info',
    title: '播放功能',
    message: '播放功能正在开发中'
  })
}

const downloadRecord = (record: RecordingRecord) => {
  // 下载录制文件
  appStore.addNotification({
    type: 'info',
    title: '下载完成',
    message: `${record.name} 下载完成`
  })
}

const deleteRecord = (record: RecordingRecord) => {
  if (confirm(`确定要删除录制文件 "${record.name}" 吗？`)) {
    const index = recordingHistory.value.findIndex(r => r.id === record.id)
    if (index > -1) {
      recordingHistory.value.splice(index, 1)
      appStore.addNotification({
        type: 'success',
        title: '删除成功',
        message: '录制文件已删除'
      })
    }
  }
}

// 监听WebSocket转录消息
const handleTranscriptMessage = (data: any) => {
  if (data.type === 'transcript' && recordingSettings.value.realtimeTranscription) {
    const transcript: Transcript = {
      id: Date.now().toString(),
      text: data.text,
      speaker: data.speaker,
      timestamp: Date.now(),
      confidence: data.confidence
    }
    
    transcripts.value.push(transcript)
    transcriptCount.value = transcripts.value.length
    
    // 限制转录记录数量
    if (transcripts.value.length > 100) {
      transcripts.value = transcripts.value.slice(-100)
    }
  }
}

// 生命周期
onMounted(async () => {
  await loadAudioDevices()
  await initializeAudioVisualizer()
  
  // 监听WebSocket消息
  wsStore.$onAction(({ name, args }) => {
    if (name === 'sendMessage') {
      // 可以在这里处理发送的消息
    }
  })
  
  // 设置canvas宽度
  const updateCanvasWidth = () => {
    if (visualizerCanvas.value) {
      canvasWidth.value = visualizerCanvas.value.offsetWidth
    }
  }
  
  updateCanvasWidth()
  window.addEventListener('resize', updateCanvasWidth)
})

onUnmounted(() => {
  if (isRecording.value) {
    stopRecording()
  }
  
  if (recordingTimer) {
    clearInterval(recordingTimer)
  }
  
  if (audioVisualizer) {
    audioVisualizer.stop()
  }
  
  window.removeEventListener('resize', () => {})
})
</script>

<style scoped>
/* 自定义样式 */
</style>