<template>
  <v-snackbar
    :model-value="showSnackbar"
    class="my-reg-snackbar"
    :timeout="4000"
    transition="fade"
  >
    {{ setMessage }}
    <template #actions>
      <v-btn
        class="snackbar-btn-close float-right ma-0 pa-0"
        variant="plain"
        :ripple="false"
        size="small"
        @click="showSnackbar = false"
      >
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </template>
  </v-snackbar>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  watch
} from 'vue'

export default defineComponent({
  name: 'BaseSnackbar',
  props: {
    setMessage: { type: String, default: '' },
    toggleSnackbar: { type: Boolean, default: false }
  },
  setup (props) {
    const localState = reactive({
      showSnackbar: false
    })

    watch(() => props.toggleSnackbar, () => {
      localState.showSnackbar = true
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
