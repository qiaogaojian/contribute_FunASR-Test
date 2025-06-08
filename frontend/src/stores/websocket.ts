import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import { useAppStore } from './app'

export interface WebSocketMessage {
  type: string
  data?: any
  meeting_id?: string
  timestamp?: string
  message?: string
  audio_data?: string
}

export interface ConnectionState {
  isConnected: boolean
  isConnecting: boolean
  reconnectAttempts: number
  lastError?: string
}

export const useWebSocketStore = defineStore('websocket', () => {
  // 状态
  const socket: Ref<WebSocket | null> = ref(null)
  const isConnected: Ref<boolean> = ref(false)
  const isConnecting: Ref<boolean> = ref(false)
  const reconnectAttempts: Ref<number> = ref(0)
  const lastError: Ref<string | undefined> = ref(undefined)
  const clientId: Ref<string> = ref('')
  const currentMeetingId: Ref<string | null> = ref(null)
  const messageQueue: Ref<WebSocketMessage[]> = ref([])
  
  // 配置
  const maxReconnectAttempts = 5
  const reconnectDelay = 1000
  const heartbeatInterval = 30000
  
  // 定时器
  let reconnectTimer: NodeJS.Timeout | null = null
  let heartbeatTimer: NodeJS.Timeout | null = null
  
  const appStore = useAppStore()
  
  // 计算属性
  const connectionState = computed((): ConnectionState => ({
    isConnected: isConnected.value,
    isConnecting: isConnecting.value,
    reconnectAttempts: reconnectAttempts.value,
    lastError: lastError.value
  }))
  
  const canReconnect = computed(() => {
    return !isConnected.value && !isConnecting.value && reconnectAttempts.value < maxReconnectAttempts
  })
  
  // 生成客户端ID
  const generateClientId = () => {
    return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
  
  // 连接WebSocket
  const connect = async () => {
    if (isConnected.value || isConnecting.value) {
      return
    }
    
    try {
      isConnecting.value = true
      lastError.value = undefined
      
      // 生成客户端ID
      if (!clientId.value) {
        clientId.value = generateClientId()
      }
      
      // 创建WebSocket连接
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = window.location.host
      const wsUrl = `${protocol}//${host}/ws/${clientId.value}`
      
      console.log('连接WebSocket:', wsUrl)
      
      socket.value = new WebSocket(wsUrl)
      
      // 连接成功
      socket.value.onopen = () => {
        console.log('WebSocket连接成功')
        isConnected.value = true
        isConnecting.value = false
        reconnectAttempts.value = 0
        
        // 发送队列中的消息
        flushMessageQueue()
        
        // 启动心跳
        startHeartbeat()
        
        appStore.showSuccess('连接成功', 'WebSocket连接已建立')
      }
      
      // 接收消息
      socket.value.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          handleMessage(message)
        } catch (error) {
          console.error('解析WebSocket消息失败:', error)
        }
      }
      
      // 连接关闭
      socket.value.onclose = (event) => {
        console.log('WebSocket连接关闭:', event.code, event.reason)
        isConnected.value = false
        isConnecting.value = false
        
        // 停止心跳
        stopHeartbeat()
        
        // 如果不是主动关闭，尝试重连
        if (event.code !== 1000 && canReconnect.value) {
          scheduleReconnect()
        }
      }
      
      // 连接错误
      socket.value.onerror = (error) => {
        console.error('WebSocket连接错误:', error)
        lastError.value = 'WebSocket连接错误'
        isConnecting.value = false
        
        appStore.showError('连接失败', 'WebSocket连接发生错误')
      }
      
    } catch (error) {
      console.error('创建WebSocket连接失败:', error)
      isConnecting.value = false
      lastError.value = '创建连接失败'
      
      if (canReconnect.value) {
        scheduleReconnect()
      }
    }
  }
  
  // 断开连接
  const disconnect = () => {
    if (socket.value) {
      socket.value.close(1000, '主动断开连接')
      socket.value = null
    }
    
    isConnected.value = false
    isConnecting.value = false
    reconnectAttempts.value = 0
    currentMeetingId.value = null
    
    // 清理定时器
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    
    stopHeartbeat()
  }
  
  // 发送消息
  const sendMessage = (message: WebSocketMessage) => {
    if (isConnected.value && socket.value) {
      try {
        socket.value.send(JSON.stringify(message))
        console.log('发送WebSocket消息:', message)
      } catch (error) {
        console.error('发送WebSocket消息失败:', error)
        // 将消息加入队列
        messageQueue.value.push(message)
      }
    } else {
      // 将消息加入队列
      messageQueue.value.push(message)
      
      // 尝试重连
      if (canReconnect.value) {
        connect()
      }
    }
  }
  
  // 处理接收到的消息
  const handleMessage = (message: WebSocketMessage) => {
    console.log('收到WebSocket消息:', message)
    
    switch (message.type) {
      case 'transcript':
        // 处理转录消息
        handleTranscriptMessage(message)
        break
        
      case 'meeting_started':
        appStore.showSuccess('会议开始', '会议录制已开始')
        break
        
      case 'meeting_ended':
        appStore.showInfo('会议结束', '会议录制已结束')
        break
        
      case 'recording_started':
        appStore.showSuccess('录制开始', message.message || '录制已开始')
        break
        
      case 'recording_stopped':
        appStore.showInfo('录制停止', message.message || '录制已停止')
        break
        
      case 'joined_meeting':
        appStore.showSuccess('加入会议', message.message || '已加入会议')
        break
        
      case 'left_meeting':
        appStore.showInfo('离开会议', message.message || '已离开会议')
        break
        
      case 'error':
        appStore.showError('错误', message.message || '发生未知错误')
        break
        
      default:
        console.log('未处理的消息类型:', message.type)
    }
  }
  
  // 处理转录消息
  const handleTranscriptMessage = (message: WebSocketMessage) => {
    // 这里可以触发事件或更新其他store
    // 例如：meetingStore.addTranscript(message.data)
    console.log('收到转录消息:', message.data)
  }
  
  // 发送队列中的消息
  const flushMessageQueue = () => {
    while (messageQueue.value.length > 0 && isConnected.value) {
      const message = messageQueue.value.shift()
      if (message) {
        sendMessage(message)
      }
    }
  }
  
  // 安排重连
  const scheduleReconnect = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
    }
    
    reconnectAttempts.value++
    const delay = reconnectDelay * Math.pow(2, reconnectAttempts.value - 1)
    
    console.log(`${delay}ms后尝试第${reconnectAttempts.value}次重连`)
    
    reconnectTimer = setTimeout(() => {
      if (canReconnect.value) {
        connect()
      }
    }, delay)
  }
  
  // 启动心跳
  const startHeartbeat = () => {
    stopHeartbeat()
    
    heartbeatTimer = setInterval(() => {
      if (isConnected.value) {
        sendMessage({ type: 'ping' })
      }
    }, heartbeatInterval)
  }
  
  // 停止心跳
  const stopHeartbeat = () => {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }
  
  // 会议相关方法
  const joinMeeting = (meetingId: string) => {
    currentMeetingId.value = meetingId
    sendMessage({
      type: 'join_meeting',
      meeting_id: meetingId
    })
  }
  
  const leaveMeeting = () => {
    if (currentMeetingId.value) {
      sendMessage({
        type: 'leave_meeting',
        meeting_id: currentMeetingId.value
      })
      currentMeetingId.value = null
    }
  }
  
  const startRecording = (meetingId: string) => {
    sendMessage({
      type: 'start_recording',
      meeting_id: meetingId
    })
  }
  
  const stopRecording = (meetingId: string) => {
    sendMessage({
      type: 'stop_recording',
      meeting_id: meetingId
    })
  }
  
  const sendAudioData = (meetingId: string, audioData: string) => {
    sendMessage({
      type: 'audio_data',
      meeting_id: meetingId,
      audio_data: audioData
    })
  }
  
  return {
    // 状态
    socket,
    isConnected,
    isConnecting,
    reconnectAttempts,
    lastError,
    clientId,
    currentMeetingId,
    messageQueue,
    
    // 计算属性
    connectionState,
    canReconnect,
    
    // 方法
    connect,
    disconnect,
    sendMessage,
    
    // 会议方法
    joinMeeting,
    leaveMeeting,
    startRecording,
    stopRecording,
    sendAudioData
  }
})