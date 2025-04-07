// "ambient module" - used to describe modules written in JS
// (needed for unit test files to find component modules)
// Extract ValidationRule Type from vuetify. Component used for extraction is arbitrary providing it has the rules prop
import type { VTextField } from 'vuetify/lib/components/VTextField/index.mjs'

declare module '*.vue' {
  // @ts-expect-error: Type mismatch due to module resolution issue
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<Record<string,unknown>, Record<string,unknown>, unknown>
  export default component
}
type UnwrapReadonlyArray<A> = A extends Readonly<Array<infer I>> ? I : A;
type ValidationRule = UnwrapReadonlyArray<InstanceType<typeof VTextField>['rules']>

