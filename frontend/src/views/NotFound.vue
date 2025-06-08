<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 text-center">
      <div>
        <h1 class="text-9xl font-bold text-gray-300">404</h1>
        <h2 class="mt-6 text-3xl font-extrabold text-gray-900">
          页面未找到
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          抱歉，您访问的页面不存在或已被移除。
        </p>
      </div>
      
      <div class="mt-8 space-y-4">
        <button
          @click="goBack"
          class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <ArrowLeftIcon class="h-5 w-5 mr-2" />
          返回上一页
        </button>
        
        <router-link
          to="/"
          class="group relative w-full flex justify-center py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <HomeIcon class="h-5 w-5 mr-2" />
          回到首页
        </router-link>
      </div>
      
      <div class="mt-8">
        <p class="text-xs text-gray-500">
          如果您认为这是一个错误，请联系我们的技术支持。
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ArrowLeftIcon, HomeIcon } from '@heroicons/vue/24/outline'

const router = useRouter()

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}
</script>