# FunASR 会议助手 - 前端应用

基于 Vue 3 + TypeScript + Vite 构建的智能会议转录助手前端应用。

## 🚀 功能特性

### 核心功能
- 🎤 **实时语音转录** - 支持多语言实时语音识别
- 📝 **会议记录管理** - 创建、编辑、删除会议记录
- 📊 **会议统计分析** - 会议时长、参与人数等统计
- 🔄 **实时同步** - WebSocket 实时数据同步
- 📱 **响应式设计** - 支持桌面端和移动端

### 高级功能
- 🎯 **智能总结** - AI 自动生成会议总结
- 👥 **多人协作** - 支持多人同时参与会议
- 🎨 **主题切换** - 支持明暗主题切换
- 🌍 **多语言支持** - 界面多语言国际化
- 📁 **文件管理** - 音频文件上传和下载

## 🛠️ 技术栈

### 前端框架
- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - 类型安全的 JavaScript 超集
- **Vite** - 下一代前端构建工具

### UI 组件
- **Tailwind CSS** - 实用优先的 CSS 框架
- **Headless UI** - 无样式的可访问 UI 组件
- **Lucide Vue** - 美观的图标库

### 状态管理
- **Pinia** - Vue 3 官方状态管理库
- **VueUse** - Vue 组合式 API 工具集

### 网络通信
- **Axios** - HTTP 客户端
- **WebSocket** - 实时双向通信

### 开发工具
- **ESLint** - 代码质量检查
- **Prettier** - 代码格式化
- **Vitest** - 单元测试框架

## 📦 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── components/         # 可复用组件
│   ├── views/             # 页面组件
│   ├── router/            # 路由配置
│   ├── stores/            # 状态管理
│   ├── utils/             # 工具函数
│   ├── types/             # TypeScript 类型定义
│   ├── assets/            # 资源文件
│   ├── App.vue            # 根组件
│   └── main.ts            # 应用入口
├── tests/                 # 测试文件
├── .env                   # 环境变量
├── .env.development       # 开发环境变量
├── .env.production        # 生产环境变量
├── vite.config.ts         # Vite 配置
├── tailwind.config.js     # Tailwind 配置
├── tsconfig.json          # TypeScript 配置
└── package.json           # 项目依赖
```

## 🚀 快速开始

### 环境要求
- Node.js >= 18.0.0
- npm >= 9.0.0

### 安装依赖
```bash
npm install
```

### 开发环境运行
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

### 预览生产版本
```bash
npm run preview
```

### 代码检查
```bash
npm run lint
```

### 代码格式化
```bash
npm run format
```

### 运行测试
```bash
npm run test
```

## ⚙️ 配置说明

### 环境变量

项目使用环境变量进行配置，主要配置项包括：

```bash
# API 配置
VITE_API_BASE_URL=http://localhost:8000    # 后端 API 地址
VITE_WS_BASE_URL=ws://localhost:8000       # WebSocket 地址

# 功能开关
VITE_ENABLE_DEBUG=true                     # 调试模式
VITE_ENABLE_ANALYTICS=false                # 分析统计

# 音频配置
VITE_AUDIO_SAMPLE_RATE=16000               # 音频采样率
VITE_AUDIO_CHANNELS=1                      # 音频声道数

# 转录配置
VITE_DEFAULT_LANGUAGE=zh                   # 默认转录语言
VITE_SUPPORTED_LANGUAGES=zh,en,ja,ko       # 支持的语言
```

### 主题配置

项目支持明暗主题切换，可以通过以下方式配置：

1. **系统主题** - 自动跟随系统主题
2. **明亮主题** - 手动设置明亮主题
3. **暗黑主题** - 手动设置暗黑主题

### 语言配置

支持多语言界面，目前支持：
- 简体中文 (zh-CN)
- English (en-US)
- 日本語 (ja-JP)
- 한국어 (ko-KR)

## 🔧 开发指南

### 组件开发

1. **组件命名** - 使用 PascalCase 命名
2. **文件结构** - 每个组件一个文件夹
3. **类型定义** - 使用 TypeScript 定义 Props 和 Emits
4. **样式规范** - 使用 Tailwind CSS 类名

### 状态管理

使用 Pinia 进行状态管理：

```typescript
// stores/example.ts
import { defineStore } from 'pinia'

export const useExampleStore = defineStore('example', {
  state: () => ({
    // 状态定义
  }),
  getters: {
    // 计算属性
  },
  actions: {
    // 方法定义
  }
})
```

### API 调用

使用封装的 API 服务：

```typescript
import { apiService } from '@/utils/api'

// GET 请求
const data = await apiService.get('/api/meetings')

// POST 请求
const result = await apiService.post('/api/meetings', {
  title: '会议标题',
  description: '会议描述'
})
```

### WebSocket 连接

使用 WebSocket Store 管理连接：

```typescript
import { useWebSocketStore } from '@/stores/websocket'

const wsStore = useWebSocketStore()

// 连接
wsStore.connect()

// 发送消息
wsStore.sendMessage({
  type: 'join_meeting',
  data: { meetingId: '123' }
})

// 断开连接
wsStore.disconnect()
```

## 🧪 测试

### 单元测试

使用 Vitest 进行单元测试：

```bash
# 运行测试
npm run test

# 监听模式
npm run test:watch

# 覆盖率报告
npm run test:coverage
```

### 测试文件结构

```
tests/
├── unit/                  # 单元测试
│   ├── components/        # 组件测试
│   ├── stores/           # 状态管理测试
│   └── utils/            # 工具函数测试
└── e2e/                  # 端到端测试
```

## 📱 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 🚀 部署

### 构建优化

生产环境构建会自动进行以下优化：

1. **代码分割** - 按路由和依赖分割代码
2. **资源压缩** - 压缩 JavaScript、CSS 和图片
3. **Tree Shaking** - 移除未使用的代码
4. **缓存优化** - 生成带哈希的文件名

### 部署到静态服务器

```bash
# 构建
npm run build

# 部署 dist 目录到服务器
```

### Docker 部署

```dockerfile
# Dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范

- 遵循 ESLint 和 Prettier 配置
- 编写有意义的提交信息
- 添加必要的测试用例
- 更新相关文档

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Vite](https://vitejs.dev/) - 下一代前端构建工具
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的 CSS 框架
- [FunASR](https://github.com/alibaba-damo-academy/FunASR) - 语音识别工具包

## 📞 联系我们

- 项目地址：[GitHub](https://github.com/funasr/meeting-assistant)
- 问题反馈：[Issues](https://github.com/funasr/meeting-assistant/issues)
- 邮箱：support@funasr.com

---

**FunASR 会议助手** - 让会议更智能，让记录更简单！