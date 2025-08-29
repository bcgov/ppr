<template>
  <div id="folio-box">
    <v-text-field
      id="folio-edit-txt"
      v-model="folioEditNumber"
      :error-messages="folioEditError"
      label="Folio or Reference Number"
      persistent-hint
      variant="filled"
      color="primary"
      @keypress.enter="shiftFocus()"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from 'vue'

export default defineComponent({
  props: {
    defaultFolioNumber: {
      type: String,
      default: ''
    }
  },
  emits: ['folioNumber', 'folioError'],
  setup (props, { emit }) {
    const localState = reactive({
      folioEdit: false,
      folioEditError: '',
      folioEditHint: `${50 - props.defaultFolioNumber?.length}`,
      folioEditNumber: props.defaultFolioNumber,
      folioNumber: props.defaultFolioNumber
    })

    watch(() => localState.folioEditNumber, (val: string) => {
      if (val?.length > 50) {
        localState.folioEditError = 'Maximum 50 characters reached'
        emit('folioError', true)
      } else {
        localState.folioEditError = ''
        localState.folioEditHint = `${50 - val?.length}`
        localState.folioNumber = localState.folioEditNumber
        emit('folioError', false)
      }
    })
    watch(() => localState.folioNumber, (val: string) => {
      emit('folioNumber', val)
    })

    // when enter pressed on the folio number, either focus on the input or the button if the input is disabled
    const shiftFocus = () => {
      if (!document.getElementById('search-bar-field')?.getAttribute('disabled')) {
        document.getElementById('search-bar-field').focus()
      } else if (document.querySelector('.search-bar-btn')) {
        document.querySelector<HTMLElement>('.search-bar-btn').focus()
      }
    }

    return {
      shiftFocus,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/theme.scss' as *;
@media (min-width: 960px) {
  #folio-box {
    width: 250px;
  }
}
</style>
