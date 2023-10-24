// "ambient module" - used to describe modules written in JS
// (needed for unit test files to find component modules)
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<Record<string,unknown>, Record<string,unknown>, unknown>
  export default component
}
