<template>
  <div>
    <section id="mhr-make-model" no-gutters class="pt-10">
      <v-col cols="auto" class="sub-header">
        5. Other Information
      </v-col>
    </section>
    <section no-gutters>
      <v-col class="pt-2 pb-6 sub-header-info">
        Include an other relevant information about the home.
      </v-col>
    </section>

    <v-card flat class="white pb-6 pt-6 pr-10 pl-8 rounded">
      <v-row>
        <v-col cols="2">
          <label class="generic-label ml" for="">Other</label>
        </v-col>
        <v-col cols="10">
          <v-textarea
            v-model="otherInfo"
            filled
            :error-messages="
              getErrorMessage('mhrRegistration.description.otherRemarks')
            "
            name="name"
            counter="140"
            placeholder="Enter other details about the home (Optional)"
            class="other-info"
          ></v-textarea>
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'

export default defineComponent({
  props: {
    // Retrieve error message via ErrorMixin
    // Pass field id for which to get the messages
    // Field id must match the state model field
    getErrorMessage: Function
  },
  setup () {
    const { getMhrRegistrationOtherInfo } = useGetters<any>([
      'getMhrRegistrationOtherInfo'
    ])

    const { setMhrRegistrationOtherInfo } = useActions<any>([
      'setMhrRegistrationOtherInfo'
    ])

    const localState = reactive({
      otherInfo: getMhrRegistrationOtherInfo.value
    })

    watch(
      () => localState.otherInfo,
      (val: string) => {
        setMhrRegistrationOtherInfo(val)
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
