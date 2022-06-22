<template>
  <div>
    <v-card flat class="white pb-6 pt-6 pr-10 pl-8 rounded">
      <v-row>
        <v-col cols="2">
          <label class="generic-label ml" for="">Other</label>
        </v-col>
        <v-col cols="10">
          <v-textarea
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
  </div>
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
