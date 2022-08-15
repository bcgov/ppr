<template>
  <v-form ref="rebuiltStatus" v-model=isRebuiltStatusValid>
    <v-card id="mhr-rebuilt-status" flat class="py-6 px-8 rounded">
      <v-row>
        <v-col cols="2" class="px-0">
          <label class="generic-label" for="rebuilt-status" :class="{'error-text': validate}">
            Rebuilt Description
          </label>
        </v-col>
        <v-col cols="10">
          <v-textarea
            filled
            id="rebuilt-status-text"
            counter="280"
            class="pl-1"
            v-model.trim="rebuiltRemarks"
            :rules="maxLength(280)"
            label="Description of the rebuilt status of the home (Optional)"
          ></v-textarea>
        </v-col>
      </v-row>
    </v-card>
  </v-form>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { useInputRules, useMhrValidations } from '@/composables/'

export default defineComponent({
  name: 'RebuiltStatus',
  components: {},
  props: {
    validate: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { getMhrRegistrationHomeDescription, getMhrRegistrationValidationModel } = useGetters<any>([
      'getMhrRegistrationHomeDescription', 'getMhrRegistrationValidationModel'
    ])

    const { setMhrHomeDescription } = useActions<any>([
      'setMhrHomeDescription'
    ])

    const { maxLength } = useInputRules()
    const {
      MhrCompVal,
      MhrSectVal,
      setValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

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

    watch(() => props.validate, async () => {
      // @ts-ignore - function exists
      await context.refs.rebuiltStatus.validate()
    })

    return { maxLength, ...toRefs(localState) }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
