<template>
  <v-container flat class="pa-0" id="folio-summary">
    <v-form v-model="isValid">
      <v-row no-gutters>
        <v-col class="generic-label"
          ><h3>1. Folio or Reference Number</h3></v-col
        >
      </v-row>
      <v-row no-gutters class="pb-6 pt-4">
        <v-col>
          Add an optional number for this business for your own tracking
          purposes. This information is not used by the BC Business Registry.
        </v-col>
      </v-row>

      <v-row class="px-1">
        <v-col cols="12" class="pa-0">
          <v-card flat>
            <v-row no-gutters>
              <v-col cols="3" class="generic-label pt-10 px-8"
                >Folio Number</v-col
              >
              <v-col cols="9" class="pt-8 pr-8">
                <v-text-field
                  filled
                  id="txt-folio"
                  label="Folio or Reference Number (Optional)"
                  v-model="folioNumber"
                  persistent-hint
                  :rules="rules"
                />
              </v-col>
            </v-row>
          </v-card>
        </v-col>
      </v-row>
    </v-form>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  watch,
  onMounted
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'

export default defineComponent({
  setup (props, { emit }) {
    const { setFolioOrReferenceNumber } = useActions<any>([
      'setFolioOrReferenceNumber'
    ])
    const { getFolioOrReferenceNumber } = useGetters<any>([
      'getFolioOrReferenceNumber'
    ])

    const localState = reactive({
      isValid: true,
      folioNumber: '',
      rules: [
        (v: string) => /^[0-9A-Za-z]*$/.test(v) || 'Invalid character', // numbers and letters only
        (v: string) => !v || v.length <= 15 || 'Maximum 15 characters reached' // maximum character count
      ]
    })

    watch(
      () => localState.folioNumber,
      (val: string) => {
        emit('folioValid', localState.isValid)
        setFolioOrReferenceNumber(val)
      }
    )

    onMounted(() => {
      localState.folioNumber = getFolioOrReferenceNumber.value
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
