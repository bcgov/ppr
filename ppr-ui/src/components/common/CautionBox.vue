<template>
  <div :class="$style['caution-box']" class="caution-box">
    <p class="ma-0 pa-4">
      <b>Important:</b> {{ msg }}
    </p>
  </div>
</template>

<script lang="ts">
// external
import {
  defineComponent,
  reactive,
  toRefs
} from '@vue/composition-api'

export default defineComponent({
  name: 'CautionBox',
  props: {
    setMsg: String
  },
  setup (props) {
    const localState = reactive({
      msg: props.setMsg
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.caution-box {
  background-color: $BCgovGold0;
  border: 1px solid $BCgovGold5;
  font-size: 0.875rem;
}
</style>
