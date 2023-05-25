<template>
  <v-form ref="otherInformationForm" v-model="isOtherInfoValid">
    <v-card id="mhr-home-other-information" flat class="py-6 px-8 rounded">
      <v-row>
        <v-col cols="2">
          <label class="generic-label" for="other-remarks" :class="{'error-text': validate}">Other</label>
        </v-col>
        <v-col cols="10">
          <v-textarea
            id="other-remarks"
            v-model.trim="otherRemarks"
            filled
            :rules="maxLength(140)"
            name="name"
            counter="140"
            label="Other details about the home (Optional)"
            class="other-info pl-1"
            data-test-id="otherRemarks"
          ></v-textarea>
        </v-col>
      </v-row>
    </v-card>
  </v-form>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, toRefs, watch } from 'vue-demi'
import { useStore } from '@/store/store'
import { useInputRules, useMhrValidations } from '@/composables/'
import { storeToRefs } from 'pinia'
import { FormIF } from '@/interfaces'

export default defineComponent({
  props: {
    validate: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { setMhrHomeDescription } = useStore()
    const { getMhrRegistrationOtherInfo, getMhrRegistrationValidationModel } = storeToRefs(useStore())
    const { maxLength } = useInputRules()
    const {
      MhrCompVal,
      MhrSectVal,
      setValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const otherInformationForm = ref(null) as FormIF

    const localState = reactive({
      isOtherInfoValid: false,
      otherRemarks: getMhrRegistrationOtherInfo.value
    })

    watch(() => localState.otherRemarks, (val: string) => {
      setMhrHomeDescription({ key: 'otherRemarks', value: val })
    })

    watch(() => localState.isOtherInfoValid, (val: boolean) => {
      setValidation(MhrSectVal.YOUR_HOME_VALID, MhrCompVal.OTHER_VALID, val)
    })

    watch(() => props.validate, () => {
      otherInformationForm.value.validate()
    })

    return { maxLength, ...toRefs(localState) }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
