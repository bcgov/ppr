<template>
  <div id="folio-box">
            <v-text-field id="folio-edit-txt"
                          class="py-0 my-0"
                          :error-messages="folioEditError"
                          label="Folio or Reference Number"
                          persistent-hint
                          filled
                          v-model="folioEditNumber"
                          />
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'

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

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#folio-box {
  width: 250px;
  margin-left: 54px;
}

</style>
