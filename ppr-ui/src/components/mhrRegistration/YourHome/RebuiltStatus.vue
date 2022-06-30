<template>
  <v-form ref="rebuiltStatus" v-model=isRebuiltStatusValid>
    <v-card id="mhr-rebuilt-status" flat class="py-6 px-8 rounded">
      <v-row no-gutters>
        <v-col cols="2">
          <label class="generic-label" for="rebuilt-status" :class="{'error-text': false}">Rebuilt Status</label>
        </v-col>
        <v-col cols="10">
          <v-textarea
            filled
            id="rebuilt-status-text"
            counter="280"
            v-model.trim="rebuiltRemarks"
            :rules="customRules(invalidSpaces(), maxLength(280))"
            label="Description of the rebuilt status of the home (Optional)"
            validate-on-blur
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
  name: 'RebuiltStatus',
  components: {},
  props: {},
  setup () {
    const { customRules, maxLength, invalidSpaces } = useInputRules()

    const { getMhrRegistrationHomeDescription } = useGetters<any>([
      'getMhrRegistrationHomeDescription'
    ])

    const { setMhrHomeDescription } = useActions<any>([
      'setMhrHomeDescription'
    ])

    const localState = reactive({
      isRebuiltStatusValid: false,
      rebuiltRemarks: getMhrRegistrationHomeDescription.value?.rebuiltRemarks
    })

    watch(
      () => localState.rebuiltRemarks,
      (val: string) => {
        setMhrHomeDescription({ key: 'rebuiltRemarks', value: val })
      }
    )

    return { customRules, invalidSpaces, maxLength, ...toRefs(localState) }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
