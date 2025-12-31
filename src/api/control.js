
import request from '@/utils/request'


export const COMMAND = {
  TAKE_OFF: 'TAKE_OFF',
  LAND: 'LAND',
  GO_HOME: 'GO_HOME',
  HOVER: 'HOVER',
  EMERGENCY_STOP: 'EMERGENCY_STOP',
  MOVE: 'MOVE',
  ROTATE: 'ROTATE'
}


function send(data) {
  return request.post('/drone/control', data)
}


export const takeOff = () => send({ command: COMMAND.TAKE_OFF })
export const land = () => send({ command: COMMAND.LAND })
export const goHome = () => send({ command: COMMAND.GO_HOME })
export const hover = () => send({ command: COMMAND.HOVER })
export const emergencyStop = () => send({ command: COMMAND.EMERGENCY_STOP })



export function move({ forward = 0, right = 0, up = 0, speed = 1 }) {
  return send({
    command: COMMAND.MOVE,
    forward,
    right,
    up,
    speed
  })
}

export function rotate(yaw = 0) {
  return send({
    command: COMMAND.ROTATE,
    yaw
  })
}
