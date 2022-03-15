<template>
  <v-container flat class="pa-0 party-summary">
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
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'

import { BasePartySummary } from '@/components/parties/summaries'
import { AddPartiesIF, PartySummaryOptionsI } from '@/interfaces' // eslint-disable-line no-unused-vars

import { partyTableHeaders } from '@/resources'
import { isSecuredPartyRestrictedList } from '@/utils'
import { RegistrationFlowType } from '@/enums'

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
  setup (props, context) {
    const {
      getAddSecuredPartiesAndDebtors,
      getRegistrationType,
      getRegistrationFlowType
    } = useGetters<any>([
      'getAddSecuredPartiesAndDebtors',
      'getRegistrationType',
      'getRegistrationFlowType'
    ])
    const { setAddSecuredPartiesAndDebtors } = useActions<any>([
      'setAddSecuredPartiesAndDebtors'
    ])
    const router = context.root.$router
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
        const headersToShow = [...partyTableHeaders]
        return headersToShow
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
