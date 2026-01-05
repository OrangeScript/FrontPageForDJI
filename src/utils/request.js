import axios from "axios";
// src/config/server.js
const REMOTE_IP = import.meta.env.VITE_API_REMOTE_IP
export const HTTP_BASE = `http://${REMOTE_IP}:8080`
export const WS_BASE   = `ws://${REMOTE_IP}:8081`
export const RTSP_STREAM_URL_WITH_AUTH = (
  user = 'aaa',
  pass = 'aaa'
) =>
  `rtsp://${user}:${pass}@${REMOTE_IP}:8554/streaming/live/1`
  
const http = axios.create({
    baseURL:HTTP_BASE,
    timeout: 60000
})

http.interceptors.response.use(
    (response) => {
        return response.data
    },
    (error) => {
        return Promise.reject(error)
    }
)

export default http