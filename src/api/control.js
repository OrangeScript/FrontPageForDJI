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

export const stick = (leftX, leftY, rightX, rightY) =>
  http.post('/send/stick', { leftX, leftY, rightX, rightY })

// camera
export const startRecording = () =>
  http.post('/send/camera/startRecording')

export const stopRecording = () =>
  http.post('/send/camera/stopRecording')
