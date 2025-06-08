<template>
  <Teleport to="body">
    <TransitionGroup name="modal" tag="div">
      <div
        v-for="modal in modals"
        :key="modal.id"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click="handleBackdropClick(modal)"
      >
        <!-- 背景遮罩 -->
        <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>
        
        <!-- 模态框内容 -->
        <div class="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
          <div
            :class="[
              'relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all',
              getSizeClass(modal.size),
              modal.class
            ]"
            @click.stop
          >
            <!-- 头部 -->
            <div v-if="modal.title || modal.closable !== false" class="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
              <div class="flex items-center justify-between">
                <h3 v-if="modal.title" class="text-lg font-medium leading-6 text-gray-900">
                  {{ modal.title }}
                </h3>
                <button
                  v-if="modal.closable !== false"
                  @click="closeModal(modal.id)"
                  class="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  <span class="sr-only">关闭</span>
                  <XMarkIcon class="h-6 w-6" />
                </button>
              </div>
            </div>
            
            <!-- 内容 -->
            <div class="bg-white px-4 pb-4 pt-5 sm:p-6">
              <component
                v-if="modal.component"
                :is="modal.component"
                v-bind="modal.props"
                @close="closeModal(modal.id)"
              />
              <div v-else-if="modal.content" v-html="modal.content"></div>
            </div>
            
            <!-- 底部按钮 -->
            <div v-if="modal.actions && modal.actions.length > 0" class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
              <button
                v-for="(action, index) in modal.actions"
                :key="index"
                :class="[
                  'inline-flex w-full justify-center rounded-md px-3 py-2 text-sm font-semibold shadow-sm sm:ml-3 sm:w-auto',
                  getActionClass(action.type)
                ]"
                @click="handleAction(modal.id, action)"
              >
                {{ action.label }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { useAppStore } from '@/stores/app'
import type { Modal, ModalAction } from '@/stores/app'

const appStore = useAppStore()

const modals = computed(() => appStore.modals)

const closeModal = (id: string) => {
  appStore.closeModal(id)
}

const handleBackdropClick = (modal: Modal) => {
  if (modal.closable !== false) {
    closeModal(modal.id)
  }
}

const handleAction = (modalId: string, action: ModalAction) => {
  if (action.handler) {
    action.handler()
  }
  if (action.close !== false) {
    closeModal(modalId)
  }
}

const getSizeClass = (size?: string) => {
  switch (size) {
    case 'sm':
      return 'sm:max-w-sm sm:w-full'
    case 'md':
      return 'sm:max-w-md sm:w-full'
    case 'lg':
      return 'sm:max-w-lg sm:w-full'
    case 'xl':
      return 'sm:max-w-xl sm:w-full'
    case '2xl':
      return 'sm:max-w-2xl sm:w-full'
    case 'full':
      return 'sm:max-w-full sm:w-full'
    default:
      return 'sm:max-w-lg sm:w-full'
  }
}

const getActionClass = (type?: string) => {
  switch (type) {
    case 'primary':
      return 'bg-blue-600 text-white hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600'
    case 'danger':
      return 'bg-red-600 text-white hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600'
    case 'success':
      return 'bg-green-600 text-white hover:bg-green-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-green-600'
    default:
      return 'bg-white text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50'
  }
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .relative,
.modal-leave-to .relative {
  transform: scale(0.95) translateY(-20px);
}

.modal-move {
  transition: transform 0.3s ease;
}
</style>