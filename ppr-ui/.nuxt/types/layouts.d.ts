import type { ComputedRef, MaybeRef } from 'vue'
export type LayoutKey = string
declare module "../../node_modules/.pnpm/nuxt@3.14.0_@parcel+watcher@2.5.0_@types+node@22.10.1_db0@0.2.1_eslint@8.57.1_ioredis@5.4.1_m_bzcb3akg2pabvobpacd3o26vsm/node_modules/nuxt/dist/pages/runtime/composables" {
  interface PageMeta {
    layout?: MaybeRef<LayoutKey | false> | ComputedRef<LayoutKey | false>
  }
}