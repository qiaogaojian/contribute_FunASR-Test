import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAppStore } from '@/stores/app'

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: {
      title: '首页',
      transition: 'fade'
    }
  },
  {
    path: '/meetings',
    name: 'Meetings',
    component: () => import('@/views/MeetingList.vue'),
    meta: {
      title: '会议列表',
      transition: 'slide-left'
    }
  },
  {
    path: '/meetings/new',
    name: 'NewMeeting',
    component: () => import('@/views/NewMeeting.vue'),
    meta: {
      title: '创建会议',
      transition: 'slide-up'
    }
  },
  {
    path: '/meetings/:id',
    name: 'MeetingDetail',
    component: () => import('@/views/MeetingDetail.vue'),
    meta: {
      title: '会议详情',
      transition: 'slide-left'
    },
    props: true
  },
  {
    path: '/meetings/:id/record',
    name: 'MeetingRecord',
    component: () => import('@/views/MeetingRecord.vue'),
    meta: {
      title: '会议录制',
      transition: 'scale'
    },
    props: true
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: {
      title: '设置',
      transition: 'slide-right'
    }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/About.vue'),
    meta: {
      title: '关于',
      transition: 'fade'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: {
      title: '页面未找到',
      transition: 'fade'
    }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // 如果有保存的位置，返回到该位置
    if (savedPosition) {
      return savedPosition
    }
    // 如果有锚点，滚动到锚点
    if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth'
      }
    }
    // 否则滚动到顶部
    return { top: 0 }
  }
})

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  const appStore = useAppStore()
  
  // 设置加载状态
  appStore.setLoading(true)
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 智能会议助手`
  } else {
    document.title = '智能会议助手'
  }
  
  // 这里可以添加权限检查逻辑
  // if (to.meta.requiresAuth && !userStore.isAuthenticated) {
  //   next('/login')
  //   return
  // }
  
  next()
})

// 全局后置守卫
router.afterEach((to, from) => {
  const appStore = useAppStore()
  
  // 延迟关闭加载状态，确保页面渲染完成
  setTimeout(() => {
    appStore.setLoading(false)
  }, 300)
  
  // 页面访问统计
  console.log(`导航到: ${to.path}`)
})

// 路由错误处理
router.onError((error) => {
  console.error('路由错误:', error)
  const appStore = useAppStore()
  appStore.setLoading(false)
})

export default router