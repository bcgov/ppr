<template>
  <v-card
    id="tabbed-container"
    flat
  >
    <v-tabs
      v-model="tab"
      height="55"
      alignTabs="center"
      grow
    >
      <v-tab
        v-for="(tabContent, index) in tabConfig"
        :key="`${tabContent.label}-${index}`"
        :value="index"
        class="tab upper-border mt-1"
        :ripple="false"
      >
        <v-icon
          class="mr-1"
          size="22"
        >
          {{ tabContent.icon }}
        </v-icon>
        <b>{{ tabContent.label }}</b>
      </v-tab>
    </v-tabs>

    <!-- Window Items -->
    <v-window
      v-model="tab"
      class="rounded-bottom bg-white px-6"
    >
      <v-window-item
        v-for="(item, index) in tabConfig"
        :key="`tab-window-${index}`"
        :value="index"
      >
        <slot :name="`tab-${index}`" />
      </v-window-item>
    </v-window>
  </v-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'

/** Props **/
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(defineProps<{
  tabConfig?: any
}>(), {
  tabConfig: {}
})

/** Local Properties **/
const tab = ref(0)

</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
#tabbed-container {
  background-color: inherit;
}
.tab {
  min-height: 55px!important;
  background-color: $app-lt-blue;
  font-size: 1rem;
  letter-spacing: 0;
  text-transform: none!important;
  border-top-left-radius: 4px!important;
  border-top-right-radius: 4px!important;
  &:hover:not(.v-tab--selected) {
    background-color: $app-lt-blue-hover;
  }
  .v-icon {
    color: $app-dk-blue;
  }
}
.v-tab--selected {
  background-color: white;
  color: $gray9;
  pointer-events: none;
}
.upper-border {
  min-height: 55px;
  max-height: 55px;
  margin: 0 2.5px;
}
.v-window {
  min-height: 400px
}
</style>
