import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import { apiClient } from '@/utils/api'
import { useAppStore } from './app'

export interface MeetingSettings {
  recordQuality?: string
  language?: string
  realtimeTranscription?: boolean
  autoSummary?: boolean
  noiseSuppression?: boolean
}

export interface Meeting {
  id: string
  title: string
  description?: string
  status: 'waiting' | 'recording' | 'completed'
  start_time?: string
  end_time?: string
  duration?: number
  participants: string[]
  settings?: MeetingSettings
  created_at: string
  updated_at: string
}

export interface TranscriptRecord {
  id: string
  meeting_id: string
  speaker: string
  text: string
  timestamp: number
  confidence: number
  is_final: boolean
  created_at: string
}

export interface Transcript {
  id: string
  speaker: string
  text: string
  timestamp: number
}

export interface Summary {
  id: string
  meeting_id: string
  summary: string
  key_points: string[]
  action_items: string[]
  participants_summary: Record<string, any>
  duration_summary: string
  created_at: string
}

export interface MeetingSummary {
  id: string
  meeting_id: string
  summary: string
  key_points: string[]
  action_items: string[]
  participants_summary: Record<string, any>
  duration_summary: string
  created_at: string
}

export interface CreateMeetingRequest {
  title: string
  description?: string
  participants: string[]
}

export const useMeetingStore = defineStore('meeting', () => {
  // 状态
  const meetings: Ref<Meeting[]> = ref([])
  const currentMeeting: Ref<Meeting | null> = ref(null)
  const transcripts: Ref<TranscriptRecord[]> = ref([])
  const summary: Ref<MeetingSummary | null> = ref(null)
  const isLoading: Ref<boolean> = ref(false)
  const isRecording: Ref<boolean> = ref(false)
  const error = ref('')
  
  const appStore = useAppStore()
  
  // 计算属性
  const activeMeetings = computed(() => 
    meetings.value.filter(m => m.status === 'recording')
  )
  
  const completedMeetings = computed(() => 
    meetings.value.filter(m => m.status === 'completed')
  )
  
  const waitingMeetings = computed(() => 
    meetings.value.filter(m => m.status === 'waiting')
  )
  
  const currentTranscripts = computed(() => 
    transcripts.value.filter(t => t.meeting_id === currentMeeting.value?.id)
  )
  
  const finalTranscripts = computed(() => 
    currentTranscripts.value.filter(t => t.is_final)
  )
  
  const realtimeTranscripts = computed(() => 
    currentTranscripts.value.filter(t => !t.is_final)
  )
  
  // 获取会议列表
  const fetchMeetings = async (limit = 50, offset = 0) => {
    try {
      isLoading.value = true
      error.value = ''
      
      const response = await apiClient.get('/api/meetings', {
        params: { limit, offset }
      })
      
      if (response.data.success) {
        meetings.value = response.data.data
      } else {
        throw new Error(response.data.message || '获取会议列表失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取会议列表失败'
      appStore.showError('获取失败', error.value)
      console.error('获取会议列表失败:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  // 获取会议详情
  const fetchMeeting = async (meetingId: string) => {
    try {
      isLoading.value = true
      error.value = ''
      
      const response = await apiClient.get(`/api/meetings/${meetingId}`)
      
      if (response.data.success) {
        currentMeeting.value = response.data.data
        
        // 更新会议列表中的对应项
        const index = meetings.value.findIndex(m => m.id === meetingId)
        if (index > -1) {
          meetings.value[index] = response.data.data
        }
      } else {
        throw new Error(response.data.message || '获取会议详情失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取会议详情失败'
      appStore.showError('获取失败', error.value)
      console.error('获取会议详情失败:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  // 创建会议
  const createMeeting = async (meetingData: CreateMeetingRequest): Promise<Meeting | null> => {
    try {
      isLoading.value = true
      error.value = ''
      
      const response = await apiClient.post('/api/meetings', meetingData)
      
      if (response.data.success) {
        const newMeeting = response.data.data
        meetings.value.unshift(newMeeting)
        appStore.showSuccess('创建成功', '会议创建成功')
        return newMeeting
      } else {
        throw new Error(response.data.message || '创建会议失败')
      }
    } catch (err: any) {
      error.value = err.message || '创建会议失败'
      appStore.showError('创建失败', error.value)
      console.error('创建会议失败:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }
  
  // 开始会议
  const startMeeting = async (meetingId: string) => {
    try {
      isLoading.value = true
      error.value = ''
      
      const response = await apiClient.post(`/api/meetings/${meetingId}/start`)
      
      if (response.data.success) {
        // 更新会议状态
        const meeting = meetings.value.find(m => m.id === meetingId)
        if (meeting) {
          meeting.status = 'recording'
          meeting.start_time = new Date().toISOString()
        }
        
        if (currentMeeting.value?.id === meetingId) {
          currentMeeting.value.status = 'recording'
          currentMeeting.value.start_time = new Date().toISOString()
        }
        
        isRecording.value = true
        appStore.showSuccess('会议开始', '会议已开始录制')
      } else {
        throw new Error(response.data.message || '开始会议失败')
      }
    } catch (err: any) {
      error.value = err.message || '开始会议失败'
      appStore.showError('开始失败', error.value)
      console.error('开始会议失败:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  // 结束会议
  const endMeeting = async (meetingId: string) => {
    try {
      isLoading.value = true
      error.value = ''
      
      const response = await apiClient.post(`/api/meetings/${meetingId}/end`)
      
      if (response.data.success) {
        // 更新会议状态
        const meeting = meetings.value.find(m => m.id === meetingId)
        if (meeting) {
          meeting.status = 'completed'
          meeting.end_time = new Date().toISOString()
        }
        
        if (currentMeeting.value?.id === meetingId) {
          currentMeeting.value.status = 'completed'
          currentMeeting.value.end_time = new Date().toISOString()
        }
        
        isRecording.value = false
        appStore.showSuccess('会议结束', '会议已结束，正在生成总结')
      } else {
        throw new Error(response.data.message || '结束会议失败')
      }
    } catch (err: any) {
      error.value = err.message || '结束会议失败'
      appStore.showError('结束失败', error.value)
      console.error('结束会议失败:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  // 删除会议
  const deleteMeeting = async (meetingId: string) => {
    try {
      isLoading.value = true
      error.value = ''
      
      const response = await apiClient.delete(`/api/meetings/${meetingId}`)
      
      if (response.data.success) {
        // 从列表中移除
        const index = meetings.value.findIndex(m => m.id === meetingId)
        if (index > -1) {
          meetings.value.splice(index, 1)
        }
        
        // 如果是当前会议，清空
        if (currentMeeting.value?.id === meetingId) {
          currentMeeting.value = null
          transcripts.value = []
          summary.value = null
        }
        
        appStore.showSuccess('删除成功', '会议已删除')
      } else {
        throw new Error(response.data.message || '删除会议失败')
      }
    } catch (err: any) {
      error.value = err.message || '删除会议失败'
      appStore.showError('删除失败', error.value)
      console.error('删除会议失败:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  // 获取转录记录
  const fetchTranscripts = async (meetingId: string) => {
    try {
      const response = await apiClient.get(`/api/meetings/${meetingId}/transcripts`)
      
      if (response.data.success) {
        transcripts.value = response.data.data
      } else {
        throw new Error(response.data.message || '获取转录记录失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取转录记录失败'
      console.error('获取转录记录失败:', err)
    }
  }
  
  // 获取会议总结
  const fetchSummary = async (meetingId: string) => {
    try {
      const response = await apiClient.get(`/api/meetings/${meetingId}/summary`)
      
      if (response.data.success) {
        summary.value = response.data.data
      } else {
        throw new Error(response.data.message || '获取会议总结失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取会议总结失败'
      console.error('获取会议总结失败:', err)
    }
  }
  
  // 添加转录记录（实时）
  const addTranscript = (transcript: TranscriptRecord) => {
    const existingIndex = transcripts.value.findIndex(t => t.id === transcript.id)
    
    if (existingIndex > -1) {
      // 更新现有记录
      transcripts.value[existingIndex] = transcript
    } else {
      // 添加新记录
      transcripts.value.push(transcript)
    }
    
    // 按时间戳排序
    transcripts.value.sort((a, b) => a.timestamp - b.timestamp)
  }
  
  // 下载会议文件
  const downloadFile = async (meetingId: string, fileType: 'audio' | 'transcript' | 'transcript_text' | 'summary') => {
    try {
      const response = await apiClient.get(`/api/meetings/${meetingId}/download/${fileType}`, {
        responseType: 'blob'
      })
      
      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      
      // 设置文件名
      const contentDisposition = response.headers['content-disposition']
      let filename = `meeting_${meetingId}_${fileType}`
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/)
        if (filenameMatch) {
          filename = filenameMatch[1]
        }
      }
      
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      appStore.showSuccess('下载成功', `${filename} 下载完成`)
    } catch (err: any) {
      error.value = err.message || '下载文件失败'
      appStore.showError('下载失败', error.value)
      console.error('下载文件失败:', err)
    }
  }
  
  // 清空当前会议数据
  const clearCurrentMeeting = () => {
    currentMeeting.value = null
    transcripts.value = []
    summary.value = null
    isRecording.value = false
  }
  
  // 设置当前会议
  const setCurrentMeeting = (meeting: Meeting) => {
    currentMeeting.value = meeting
    isRecording.value = meeting.status === 'recording'
  }
  
  return {
    // 状态
    meetings,
    currentMeeting,
    transcripts,
    summary,
    isLoading,
    isRecording,
    error,
    
    // 计算属性
    activeMeetings,
    completedMeetings,
    waitingMeetings,
    currentTranscripts,
    finalTranscripts,
    realtimeTranscripts,
    
    // 方法
    fetchMeetings,
    fetchMeeting,
    createMeeting,
    startMeeting,
    endMeeting,
    deleteMeeting,
    fetchTranscripts,
    fetchSummary,
    addTranscript,
    downloadFile,
    clearCurrentMeeting,
    setCurrentMeeting
  }
})