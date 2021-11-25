<template>
  <div class="ma-0 pa-0">
    <v-row no-gutters>
      <v-col class="tombstone-header">
        {{ header }}
      </v-col>
      <v-col class="ml-16 tombstone-info" style="padding-top: 0.375rem;">
        <v-row justify="end" no-gutters>
          <v-col :class="$style['info-label']" cols="6">
            <span class="float-right">Base Registration Date and Time: </span>
          </v-col>
          <v-col class="pl-3" cols="6">
            {{ creationDate }}
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    <v-row class="tombstone-sub-header" no-gutters>
      <v-col>
        {{ registrationType }}
      </v-col>
      <v-col class="ml-16 tombstone-info" style="padding-top: 0.125rem;">
        <v-row justify="end" no-gutters>
          <v-col :class="$style['info-label']" cols="6">
            <span class="float-right">Current Expiry Date and Time: </span>
          </v-col>
          <v-col class="pl-3" cols="6">
            {{ expiryDate }}
          </v-col>
        </v-row>
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
  name: 'TombstoneDischarge',
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
          const date = new Date(getRegistrationCreationDate.value)
          return convertDate(date, true, true)
        }
        return ''
      }),
      expiryDate: computed((): string => {
        if (getRegistrationExpiryDate.value) {
          const date = new Date(getRegistrationExpiryDate.value)
          return convertDate(date, true, true)
        }
        return 'No Expiry'
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
