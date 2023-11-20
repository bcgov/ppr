<template>
  <v-container class="pa-0">
    <v-row
      v-if="setBaseText"
      noGutters
    >
      <v-col cols="auto">
        <p
          class="dialog-text ma-0"
          v-html="setBaseText"
        />
      </v-col>
    </v-row>
    <v-row
      v-if="setExtraText.length > 0"
      class="pt-5"
      noGutters
    >
      <v-col cols="auto">
        <p
          v-for="(text, index) in setExtraText"
          :key="index"
          class="dialog-text ma-0"
          v-html="text"
        />
      </v-col>
    </v-row>
    <v-row
      v-if="setHasContactInfo"
      class="pt-5"
      noGutters
    >
      <v-col>
        <ErrorContact />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
// external
import {
  computed,
  defineComponent,
  reactive,
  toRefs
} from 'vue'
// local
import ErrorContact from '@/components/common/ErrorContact.vue'

export default defineComponent({
  name: 'DialogContent',
  components: {
    ErrorContact
  },
  props: {
    setBaseText: { type: String, default: '' },
    setExtraText: { type: Array as () => string[], default: () => [] as string[] },
    setHasContactInfo: { type: Boolean, default: false }
  },
  setup () {
    const localState = reactive({})

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
