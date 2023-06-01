<template>
  <v-container class="pa-0 party-summary flat">
    <base-party-summary
      :setHeaders="securedPartyHeaders"
      :setItems="securedParties"
      :setOptions="securedPartyOptions"
      @triggerNoDataAction="goToParties()"
    />
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  computed,
  toRefs
} from 'vue-demi'
import { useStore } from '@/store/store'
import { BasePartySummary } from '@/components/parties/summaries'
import { AddPartiesIF, PartySummaryOptionsI } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useRouter } from 'vue2-helpers/vue-router'
import { partyTableHeaders } from '@/resources'
import { isSecuredPartyRestrictedList } from '@/utils'
import { RegistrationFlowType } from '@/enums'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'SecuredPartySummary',
  components: {
    BasePartySummary
  },
  props: {
    setEnableNoDataAction: {
      default: false
    },
    setHeader: {
      default: ''
    }
  },
  setup (props) {
    const router = useRouter()
    const { setAddSecuredPartiesAndDebtors } = useStore()
    const {
      // Getters
      getAddSecuredPartiesAndDebtors,
      getRegistrationType,
      getRegistrationFlowType
    } = storeToRefs(useStore())
    const parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value

    const localState = reactive({
      securedParties: computed(function () {
        if (getRegistrationFlowType.value === RegistrationFlowType.NEW) {
          if (isSecuredPartyRestrictedList(getRegistrationType.value.registrationTypeAPI) &&
            parties.securedParties.length > 1) {
            return []
          }
        }
        return parties.securedParties
      }),
      securedPartyHeaders: computed(function () {
        return [...partyTableHeaders]
      }),
      securedPartyOptions: {
        header: props.setHeader,
        iconColor: 'darkBlue',
        iconImage: 'mdi-account',
        isDebtorSummary: false,
        enableNoDataAction: props.setEnableNoDataAction,
        isRegisteringParty: false
      } as PartySummaryOptionsI
    })

    const goToParties = (): void => {
      parties.showInvalid = true
      setAddSecuredPartiesAndDebtors(parties)
      router.push({ path: '/new-registration/add-securedparties-debtors' })
    }

    return {
      goToParties,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
