<template>
  <div id="folio-box">
            <v-text-field id="folio-edit-txt"
                          class="py-0 my-0"
                          :error-messages="folioEditError"
                          label="Folio or Reference Number"
                          persistent-hint
                          filled
                          v-model="folioEditNumber"
                          @keypress.enter="shiftFocus()"
                          />
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from 'vue-demi'

export default defineComponent({
  props: {
    defaultFolioNumber: {
      type: String,
      default: ''
    }
  },
  setup (props, { emit }) {
    const localState = reactive({
      folioEdit: false,
      folioEditError: '',
      folioEditHint: `${15 - props.defaultFolioNumber?.length}`,
      folioEditNumber: props.defaultFolioNumber,
      folioNumber: props.defaultFolioNumber
    })

    watch(() => localState.folioEditNumber, (val: string) => {
      if (val?.length > 15) {
        localState.folioEditError = 'Maximum 15 characters reached'
        emit('folio-error', true)
      } else {
        localState.folioEditError = ''
        localState.folioEditHint = `${15 - val?.length}`
        localState.folioNumber = localState.folioEditNumber
        emit('folio-error', false)
      }
    })
    watch(() => localState.folioNumber, (val: string) => {
      emit('folio-number', val)
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
@import '@/assets/styles/theme.scss';
#folio-box::v-deep {
  width: 250px;
  float: right;
  .v-input.v-text-field .v-text-field__details {
    margin-bottom: 0px;
  }
}

</style>
