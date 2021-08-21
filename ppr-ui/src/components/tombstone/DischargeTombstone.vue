<template>
  <div class="ma-0 pa-0">
    <v-row no-gutters>
      <v-col class="tombstone-header">
        {{ header }}
      </v-col>
      <v-col class="float-right tombstone-info" style="padding-top: 0.375rem;">
        <div class="float-right">
          <span :class="$style['info-label']">Base Registration Date and Time: </span>
          {{ creationDate }}
        </div>
      </v-col>
    </v-row>
    <v-row class="tombstone-sub-header" no-gutters>
      <v-col>
        {{ registrationType }}
      </v-col>
      <v-col class="tombstone-info" style="padding-top: 0.125rem;">
        <div class="float-right">
          <span :class="$style['info-label']">Current Expiry Date and Time: </span>
          {{ expiryDate }}
        </div>
      </v-col>
    </v-row>
  </div>
</template>
<script lang="ts">
// external
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
// local
import { convertDate } from '@/utils'
import { RegistrationTypeIF } from '@/interfaces' // eslint-disable-line

export default defineComponent({
  name: 'DischargeTombstone',
  setup () {
    const {
      getRegistrationCreationDate,
      getRegistrationExpiryDate,
      getRegistrationNumber,
      getRegistrationType
    } = useGetters<any>([
      'getRegistrationCreationDate',
      'getRegistrationExpiryDate',
      'getRegistrationNumber',
      'getRegistrationType'
    ])
    const localState = reactive({
      creationDate: computed((): string => {
        if (getRegistrationCreationDate.value) {
          console.log(getRegistrationCreationDate.value)
          const date = new Date(getRegistrationCreationDate.value)
          return convertDate(date, true, true)
        }
        return ''
      }),
      expiryDate: computed((): string => {
        if (getRegistrationExpiryDate.value) {
          console.log(getRegistrationExpiryDate.value)
          const date = new Date(getRegistrationExpiryDate.value)
          return convertDate(date, true, true)
        }
        return ''
      }),
      header: computed((): string => {
        const regNum = getRegistrationNumber.value || ''
        return 'Base Registration Number ' + regNum
      }),
      registrationType: computed((): string => {
        const registration = getRegistrationType.value as RegistrationTypeIF
        return registration?.registrationTypeUI || ''
      })
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.info-label {
  color: $gray9 !important;
  font-weight: bold;
}
</style>
