<template>
  <v-container class="pa-0">
    <v-row v-if="baseText" no-gutters>
      <v-col cols="auto">
        <p class="dialog-text ma-0" v-html="baseText" />
      </v-col>
    </v-row>
    <v-row v-if="extraText.length > 0" class="pt-5" no-gutters>
      <v-col cols="auto">
        <p v-for="(text, index) in extraText" class="dialog-text ma-0" :key="index" v-html="text" />
      </v-col>
    </v-row>
    <v-row v-if="hasContactInfo" class="pt-5" no-gutters>
      <v-col>
        <error-contact />
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
} from 'vue-demi'
// local
import ErrorContact from '@/components/common/ErrorContact.vue'

export default defineComponent({
  name: 'DialogContent',
  components: {
    ErrorContact
  },
  props: {
    setBaseText: { default: '' },
    setExtraText: { default: () => [] as String[] },
    setHasContactInfo: { default: false }
  },
  setup (props) {
    const localState = reactive({
      baseText: computed(() => {
        return props.setBaseText
      }),
      extraText: computed(() => {
        return props.setExtraText
      }),
      hasContactInfo: computed(() => {
        return props.setHasContactInfo
      })
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
