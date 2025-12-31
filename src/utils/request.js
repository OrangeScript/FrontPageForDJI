import axios from "axios";

const request = axios.create({
    baseURL:'http://localhost:8080',
    timeout: 60000
})

request.interceptors.response.use(
    (response) => {
        return response.data
    },
    (error) => {
        return Promise.reject(error)
    }
)

export default request