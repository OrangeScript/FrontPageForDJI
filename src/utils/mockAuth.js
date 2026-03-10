/**
 * 前端 Mock 认证系统 —— 无需后端/数据库
 * 所有用户数据存储在 localStorage 中
 */

const STORAGE_KEY = 'dji_cmd_users'
const AUTH_KEY    = 'dji_cmd_auth'

/* ---------- 预置用户 ---------- */
const DEFAULT_USERS = [
  { username: 'admin',    password: 'admin123',  role: '系统管理员', email: 'admin@uav-cmd.mil',    createTime: '2025-01-15' },
  { username: 'operator', password: 'op123',     role: '任务操作员', email: 'operator@uav-cmd.mil', createTime: '2025-03-20' },
  { username: 'pilot',    password: 'pilot123',  role: '飞行员',     email: 'pilot@uav-cmd.mil',    createTime: '2025-06-10' },
]

/* ---------- 用户列表 ---------- */
export function getUsers () {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULT_USERS))
    return [...DEFAULT_USERS]
  }
  return JSON.parse(raw)
}

/* ---------- 注册 ---------- */
export function registerUser ({ username, password, email, role = '操作员' }) {
  const users = getUsers()
  if (users.find(u => u.username === username)) {
    return { success: false, message: '操作员编号已存在' }
  }
  const newUser = { username, password, email, role, createTime: new Date().toISOString().slice(0, 10) }
  users.push(newUser)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(users))
  return { success: true, message: '注册成功，请返回登录' }
}

/* ---------- 登录 ---------- */
export function loginUser (username, password) {
  const users = getUsers()
  const user = users.find(u => u.username === username && u.password === password)
  if (!user) return { success: false, message: '操作员编号或访问密钥错误' }

  const payload = {
    username: user.username,
    role: user.role,
    token: `MOCK-JWT-${Date.now()}-${Math.random().toString(36).slice(2, 8).toUpperCase()}`,
    loginTime: new Date().toISOString(),
  }
  localStorage.setItem(AUTH_KEY, JSON.stringify(payload))
  return { success: true, data: payload }
}

/* ---------- 修改密码 ---------- */
export function updatePassword (username, oldPwd, newPwd) {
  const users = getUsers()
  const idx = users.findIndex(u => u.username === username && u.password === oldPwd)
  if (idx === -1) return { success: false, message: '操作员编号或旧密钥错误' }
  users[idx].password = newPwd
  localStorage.setItem(STORAGE_KEY, JSON.stringify(users))
  return { success: true, message: '访问密钥已更新' }
}

/* ---------- 鉴权工具 ---------- */
export function isAuthenticated () {
  return !!localStorage.getItem(AUTH_KEY)
}

export function getAuthUser () {
  const raw = localStorage.getItem(AUTH_KEY)
  return raw ? JSON.parse(raw) : null
}

export function logout () {
  localStorage.removeItem(AUTH_KEY)
}
