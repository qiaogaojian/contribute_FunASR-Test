<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- 全局加载指示器 -->
    <Transition name="fade">
      <div
        v-if="isLoading"
        class="fixed inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm"
      >
        <div class="text-center">
          <div class="loading w-8 h-8 mx-auto mb-4"></div>
          <p class="text-gray-600">加载中...</p>
        </div>
      </div>
    </Transition>

    <!-- 全局通知 -->
    <NotificationContainer />

    <!-- 主要内容 -->
    <RouterView v-slot="{ Component, route }">
      <Transition
        :name="(route.meta?.transition as string) || 'fade'"
        mode="out-in"
        appear
      >
        <component :is="Component" :key="route.path" />
      </Transition>
    </RouterView>

    <!-- 全局模态框 -->
    <ModalContainer />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { RouterView } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useWebSocketStore } from '@/stores/websocket'
import NotificationContainer from '@/components/common/NotificationContainer.vue'
import ModalContainer from '@/components/common/ModalContainer.vue'

const appStore = useAppStore()
const wsStore = useWebSocketStore()

const isLoading = computed(() => appStore.isLoading)

// 应用初始化
onMounted(async () => {
  try {
    // 初始化应用
    await appStore.initialize()
    
    // 连接WebSocket
    await wsStore.connect()
    
    console.log('应用初始化完成')
  } catch (error) {
    console.error('应用初始化失败:', error)
  }
})

// 清理资源
onUnmounted(() => {
  wsStore.disconnect()
})

// 监听页面可见性变化
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    // 页面隐藏时的处理
    console.log('页面隐藏')
  } else {
    // 页面显示时的处理
    console.log('页面显示')
    // 重新连接WebSocket（如果需要）
    if (!wsStore.isConnected) {
      wsStore.connect()
    }
  }
})

// 监听网络状态变化
window.addEventListener('online', () => {
  console.log('网络已连接')
  appStore.setOnlineStatus(true)
  // 重新连接WebSocket
  if (!wsStore.isConnected) {
    wsStore.connect()
  }
})

window.addEventListener('offline', () => {
  console.log('网络已断开')
  appStore.setOnlineStatus(false)
})
</script>

<style scoped>
/* 页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.3s ease;
}

.slide-left-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-left-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}

.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.3s ease;
}

.slide-right-enter-from {
  transform: translateX(-100%);
  opacity: 0;
}

.slide-right-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  transform: translateY(100%);
  opacity: 0;
}

.slide-up-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}

.scale-enter-active,
.scale-leave-active {
  transition: all 0.3s ease;
}

.scale-enter-from,
.scale-leave-to {
  transform: scale(0.9);
  opacity: 0;
}
</style>