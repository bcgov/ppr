<template>
  <v-row justify="center" no-gutters :class="{ 'reverse': reverseButtons }">
    <v-col v-if="cancelText" cols="auto">
      <v-btn
        id="cancel-btn"
        class="dialog-btn"
        :class="reverseButtons ? 'ml-3 primary' : 'outlined'"
        outlined
        @click="proceed(false)">
        {{ cancelText }}
      </v-btn>
    </v-col>
    <v-col v-if="acceptText" cols="auto">
      <v-btn
        id="accept-btn"
        class="dialog-btn"
        :class="reverseButtons ? 'outlined' : 'ml-3 primary'"
        @click="proceed(true)">
        {{ acceptText }}
      </v-btn>
    </v-col>
  </v-row>
</template>

<script lang="ts">
// external
import {
  computed,
  defineComponent,
  reactive,
  toRefs
} from 'vue-demi'

export default defineComponent({
  name: 'DialogButtons',
  props: {
    setAcceptText: String,
    setCancelText: String,
    reverseButtons: Boolean
  },
  emits: ['proceed'],
  setup (props, { emit }) {
    const localState = reactive({
      acceptText: computed(() => {
        return props.setAcceptText || ''
      }),
      cancelText: computed(() => {
        return props.setCancelText || ''
      })
    })
    const proceed = (val: boolean) => {
      emit('proceed', val)
    }

    return {
      proceed,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#accept-btn {
  font-weight: normal;
}

.reverse {
  display: flex;
  flex-direction: row-reverse;
}
</style>
