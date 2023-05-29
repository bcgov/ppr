// vue-demi-shim.d.ts
import Vue from 'vue-demi'

// Add type declarations for the Vue 3 composition API
declare module 'vue-demi' {
  // @ts-ignore
  export * from 'vue'
}

// Declare global properties and types
declare module 'vue/types/vue' {
  interface Vue {
    // Add any additional properties or types you need
  }
}
