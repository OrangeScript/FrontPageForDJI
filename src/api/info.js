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
// import { WS_BASE } from '../utils/request'
const WS_BASE = 'ws://192.168.246.214:8765'
export function connectTelemetry() {
  socket = new WebSocket(WS_BASE)

  socket.onmessage = e => {
    try {
      const data = JSON.parse(e.data)
      Object.assign(telemetry, data)
    } catch (err) {
      console.error('Telemetry parse error', err)
    }
  }

  socket.onerror = e => console.error('Telemetry socket error', e)
  socket.onclose = () => console.warn('Telemetry socket closed')
}
