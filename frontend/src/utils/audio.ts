// 音频处理工具类

export interface AudioConfig {
  sampleRate: number
  channels: number
  bitDepth: number
  bufferSize: number
}

export interface AudioRecorderOptions {
  sampleRate?: number
  channels?: number
  bitDepth?: number
  bufferSize?: number
  echoCancellation?: boolean
  noiseSuppression?: boolean
  autoGainControl?: boolean
}

export class AudioRecorder {
  private mediaRecorder: MediaRecorder | null = null
  private audioContext: AudioContext | null = null
  private analyser: AnalyserNode | null = null
  private microphone: MediaStreamAudioSourceNode | null = null
  private processor: ScriptProcessorNode | null = null
  private stream: MediaStream | null = null
  private isRecording = false
  private chunks: Blob[] = []
  private config: AudioConfig
  
  private onDataCallback?: (audioData: ArrayBuffer) => void
  private onVolumeCallback?: (volume: number) => void
  private onErrorCallback?: (error: Error) => void
  
  constructor(options: AudioRecorderOptions = {}) {
    this.config = {
      sampleRate: options.sampleRate || 16000,
      channels: options.channels || 1,
      bitDepth: options.bitDepth || 16,
      bufferSize: options.bufferSize || 4096
    }
  }
  
  // 初始化音频录制
  async initialize(): Promise<void> {
    try {
      // 请求麦克风权限
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: this.config.sampleRate,
          channelCount: this.config.channels,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      })
      
      // 创建音频上下文
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: this.config.sampleRate
      })
      
      // 创建分析器节点
      this.analyser = this.audioContext.createAnalyser()
      this.analyser.fftSize = 256
      
      // 创建麦克风源节点
      this.microphone = this.audioContext.createMediaStreamSource(this.stream)
      
      // 创建处理器节点
      this.processor = this.audioContext.createScriptProcessor(
        this.config.bufferSize,
        this.config.channels,
        this.config.channels
      )
      
      // 连接音频节点
      this.microphone.connect(this.analyser)
      this.microphone.connect(this.processor)
      this.processor.connect(this.audioContext.destination)
      
      // 处理音频数据
      this.processor.onaudioprocess = (event) => {
        if (!this.isRecording) return
        
        const inputBuffer = event.inputBuffer
        const audioData = inputBuffer.getChannelData(0)
        
        // 转换为 ArrayBuffer
        const arrayBuffer = this.float32ToInt16(audioData)
        
        // 回调音频数据
        if (this.onDataCallback) {
          this.onDataCallback(arrayBuffer)
        }
        
        // 计算音量
        if (this.onVolumeCallback) {
          const volume = this.calculateVolume(audioData)
          this.onVolumeCallback(volume)
        }
      }
      
      // 创建 MediaRecorder（用于录制完整音频文件）
      this.mediaRecorder = new MediaRecorder(this.stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.chunks.push(event.data)
        }
      }
      
    } catch (error) {
      console.error('音频初始化失败:', error)
      if (this.onErrorCallback) {
        this.onErrorCallback(error as Error)
      }
      throw error
    }
  }
  
  // 开始录制
  startRecording(): void {
    if (!this.audioContext || !this.mediaRecorder) {
      throw new Error('音频录制器未初始化')
    }
    
    if (this.isRecording) {
      console.warn('录制已在进行中')
      return
    }
    
    try {
      // 恢复音频上下文
      if (this.audioContext.state === 'suspended') {
        this.audioContext.resume()
      }
      
      this.isRecording = true
      this.chunks = []
      
      // 开始 MediaRecorder 录制
      this.mediaRecorder.start(100) // 每100ms收集一次数据
      
      console.log('开始录制音频')
    } catch (error) {
      console.error('开始录制失败:', error)
      if (this.onErrorCallback) {
        this.onErrorCallback(error as Error)
      }
      throw error
    }
  }
  
  // 停止录制
  stopRecording(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      if (!this.isRecording || !this.mediaRecorder) {
        reject(new Error('录制未在进行中'))
        return
      }
      
      this.isRecording = false
      
      this.mediaRecorder.onstop = () => {
        const blob = new Blob(this.chunks, { type: 'audio/webm;codecs=opus' })
        this.chunks = []
        resolve(blob)
      }
      
      this.mediaRecorder.onerror = (event) => {
        reject(new Error('录制停止时发生错误'))
      }
      
      this.mediaRecorder.stop()
      console.log('停止录制音频')
    })
  }
  
  // 暂停录制
  pauseRecording(): void {
    if (this.isRecording && this.mediaRecorder) {
      this.mediaRecorder.pause()
      console.log('暂停录制音频')
    }
  }
  
  // 恢复录制
  resumeRecording(): void {
    if (this.isRecording && this.mediaRecorder) {
      this.mediaRecorder.resume()
      console.log('恢复录制音频')
    }
  }
  
  // 获取音频设备列表
  static async getAudioDevices(): Promise<MediaDeviceInfo[]> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices()
      return devices.filter(device => device.kind === 'audioinput')
    } catch (error) {
      console.error('获取音频设备失败:', error)
      return []
    }
  }
  
  // 检查浏览器支持
  static checkSupport(): { supported: boolean; missing: string[] } {
    const missing: string[] = []
    
    if (!navigator.mediaDevices) {
      missing.push('MediaDevices API')
    }
    
    if (!navigator.mediaDevices.getUserMedia) {
      missing.push('getUserMedia API')
    }
    
    if (!window.AudioContext && !(window as any).webkitAudioContext) {
      missing.push('Web Audio API')
    }
    
    if (!window.MediaRecorder) {
      missing.push('MediaRecorder API')
    }
    
    return {
      supported: missing.length === 0,
      missing
    }
  }
  
  // 获取当前音量
  getCurrentVolume(): number {
    if (!this.analyser) return 0
    
    const bufferLength = this.analyser.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)
    this.analyser.getByteFrequencyData(dataArray)
    
    let sum = 0
    for (let i = 0; i < bufferLength; i++) {
      sum += dataArray[i]
    }
    
    return sum / bufferLength / 255 // 归一化到 0-1
  }
  
  // 设置回调函数
  onData(callback: (audioData: ArrayBuffer) => void): void {
    this.onDataCallback = callback
  }
  
  onVolume(callback: (volume: number) => void): void {
    this.onVolumeCallback = callback
  }
  
  onError(callback: (error: Error) => void): void {
    this.onErrorCallback = callback
  }
  
  // 清理资源
  destroy(): void {
    try {
      if (this.isRecording) {
        this.stopRecording()
      }
      
      if (this.processor) {
        this.processor.disconnect()
        this.processor = null
      }
      
      if (this.microphone) {
        this.microphone.disconnect()
        this.microphone = null
      }
      
      if (this.analyser) {
        this.analyser.disconnect()
        this.analyser = null
      }
      
      if (this.audioContext) {
        this.audioContext.close()
        this.audioContext = null
      }
      
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop())
        this.stream = null
      }
      
      this.mediaRecorder = null
      this.chunks = []
      
      console.log('音频录制器已清理')
    } catch (error) {
      console.error('清理音频录制器失败:', error)
    }
  }
  
  // 工具方法：Float32 转 Int16
  private float32ToInt16(float32Array: Float32Array): ArrayBuffer {
    const int16Array = new Int16Array(float32Array.length)
    
    for (let i = 0; i < float32Array.length; i++) {
      // 将 -1 到 1 的浮点数转换为 -32768 到 32767 的整数
      const sample = Math.max(-1, Math.min(1, float32Array[i]))
      int16Array[i] = sample < 0 ? sample * 0x8000 : sample * 0x7FFF
    }
    
    return int16Array.buffer
  }
  
  // 工具方法：计算音量
  private calculateVolume(audioData: Float32Array): number {
    let sum = 0
    for (let i = 0; i < audioData.length; i++) {
      sum += audioData[i] * audioData[i]
    }
    
    const rms = Math.sqrt(sum / audioData.length)
    return Math.min(1, rms * 10) // 放大并限制在 0-1 范围内
  }
  
  // Getter 方法
  get recording(): boolean {
    return this.isRecording
  }
  
  get audioConfig(): AudioConfig {
    return { ...this.config }
  }
}

// 音频格式转换工具
export class AudioConverter {
  // WAV 文件头
  static createWavHeader(sampleRate: number, channels: number, bitDepth: number, dataLength: number): ArrayBuffer {
    const buffer = new ArrayBuffer(44)
    const view = new DataView(buffer)
    
    // RIFF 标识符
    view.setUint32(0, 0x52494646, false) // "RIFF"
    // 文件大小
    view.setUint32(4, 36 + dataLength, true)
    // WAVE 标识符
    view.setUint32(8, 0x57415645, false) // "WAVE"
    // fmt 子块
    view.setUint32(12, 0x666d7420, false) // "fmt "
    view.setUint32(16, 16, true) // 子块大小
    view.setUint16(20, 1, true) // 音频格式 (PCM)
    view.setUint16(22, channels, true) // 声道数
    view.setUint32(24, sampleRate, true) // 采样率
    view.setUint32(28, sampleRate * channels * bitDepth / 8, true) // 字节率
    view.setUint16(32, channels * bitDepth / 8, true) // 块对齐
    view.setUint16(34, bitDepth, true) // 位深度
    // data 子块
    view.setUint32(36, 0x64617461, false) // "data"
    view.setUint32(40, dataLength, true) // 数据长度
    
    return buffer
  }
  
  // 转换为 WAV 格式
  static toWav(audioData: ArrayBuffer, sampleRate: number, channels: number, bitDepth: number): Blob {
    const header = this.createWavHeader(sampleRate, channels, bitDepth, audioData.byteLength)
    return new Blob([header, audioData], { type: 'audio/wav' })
  }
  
  // 重采样音频数据
  static resample(audioData: Float32Array, fromSampleRate: number, toSampleRate: number): Float32Array {
    if (fromSampleRate === toSampleRate) {
      return audioData
    }
    
    const ratio = fromSampleRate / toSampleRate
    const newLength = Math.round(audioData.length / ratio)
    const result = new Float32Array(newLength)
    
    for (let i = 0; i < newLength; i++) {
      const index = i * ratio
      const indexFloor = Math.floor(index)
      const indexCeil = Math.min(indexFloor + 1, audioData.length - 1)
      const fraction = index - indexFloor
      
      // 线性插值
      result[i] = audioData[indexFloor] * (1 - fraction) + audioData[indexCeil] * fraction
    }
    
    return result
  }
}

// 音频可视化工具
export class AudioVisualizer {
  private canvas: HTMLCanvasElement
  private ctx: CanvasRenderingContext2D
  private analyser: AnalyserNode | null = null
  private animationId: number | null = null
  
  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas
    const ctx = canvas.getContext('2d')
    if (!ctx) {
      throw new Error('无法获取 Canvas 2D 上下文')
    }
    this.ctx = ctx
  }
  
  // 连接分析器
  connect(analyser: AnalyserNode): void {
    this.analyser = analyser
  }
  
  // 开始可视化
  start(): void {
    if (!this.analyser) {
      throw new Error('未连接音频分析器')
    }
    
    this.draw()
  }
  
  // 停止可视化
  stop(): void {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId)
      this.animationId = null
    }
    
    // 清空画布
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)
  }
  
  // 绘制频谱
  private draw(): void {
    if (!this.analyser) return
    
    this.animationId = requestAnimationFrame(() => this.draw())
    
    const bufferLength = this.analyser.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)
    this.analyser.getByteFrequencyData(dataArray)
    
    const { width, height } = this.canvas
    
    // 清空画布
    this.ctx.fillStyle = 'rgb(20, 20, 20)'
    this.ctx.fillRect(0, 0, width, height)
    
    // 绘制频谱条
    const barWidth = width / bufferLength * 2.5
    let x = 0
    
    for (let i = 0; i < bufferLength; i++) {
      const barHeight = (dataArray[i] / 255) * height
      
      // 渐变色
      const hue = (i / bufferLength) * 360
      this.ctx.fillStyle = `hsl(${hue}, 70%, 50%)`
      
      this.ctx.fillRect(x, height - barHeight, barWidth, barHeight)
      x += barWidth + 1
    }
  }
}

export default AudioRecorder