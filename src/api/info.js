// src/api/info.js
import { reactive } from 'vue'

export const telemetry = reactive({
  speed: {},
  heading: 0,
  attitude: {},
  location: {},
  gimbalAttitude: {},
  batteryLevel: 0,
  satelliteCount: 0,
  flightMode: '',
  distanceToHome: 0,
  remainingFlightTime: 0
})

let socket = null
const WS_BASE = 'ws://192.168.246.214:8765'
export function connectTelemetry() {
  if (socket) socket.close()
    
    // 指定 'binary' 子协议可以告诉 websockify 我们准备好处理二进制了
    socket = new WebSocket(WS_BASE, ['binary'])
    
    let buffer = '' 
    
    socket.onmessage = async (e) => {
    console.log('收到数据类型:', e.data.constructor.name)
    // 1. 模拟 Python 的 .decode('utf-8')
    // 这一步是核心：不管发来什么，都统一转成 String
    let textData = ''
    if (e.data instanceof Blob) {
        textData = await e.data.text() // <--- 这就是 JS 版的 decode()
    } else {
        textData = e.data // 如果本来就是文本，直接用
    }
    console.log('收到数据:', textData)
    // 2. 下面是你原本的逻辑 (完全正确，不用改)
    buffer += textData
    
    let newlineIndex = buffer.indexOf('\n')
    while (newlineIndex !== -1) {
      const line = buffer.slice(0, newlineIndex).trim()
      buffer = buffer.slice(newlineIndex + 1)
      if (line) {
        try {
          const data = JSON.parse(line)
          Object.assign(telemetry, data)
        } catch (err) {
          console.warn('JSON解析错误:', line)
        }
      }
      newlineIndex = buffer.indexOf('\n')
    }
  }

  socket.onopen = () => console.log('✅ 遥测链路已连接')
  socket.onerror = e => console.error('❌ 连接报错', e)
}
