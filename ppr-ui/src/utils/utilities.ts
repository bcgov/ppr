export function isSigningIn (): boolean {
  const path = window.location.pathname
  return path.includes('/login') || path.includes('/signin')
}

export function isSigningOut (): boolean {
  const path = window.location.pathname
  return path.includes('/signout')
}
