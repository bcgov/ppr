<template>
  <v-container
    class="pa-0"
    :class="showErrors && !valid ? 'border-error-left': ''"
    style="background-color: white;"
  >
    <v-row no-gutters style="padding: 40px 30px;">
      <v-col class="generic-label pt-5" cols="3">
        Total Discharge
      </v-col>
      <v-col cols="9">
        <div class="summary-info px-7 py-5">
          <p class="ma-0"><b>Base Registration Number:</b> {{ regNum }}</p>
          <p class="ma-0 pt-2"><b>Registration Type:</b> {{ regType }}</p>
          <p class="ma-0 pt-2"><b>Collateral:</b> {{ collateralSummary }}</p>
        </div>
        <v-checkbox
          id="discharge-confirm-checkbox-1"
          class="ma-0 pt-4"
          :class="showErrors && !checkbox1 ? 'check-box-error': 'copy-normal'"
          hide-details
          v-model="checkbox1"
        >
          <template v-slot:label>
            <p class="ma-0">
              I confirm that I wish to <b>discharge this registration.</b>
            </p>
          </template>
        </v-checkbox>
        <v-checkbox
          id="discharge-confirm-checkbox-2"
          class="ma-0 pt-4"
          :class="showErrors && !checkbox2 ? 'check-box-error': 'copy-normal'"
          hide-details
          v-model="checkbox2"
        >
          <template v-slot:label>
            <p class="ma-0">
              I understand that <b>all collateral on this registration will be released.</b>
            </p>
          </template>
        </v-checkbox>
        <v-checkbox
          id="discharge-confirm-checkbox-3"
          class="ma-0 pt-4"
          :class="showErrors && !checkbox3 ? 'check-box-error': 'copy-normal'"
          hide-details
          v-model="checkbox3"
        >
          <template v-slot:label>
            <p class="ma-0">
              I understand that <b>all Secured Parties will be notified.</b>
            </p>
          </template>
        </v-checkbox>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
  watch
} from 'vue-demi'

// local
import { UIRegistrationTypes } from '@/enums' // eslint-disable-line no-unused-vars

export default defineComponent({
  name: 'DischargeConfirmSummary',
  props: {
    setRegNum: String,
    setRegType: String,
    setCollateralSummary: String,
    setShowErrors: {
      default: false
    }
  },
  emits: ['valid'],
  setup (props, { emit }) {
    const localState = reactive({
      checkbox1: false,
      checkbox2: false,
      checkbox3: false,
      collateralSummary: props.setCollateralSummary,
      regNum: props.setRegNum,
      regType: props.setRegType as UIRegistrationTypes,
      showErrors: props.setShowErrors,
      valid: computed(() => {
        return localState.checkbox1 && localState.checkbox2 && localState.checkbox3
      })
    })

    watch(() => props.setShowErrors, (val) => {
      localState.showErrors = val
    })
    watch(() => localState.valid, (val) => {
      emit('valid', val)
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.check-box-error p {
  color: $error !important;
}
.copy-normal p {
  color: $gray7;
}
.summary-info {
  background-color: $gray1;
  color: $gray7;
}
</style>
