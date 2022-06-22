<template>
  <v-card id="mhr-home-other-information" flat class="py-6 px-8 rounded">
    <v-row>
      <v-col cols="2">
        <label class="generic-label" for="other-remarks">Other</label>
      </v-col>
      <v-col cols="10">
        <v-textarea
          id="other-remarks"
          v-model="otherRemarks"
          filled
          :error-messages="errorMessages.otherRemarks"
          name="name"
          counter="140"
          placeholder="Enter other details about the home (Optional)"
          class="other-info"
          data-test-id="otherRemarks"
        ></v-textarea>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { useMhrRegistrationValidation as getMhrRegistrationErrors } from '@/composables/useMhrRegistrationValidation'

export default defineComponent({
  setup () {
    const { getMhrRegistrationOtherInfo } = useGetters<any>([
      'getMhrRegistrationOtherInfo'
    ])

    const { setMhrRegistrationOtherInfo } = useActions<any>([
      'setMhrRegistrationOtherInfo'
    ])

    const localState = reactive({
      otherRemarks: getMhrRegistrationOtherInfo.value,
      errorMessages: {
        otherRemarks: ''
      }
    })

    watch(
      () => localState.otherRemarks,
      (val: string) => {
        setMhrRegistrationOtherInfo(val)
        localState.errorMessages.otherRemarks = getMhrRegistrationErrors(
          localState,
          'otherRemarks'
        )
      }
    )

    return { ...toRefs(localState) }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

::v-deep .other-info {
  color: $gray7;
}
</style>
