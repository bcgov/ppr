<template>
  <v-form
    ref="otherInformationForm"
    v-model="isOtherInfoValid"
  >
    <v-card
      id="mhr-home-other-information"
      flat
      class="py-6 px-8 rounded"
    >
      <v-row>
        <v-col cols="3">
          <label
            class="generic-label"
            for="other-remarks"
            :class="{'error-text': validate}"
          >Other</label>
          <UpdatedBadge
            v-if="showUpdatedBadge"
            :action="correctionState.action"
            :baseline="correctionState.otherRemarks.baseline"
            :current-state="correctionState.otherRemarks.currentState"
          />
        </v-col>
        <v-col cols="9">
          <v-textarea
            id="other-remarks"
            v-model.trim="otherRemarks"
            variant="filled"
            color="primary"
            :rules="maxLength(140)"
            name="name"
            counter="140"
            label="Other details about the home (Optional)"
            class="other-info"
            data-test-id="otherRemarks"
          />
        </v-col>
      </v-row>
    </v-card>
  </v-form>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { useInputRules, useMhrCorrections, useMhrValidations, useUpdatedBadges } from '@/composables/'
import { storeToRefs } from 'pinia'
import type { FormIF } from '@/interfaces'
import { UpdatedBadge } from '@/components/common'

export default defineComponent({
  name: 'OtherInformation',
  components: { UpdatedBadge },
  props: {
    validate: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const { setMhrHomeDescription } = useStore()
    const {
      getMhrRegistrationOtherInfo,
      getMhrRegistrationValidationModel
     } = storeToRefs(useStore())
    const { maxLength } = useInputRules()
    const {
      MhrCompVal,
      MhrSectVal,
      setValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const { correctionState } = useMhrCorrections()
    const { showUpdatedBadge } = useUpdatedBadges()

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

    return {
      maxLength,
      correctionState,
      showUpdatedBadge,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
