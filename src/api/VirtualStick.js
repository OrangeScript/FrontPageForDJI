import request from '@/utils/request'

export function sendVS(payload) {
  return request.post('/drone/vs', {
    mode: payload.mode ?? 'NORMAL',
    lv: payload.lv ?? 0,
    lh: payload.lh ?? 0,
    rv: payload.rv ?? 0,
    rh: payload.rh ?? 0,
    roll: payload.roll ?? 0,
    pitch: payload.pitch ?? 0,
    yaw: payload.yaw ?? 0,
    throttle: payload.throttle ?? 0
  })
}
