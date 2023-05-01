<template>
  <div class="ma-0 pa-0">
    <v-row no-gutters>
      <v-col class="tombstone-header">
        {{ header }}
      </v-col>
      <v-col class="ml-16 tombstone-info" style="padding-top: 0.375rem;">
        <v-row v-if="!isMhrInformation" justify="end" no-gutters>
          <v-col :class="$style['info-label']" cols="6">
            <span class="float-right">{{ dateTimePrefix }} Registration Date and Time: </span>
          </v-col>
          <v-col class="pl-3" cols="6">
            {{ creationDate }}
          </v-col>
        </v-row>
        <v-row v-else-if="isMhrInformation" justify="end" no-gutters>
          <v-col :class="$style['info-label']" cols="6">
            <span class="float-right">Registration Status: </span>
          </v-col>
          <v-col class="pl-3" cols="6">
            {{ statusType }}
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    <v-row v-if="!isMhrInformation" class="tombstone-sub-header" no-gutters>
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
    <v-row v-else>
        <v-col>
          <v-spacer></v-spacer>
        </v-col>
    </v-row>
  </div>
</template>
<script lang="ts">
// external
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
// local
import { formatExpiryDate, pacificDate } from '@/utils'
import { RegistrationTypeIF } from '@/interfaces' // eslint-disable-line
import { APIStatusTypes, MhUIStatusTypes } from '@/enums'
import { useMhrInformation } from '@/composables'

export default defineComponent({
  name: 'TombstoneDischarge',
  props: {
    isMhrInformation: {
      default: false
    }
  },
  setup () {
    const {
      getRegistrationCreationDate,
      getRegistrationExpiryDate,
      getRegistrationNumber,
      getRegistrationType,
      getMhrInformation
    } = useGetters<any>([
      'getRegistrationCreationDate',
      'getRegistrationExpiryDate',
      'getRegistrationNumber',
      'getRegistrationType',
      'getMhrInformation'
    ])
    const { isFrozenMhr } = useMhrInformation()
    const localState = reactive({
      creationDate: computed((): string => {
        if (getRegistrationCreationDate.value) {
          const date = new Date(getRegistrationCreationDate.value)
          return pacificDate(date)
        }
        if (getMhrInformation.value) {
          const date = new Date(getMhrInformation.value.createDateTime)
          return pacificDate(date)
        }
        return ''
      }),
      expiryDate: computed((): string => {
        if (getRegistrationExpiryDate.value) {
          return formatExpiryDate(new Date(new Date(getRegistrationExpiryDate.value)
            .toLocaleString('en-US', { timeZone: 'America/Vancouver' })))
        }
        return 'No Expiry'
      }),
      statusType: computed((): string => {
        const regStatus = getMhrInformation.value.statusType

        return isFrozenMhr.value || regStatus === APIStatusTypes.DRAFT
          ? MhUIStatusTypes.ACTIVE
          : regStatus[0] + regStatus.toLowerCase().slice(1)
      }),
      header: computed((): string => {
        const numberType = getRegistrationNumber.value ? 'Base' : 'Manufactured Home'
        const regNum = getRegistrationNumber.value || getMhrInformation.value.mhrNumber || ''

        return numberType + ' Registration Number ' + regNum
      }),
      registrationType: computed((): string => {
        const registration = getRegistrationType.value as RegistrationTypeIF
        return registration?.registrationTypeUI || ''
      }),
      dateTimePrefix: computed(() => {
        return getRegistrationNumber.value ? 'Base' : 'MH'
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
