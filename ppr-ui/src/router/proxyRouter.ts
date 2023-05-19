// utils.js
import { getCurrentInstance } from 'vue'

export function useRoute () {
  const { proxy } = getCurrentInstance()
  return proxy?.$route
}
export function useRouter () {
  const { proxy } = getCurrentInstance()
  return proxy?.$router
}
