import axios from "axios";
// src/config/server.js
export const HTTP_BASE = `/api`
export const WS_BASE   = `ws://localhost:8080/ws/telemetry`

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