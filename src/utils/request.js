import axios from "axios";
// src/config/server.js
export const HTTP_BASE = import.meta.env.VITE_API_HTTP_BASE
export const WS_BASE   = import.meta.env.VITE_API_WS_BASE

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