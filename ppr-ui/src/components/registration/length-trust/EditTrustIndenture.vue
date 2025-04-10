<template>
  <v-container
    fluid
    class="pa-0 noGutters"
  >
    <div>
      <v-row
        class="pt-6"
        no-gutters
      >
        <v-col
          cols="3"
          class="generic-label"
        >
          Trust Indenture
        </v-col>
        <v-col cols="auto">
          <v-checkbox
            id="trust-indenture-checkbox"
            v-model="trustIndenture"
            class="trust-checkbox pa-0 ma-0 mt-n4 ml-n3"
            hide-details
            label=""
          />
        </v-col>
        <v-col cols="8">
          <p class="trust-indenture">
            Trust Indenture (Optional)
          </p>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col cols="12">
          <div class="form__row form__btns pt-4 float-right">
            <v-btn
              id="done-btn-trust-indenture"
              size="large"
              class="ml-auto mr-2"
              color="primary"
              @click="onSubmitForm()"
            >
              Done
            </v-btn>

            <v-btn
              id="cancel-btn-trust-indenture"
              size="large"
              variant="outlined"
              color="primary"
              @click="resetData()"
            >
              Cancel
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  toRefs
} from 'vue'
import { useStore } from '@/store/store'
import type { LengthTrustIF } from '@/interfaces'
import { ActionTypes } from '@/enums'
import { storeToRefs } from 'pinia'

export default defineComponent({
  props: {
    currentTrustIndenture: {
      type: Boolean,
      default: false
    }
  },
  emits: ['editTrustIndenture', 'resetEvent'],
  setup (props, context) {
    const { setLengthTrust } = useStore()
    const { getLengthTrust } = storeToRefs(useStore())
    const localState = reactive({
      existingTrustIndenture: props.currentTrustIndenture,
      trustIndenture: props.currentTrustIndenture,
      lengthTrust: computed((): LengthTrustIF => {
        return getLengthTrust.value as LengthTrustIF || null
      })
    })

    const resetData = (): void => {
      context.emit('resetEvent')
    }

    const onSubmitForm = (): void => {
      if (localState.trustIndenture !== localState.existingTrustIndenture) {
        const lt = localState.lengthTrust
        lt.trustIndenture = localState.trustIndenture
        lt.action = ActionTypes.EDITED
        setLengthTrust(lt)
      }
      context.emit('editTrustIndenture')
    }

    return {
      onSubmitForm,
      resetData,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
/* Need scoped for date picker v-deep style overrides to work */
@import '@/assets/styles/theme.scss';
</style>
