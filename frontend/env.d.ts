/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_WS_BASE_URL: string
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_VERSION: string
  readonly VITE_APP_DESCRIPTION: string
  readonly VITE_ENABLE_MOCK: string
  readonly VITE_ENABLE_DEVTOOLS: string
  readonly VITE_LOG_LEVEL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// Vue 组件类型声明
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// 静态资源类型声明
declare module '*.svg' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent
  export default component
}

declare module '*.png' {
  const src: string
  export default src
}

declare module '*.jpg' {
  const src: string
  export default src
}

declare module '*.jpeg' {
  const src: string
  export default src
}

declare module '*.gif' {
  const src: string
  export default src
}

declare module '*.webp' {
  const src: string
  export default src
}

declare module '*.ico' {
  const src: string
  export default src
}

// CSS 模块类型声明
declare module '*.module.css' {
  const classes: { readonly [key: string]: string }
  export default classes
}

declare module '*.module.scss' {
  const classes: { readonly [key: string]: string }
  export default classes
}

declare module '*.module.sass' {
  const classes: { readonly [key: string]: string }
  export default classes
}

declare module '*.module.less' {
  const classes: { readonly [key: string]: string }
  export default classes
}

// Web API 扩展
interface Navigator {
  readonly userAgentData?: {
    readonly brands: Array<{
      readonly brand: string
      readonly version: string
    }>
    readonly mobile: boolean
    readonly platform: string
  }
}

// 全局类型声明
declare global {
  interface Window {
    // 可能的全局变量
    __APP_VERSION__?: string
    __BUILD_TIME__?: string
    
    // 第三方库
    webkitAudioContext?: typeof AudioContext
    
    // Electron API
    electronAPI?: {
      selectDirectory: () => Promise<string>
      openExternal: (url: string) => Promise<void>
      getSystemInfo: () => Promise<any>
      [key: string]: any
    }
  }
}

export {}