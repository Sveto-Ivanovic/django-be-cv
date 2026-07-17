import type { Router } from 'vue-router'

let routerInstance: Router | null = null

export function setRouterInstance(router: Router) {
  routerInstance = router
}

export function getRouterInstance(): Router | null {
  return routerInstance
}