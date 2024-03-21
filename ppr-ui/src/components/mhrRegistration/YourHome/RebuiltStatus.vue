<template>
  <v-form
    ref="rebuiltStatus"
    v-model="isRebuiltStatusValid"
  >
    <v-card
      id="mhr-rebuilt-status"
      flat
      class="py-6 px-8 rounded"
    >
      <v-row>
        <v-col
          cols="3"
          class="px-0"
        >
          <label
            class="generic-label"
            for="rebuilt-status"
            :class="{'error-text': validate}"
          >
            Rebuilt Description
          </label>
          <UpdatedBadge
            v-if="isMhrCorrection"
            :baseline="correctionState.rebuilt.baseline"
            :currentState="correctionState.rebuilt.currentState"
          />
        </v-col>
        <v-col cols="9">
          <v-textarea
            id="rebuilt-status-text"
            v-model.trim="rebuiltRemarks"
            variant="filled"
            color="primary"
            counter="280"
            :rules="maxLength(280)"
            label="Description of the rebuilt status of the home (Optional)"
          />
        </v-col>
      </v-row>
    </v-card>
  </v-form>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { useInputRules, useMhrCorrections, useMhrValidations } from '@/composables/'
import { storeToRefs } from 'pinia'
import { FormIF } from '@/interfaces'
import { UpdatedBadge } from '@/components/common'

export default defineComponent({
  name: 'RebuiltStatus',
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
      getMhrRegistrationHomeDescription,
      getMhrRegistrationValidationModel
     } = storeToRefs(useStore())
    const { maxLength } = useInputRules()
    const {
      MhrCompVal,
      MhrSectVal,
      setValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const { correctionState, isMhrCorrection } = useMhrCorrections()
    const rebuiltStatus = ref(null) as FormIF

    const localState = reactive({
      isRebuiltStatusValid: false,
      rebuiltRemarks: getMhrRegistrationHomeDescription.value?.rebuiltRemarks
    })

    watch(() => localState.rebuiltRemarks, (val: string) => {
      setMhrHomeDescription({ key: 'rebuiltRemarks', value: val })
    })

    watch(() => localState.isRebuiltStatusValid, (val: boolean) => {
      setValidation(MhrSectVal.YOUR_HOME_VALID, MhrCompVal.REBUILT_STATUS_VALID, val)
    })

    watch(() => props.validate, () => {
      rebuiltStatus.value?.validate()
    })

    return {
      maxLength,
      rebuiltStatus,
      correctionState,
      isMhrCorrection,
      ...toRefs(localState) }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
