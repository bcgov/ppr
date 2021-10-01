<template>
  <v-container fluid no-gutters class="pa-0">
    <div>
      <v-row no-gutters>
        <v-col cols="3" class="generic-label">
          Trust Indenture
        </v-col>
        <v-col cols="auto">
          <v-checkbox
            class="trust-checkbox pa-0 ma-0"
            :hide-details="false"
            :hint="trustIndentureHint"
            label=""
            id="trust-indenture-checkbox"
            v-model="trustIndenture"
          >
          </v-checkbox>
        </v-col>
        <v-col cols="8">
          <v-tooltip
            top
            content-class="top-tooltip pa-5"
            transition="fade-transition"
          >
            <template v-slot:activator="{ on }">
              <span v-on="on" class="trust-indenture">Trust Indenture (Optional)</span>
            </template>
            {{ trustIndentureHint }}
          </v-tooltip>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col cols="3" class="generic-label">
        </v-col>
        <v-col cols="9" class="summary-text">
            Note: a court order is required to add or remove trust indenture.
        </v-col>
      </v-row>

    <v-row no-gutters>
      <v-col cols="12">
        <div class="form__row form__btns pt-4">
            <v-btn
                large
                id="done-btn-trust-indenture"
                class="ml-auto"
                color="primary"
                @click="onSubmitForm()"
                >
                Done
            </v-btn>

            <v-btn
                id="cancel-btn-trust-indenture"
                large
                outlined
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
// external
import {
  computed,
  defineComponent,
  reactive,
  toRefs
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'

// local
import { LengthTrustIF } from '@/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  props: {
    currentTrustIndenture: {
      type: Boolean,
      default: false
    }
  },
  emits: ['editTrustIndenture', 'resetEvent'],
  setup (props, context) {
    const { setLengthTrust } = useActions<any>(['setLengthTrust'])
    const { getLengthTrust } = useGetters<any>(['getLengthTrust'])
    const modal = false

    const localState = reactive({
      existingTrustIndenture: props.currentTrustIndenture,
      trustIndenture: props.currentTrustIndenture,
      trustIndentureHint: 'Note: a court order is required to add or remove trust indenture.',
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
        setLengthTrust(lt)
      }
      context.emit('editTrustIndenture')
    }

    return {
      onSubmitForm,
      resetData,
      modal,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
/* Need scoped for date picker v-deep style overrides to work */
@import '@/assets/styles/theme.scss';
</style>
