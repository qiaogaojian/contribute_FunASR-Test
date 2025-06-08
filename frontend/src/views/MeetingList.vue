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
            <h1 class="text-2xl font-bold text-gray-900">会议列表</h1>
          </div>
          
          <div class="flex items-center space-x-3">
            <!-- 搜索框 -->
            <div class="relative">
              <MagnifyingGlassIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="搜索会议..."
                class="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64"
              />
            </div>
            
            <!-- 筛选按钮 -->
            <button
              @click="showFilters = !showFilters"
              class="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <FunnelIcon class="w-5 h-5 mr-2 text-gray-600" />
              筛选
            </button>
            
            <!-- 新建会议按钮 -->
            <router-link
              to="/meetings/new"
              class="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <PlusIcon class="w-5 h-5 mr-2" />
              新建会议
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选面板 -->
    <div v-if="showFilters" class="bg-white border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- 状态筛选 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">状态</label>
            <select
              v-model="filters.status"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">全部状态</option>
              <option value="waiting">等待中</option>
              <option value="recording">录制中</option>
              <option value="completed">已完成</option>
            </select>
          </div>
          
          <!-- 日期范围 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">开始日期</label>
            <input
              v-model="filters.startDate"
              type="date"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">结束日期</label>
            <input
              v-model="filters.endDate"
              type="date"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <!-- 排序 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">排序</label>
            <select
              v-model="filters.sortBy"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="created_at_desc">创建时间（新到旧）</option>
              <option value="created_at_asc">创建时间（旧到新）</option>
              <option value="title_asc">标题（A-Z）</option>
              <option value="title_desc">标题（Z-A）</option>
              <option value="duration_desc">时长（长到短）</option>
              <option value="duration_asc">时长（短到长）</option>
            </select>
          </div>
        </div>
        
        <!-- 筛选操作 -->
        <div class="flex items-center justify-between mt-4">
          <div class="text-sm text-gray-600">
            共找到 {{ filteredMeetings.length }} 个会议
          </div>
          <div class="flex space-x-2">
            <button
              @click="resetFilters"
              class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 transition-colors"
            >
              重置
            </button>
            <button
              @click="showFilters = false"
              class="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              应用
            </button>
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
      
      <!-- 空状态 -->
      <div v-else-if="filteredMeetings.length === 0" class="text-center py-12">
        <CalendarIcon class="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">暂无会议</h3>
        <p class="text-gray-500 mb-6">
          {{ searchQuery || hasActiveFilters ? '没有找到符合条件的会议' : '还没有创建任何会议' }}
        </p>
        <router-link
          to="/meetings/new"
          class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <PlusIcon class="w-5 h-5 mr-2" />
          创建第一个会议
        </router-link>
      </div>
      
      <!-- 会议列表 -->
      <div v-else class="space-y-4">
        <!-- 列表视图切换 -->
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <button
              @click="viewMode = 'list'"
              :class="[
                'p-2 rounded-lg transition-colors',
                viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'
              ]"
            >
              <Bars3Icon class="w-5 h-5" />
            </button>
            <button
              @click="viewMode = 'grid'"
              :class="[
                'p-2 rounded-lg transition-colors',
                viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'
              ]"
            >
              <Squares2X2Icon class="w-5 h-5" />
            </button>
          </div>
          
          <!-- 批量操作 -->
          <div v-if="selectedMeetings.length > 0" class="flex items-center space-x-2">
            <span class="text-sm text-gray-600">已选择 {{ selectedMeetings.length }} 个会议</span>
            <button
              @click="batchDelete"
              class="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
            >
              批量删除
            </button>
            <button
              @click="selectedMeetings = []"
              class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 transition-colors"
            >
              取消选择
            </button>
          </div>
        </div>
        
        <!-- 列表视图 -->
        <div v-if="viewMode === 'list'" class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div class="divide-y divide-gray-200">
            <div
              v-for="meeting in paginatedMeetings"
              :key="meeting.id"
              class="p-6 hover:bg-gray-50 transition-colors"
            >
              <div class="flex items-center space-x-4">
                <!-- 选择框 -->
                <input
                  v-model="selectedMeetings"
                  :value="meeting.id"
                  type="checkbox"
                  class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                
                <!-- 会议信息 -->
                <div class="flex-1 cursor-pointer" @click="$router.push(`/meetings/${meeting.id}`)">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                      <h3 class="text-lg font-medium text-gray-900">{{ meeting.title }}</h3>
                      <span :class="[
                        'px-2 py-1 text-xs font-medium rounded-full',
                        getStatusClass(meeting.status)
                      ]">
                        {{ getStatusText(meeting.status) }}
                      </span>
                    </div>
                    
                    <div class="flex items-center space-x-2">
                      <!-- 操作按钮 -->
                      <button
                        v-if="meeting.status === 'waiting'"
                        @click.stop="startMeeting(meeting.id)"
                        class="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                        title="开始会议"
                      >
                        <PlayIcon class="w-5 h-5" />
                      </button>
                      
                      <button
                        v-if="meeting.status === 'recording'"
                        @click.stop="stopMeeting(meeting.id)"
                        class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="停止会议"
                      >
                        <StopIcon class="w-5 h-5" />
                      </button>
                      
                      <button
                        @click.stop="downloadMeeting(meeting.id)"
                        class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="下载文件"
                      >
                        <ArrowDownTrayIcon class="w-5 h-5" />
                      </button>
                      
                      <button
                        @click.stop="deleteMeeting(meeting.id)"
                        class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="删除会议"
                      >
                        <TrashIcon class="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                  
                  <p v-if="meeting.description" class="text-gray-600 mt-1">{{ meeting.description }}</p>
                  
                  <div class="flex items-center space-x-6 mt-3 text-sm text-gray-500">
                    <span class="flex items-center">
                      <CalendarIcon class="w-4 h-4 mr-1" />
                      {{ formatTime.datetime(meeting.created_at) }}
                    </span>
                    <span v-if="meeting.duration" class="flex items-center">
                      <ClockIcon class="w-4 h-4 mr-1" />
                      {{ formatTime.duration(meeting.duration) }}
                    </span>
                    <span class="flex items-center">
                      <UsersIcon class="w-4 h-4 mr-1" />
                      {{ meeting.participants.length }} 人
                    </span>
                    <span v-if="meeting.start_time" class="flex items-center">
                      <PlayIcon class="w-4 h-4 mr-1" />
                      {{ formatTime.datetime(meeting.start_time) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 网格视图 -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="meeting in paginatedMeetings"
            :key="meeting.id"
            class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
            @click="$router.push(`/meetings/${meeting.id}`)"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center space-x-2">
                <input
                  v-model="selectedMeetings"
                  :value="meeting.id"
                  type="checkbox"
                  class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  @click.stop
                />
                <span :class="[
                  'px-2 py-1 text-xs font-medium rounded-full',
                  getStatusClass(meeting.status)
                ]">
                  {{ getStatusText(meeting.status) }}
                </span>
              </div>
              
              <div class="flex space-x-1">
                <button
                  @click.stop="downloadMeeting(meeting.id)"
                  class="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                >
                  <ArrowDownTrayIcon class="w-4 h-4" />
                </button>
                <button
                  @click.stop="deleteMeeting(meeting.id)"
                  class="p-1 text-gray-400 hover:text-red-600 transition-colors"
                >
                  <TrashIcon class="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <h3 class="text-lg font-medium text-gray-900 mb-2">{{ meeting.title }}</h3>
            <p v-if="meeting.description" class="text-gray-600 text-sm mb-4 line-clamp-2">{{ meeting.description }}</p>
            
            <div class="space-y-2 text-sm text-gray-500">
              <div class="flex items-center">
                <CalendarIcon class="w-4 h-4 mr-2" />
                {{ formatTime.date(meeting.created_at) }}
              </div>
              <div v-if="meeting.duration" class="flex items-center">
                <ClockIcon class="w-4 h-4 mr-2" />
                {{ formatTime.duration(meeting.duration) }}
              </div>
              <div class="flex items-center">
                <UsersIcon class="w-4 h-4 mr-2" />
                {{ meeting.participants.length }} 人参与
              </div>
            </div>
          </div>
        </div>
        
        <!-- 分页 -->
        <div v-if="totalPages > 1" class="flex items-center justify-between mt-8">
          <div class="text-sm text-gray-600">
            显示第 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, filteredMeetings.length) }} 条，
            共 {{ filteredMeetings.length }} 条记录
          </div>
          
          <div class="flex items-center space-x-2">
            <button
              @click="currentPage = Math.max(1, currentPage - 1)"
              :disabled="currentPage === 1"
              class="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              上一页
            </button>
            
            <div class="flex space-x-1">
              <button
                v-for="page in visiblePages"
                :key="page"
                @click="typeof page === 'number' && (currentPage = page)"
                :class="[
                  'px-3 py-2 text-sm rounded-lg',
                  page === currentPage
                    ? 'bg-blue-600 text-white'
                    : 'border border-gray-300 hover:bg-gray-50'
                ]"
              >
                {{ page }}
              </button>
            </div>
            
            <button
              @click="currentPage = Math.min(totalPages, currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import {
  ArrowLeftIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  PlusIcon,
  CalendarIcon,
  ClockIcon,
  UsersIcon,
  PlayIcon,
  StopIcon,
  ArrowDownTrayIcon,
  TrashIcon,
  Bars3Icon,
  Squares2X2Icon
} from '@heroicons/vue/24/outline'

import { useAppStore } from '@/stores/app'
import { useMeetingStore } from '@/stores/meeting'
import { formatTime } from '@/utils'
import type { Meeting } from '@/stores/meeting'

const appStore = useAppStore()
const meetingStore = useMeetingStore()

// 响应式数据
const isLoading = ref(false)
const searchQuery = ref('')
const showFilters = ref(false)
const viewMode = ref<'list' | 'grid'>('list')
const selectedMeetings = ref<string[]>([])
const currentPage = ref(1)
const pageSize = ref(10)

// 筛选条件
const filters = ref({
  status: '',
  startDate: '',
  endDate: '',
  sortBy: 'created_at_desc'
})

// 计算属性
const filteredMeetings = computed(() => {
  let meetings = [...meetingStore.meetings]
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    meetings = meetings.filter(meeting => 
      meeting.title.toLowerCase().includes(query) ||
      meeting.description?.toLowerCase().includes(query) ||
      meeting.participants.some(p => p.toLowerCase().includes(query))
    )
  }
  
  // 状态过滤
  if (filters.value.status) {
    meetings = meetings.filter(meeting => meeting.status === filters.value.status)
  }
  
  // 日期过滤
  if (filters.value.startDate) {
    const startDate = new Date(filters.value.startDate)
    meetings = meetings.filter(meeting => new Date(meeting.created_at) >= startDate)
  }
  
  if (filters.value.endDate) {
    const endDate = new Date(filters.value.endDate)
    endDate.setHours(23, 59, 59, 999)
    meetings = meetings.filter(meeting => new Date(meeting.created_at) <= endDate)
  }
  
  // 排序
  const [sortField, sortOrder] = filters.value.sortBy.split('_')
  meetings.sort((a, b) => {
    let aValue: any = a[sortField as keyof Meeting]
    let bValue: any = b[sortField as keyof Meeting]
    
    if (sortField === 'created_at' || sortField === 'start_time') {
      aValue = new Date(aValue || 0).getTime()
      bValue = new Date(bValue || 0).getTime()
    }
    
    if (sortField === 'title') {
      aValue = aValue?.toLowerCase() || ''
      bValue = bValue?.toLowerCase() || ''
    }
    
    if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1
    if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1
    return 0
  })
  
  return meetings
})

const totalPages = computed(() => Math.ceil(filteredMeetings.value.length / pageSize.value))

const paginatedMeetings = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredMeetings.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages: (number | string)[] = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push('...', total)
    } else if (current >= total - 3) {
      pages.push(1, '...')
      for (let i = total - 4; i <= total; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1, '...')
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i)
      }
      pages.push('...', total)
    }
  }
  
  return pages.filter(p => p !== '...' || pages.indexOf(p) === pages.lastIndexOf(p))
})

const hasActiveFilters = computed(() => {
  return filters.value.status || filters.value.startDate || filters.value.endDate
})

// 方法
const loadMeetings = async () => {
  try {
    isLoading.value = true
    await meetingStore.fetchMeetings()
  } catch (error) {
    console.error('加载会议列表失败:', error)
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

const startMeeting = async (meetingId: string) => {
  try {
    await meetingStore.startMeeting(meetingId)
  } catch (error) {
    console.error('开始会议失败:', error)
  }
}

const stopMeeting = async (meetingId: string) => {
  try {
    await meetingStore.endMeeting(meetingId)
  } catch (error) {
    console.error('停止会议失败:', error)
  }
}

const downloadMeeting = async (meetingId: string) => {
  try {
    // 显示下载选项
    const options = [
      { key: 'transcript', label: '转录文件 (JSON)' },
      { key: 'transcript_text', label: '转录文件 (TXT)' },
      { key: 'summary', label: '会议总结' },
      { key: 'audio', label: '音频文件' }
    ]
    
    // 这里可以显示一个模态框让用户选择下载类型
    // 暂时默认下载转录文件
    await meetingStore.downloadFile(meetingId, 'transcript')
  } catch (error) {
    console.error('下载文件失败:', error)
  }
}

const deleteMeeting = async (meetingId: string) => {
  if (!confirm('确定要删除这个会议吗？此操作不可恢复。')) {
    return
  }
  
  try {
    await meetingStore.deleteMeeting(meetingId)
  } catch (error) {
    console.error('删除会议失败:', error)
  }
}

const batchDelete = async () => {
  if (!confirm(`确定要删除选中的 ${selectedMeetings.value.length} 个会议吗？此操作不可恢复。`)) {
    return
  }
  
  try {
    for (const meetingId of selectedMeetings.value) {
      await meetingStore.deleteMeeting(meetingId)
    }
    selectedMeetings.value = []
  } catch (error) {
    console.error('批量删除失败:', error)
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    startDate: '',
    endDate: '',
    sortBy: 'created_at_desc'
  }
  searchQuery.value = ''
  currentPage.value = 1
}

// 监听器
watch([searchQuery, filters], () => {
  currentPage.value = 1
}, { deep: true })

// 生命周期
onMounted(() => {
  loadMeetings()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>