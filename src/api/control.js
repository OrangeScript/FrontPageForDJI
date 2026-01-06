// src/api/control.js
import http from '@/utils/request'

export const takeoff = () => http.post('/send/takeoff')
export const land = () => http.post('/send/land')
export const RTH = () => http.post('/send/RTH')

export const gotoWP = (lat, lon, alt) =>
  http.post('/send/gotoWP', { lat, lon, alt })

export const gotoWPwithPID = (lat, lon, alt, yaw) =>
  http.post('/send/gotoWPwithPID', { lat, lon, alt, yaw })

export const gotoYaw = yaw_angle =>
  http.post('/send/gotoYaw', { yaw_angle })

export const gotoAltitude = altitude =>
  http.post('/send/gotoAltitude', { altitude })

export const enableVirtualStick = () =>
  http.post('/send/enableVirtualStick')

export const abortMission = () =>
  http.post('/send/abortMission')

export const stick = (leftX = 0, leftY = 0, rightX = 0, rightY = 0) => {
  const data = `${leftX},${leftY},${rightX},${rightY}`   // ✅ CSV string
  return http.post('/send/stick', data, {
    headers: { 'Content-Type': 'text/plain' }         // 必须 text/plain
  })
}
// camera
export const startRecording = () =>
  http.post('/send/camera/startRecording')

export const stopRecording = () =>
  http.post('/send/camera/stopRecording')


// 万向节 Pitch 控制
export const gimbalPitch = (roll = 0, pitch = 0, yaw = 0) => {
  const data = `${roll},${pitch},${yaw}`   // CSV
  return http.post('/send/gimbal/pitch', data, {
    headers: { 'Content-Type': 'text/plain' }
  })
}

// 万向节 Yaw 控制
export const gimbalYaw = (roll = 0, pitch = 0, yaw = 0) => {
  const data = `${roll},${pitch},${yaw}`   // CSV
  return http.post('/send/gimbal/yaw', data, {
    headers: { 'Content-Type': 'text/plain' }
  })
}
