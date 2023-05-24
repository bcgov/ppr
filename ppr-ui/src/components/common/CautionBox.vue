<template>
  <div :class="$style['caution-box']" class="caution-box">
    <p class="ma-0 pa-4">
      <b>{{ importantWord }}:</b> {{ msg }}
    </p>
  </div>
</template>

<script lang="ts">
// external
import {
  defineComponent,
  reactive,
  toRefs
} from 'vue-demi'

export default defineComponent({
  name: 'CautionBox',
  props: {
    setMsg: String,
    setImportantWord: {
      type: String,
      default: 'Important'
    }
  },
  setup (props) {
    const localState = reactive({
      msg: props.setMsg,
      importantWord: props.setImportantWord
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
