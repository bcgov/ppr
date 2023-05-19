<template>
  <v-snackbar
    class="my-reg-snackbar"
    timeout="4000"
    transition="fade"
    v-model="showSnackbar"
  >
    <v-row no-gutters>
      <v-col cols="11">
        {{ message }}
      </v-col>
      <v-col cols="1">
        <v-btn
          class="snackbar-btn-close float-right ma-0 mr-n2 pa-0"
          icon
          :ripple="false"
          small
          @click="showSnackbar = false"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </v-snackbar>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
  watch
} from 'vue'

export default defineComponent({
  name: 'BaseSnackbar',
  props: {
    setMessage: String,
    toggleSnackbar: { default: false }
  },
  setup (props) {
    const localState = reactive({
      showSnackbar: false,
      message: computed(() => {
        return props.setMessage
      })
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

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
