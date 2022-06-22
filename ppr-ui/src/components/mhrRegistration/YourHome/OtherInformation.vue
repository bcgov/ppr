<template>
  <v-form ref="otherInformationForm" v-model="isOtherInfoValid">
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
            :rules="maxLengthRules(140)"
            name="name"
            counter="140"
            label="Other details about the home (Optional)"
            class="other-info"
            data-test-id="otherRemarks"
          ></v-textarea>
        </v-col>
      </v-row>
    </v-card>
  </v-form>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { useInputRules } from '@/composables/useInputRules'

export default defineComponent({
  setup () {
    const { maxLengthRules } = useInputRules()

    const { getMhrRegistrationOtherInfo } = useGetters<any>([
      'getMhrRegistrationOtherInfo'
    ])

    const { setMhrRegistrationOtherInfo } = useActions<any>([
      'setMhrRegistrationOtherInfo'
    ])

    const localState = reactive({
      isOtherInfoValid: false,
      otherRemarks: getMhrRegistrationOtherInfo.value
    })

    watch(
      () => localState.otherRemarks,
      (val: string) => {
        setMhrRegistrationOtherInfo(val)
      }
    )

    return { maxLengthRules, ...toRefs(localState) }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

::v-deep .other-info {
  color: $gray7;
}
</style>
