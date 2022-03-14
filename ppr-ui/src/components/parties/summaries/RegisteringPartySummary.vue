<template>
  <v-container flat class="pa-0 party-summary">
    <base-party-summary
      :setHeaders="registeringPartyHeaders"
      :setItems="registeringParty"
      :setOptions="registeringPartyOptions"
      @triggerNoDataAction="goToParties()"
    />
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  computed,
  onMounted,
  toRefs
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'

import { BasePartySummary } from '@/components/parties/summaries'
import { AddPartiesIF, PartyIF, PartySummaryOptionsI } from '@/interfaces' // eslint-disable-line no-unused-vars

import { registeringTableHeaders } from '@/resources'
import { RegistrationFlowType } from '@/enums'
import { useRegisteringParty } from '@/composables/useRegisteringParty'

export default defineComponent({
  name: 'RegisteringPartySummary',
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
      getOriginalAddSecuredPartiesAndDebtors,
      getRegistrationFlowType
    } = useGetters<any>([
      'getAddSecuredPartiesAndDebtors',
      'getOriginalAddSecuredPartiesAndDebtors',
      'getRegistrationFlowType'
    ])
    const { setAddSecuredPartiesAndDebtors } = useActions<any>([
      'setAddSecuredPartiesAndDebtors'
    ])
    const { getRegisteringParty } = useRegisteringParty()
    const router = context.root.$router
    const parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value

    const localState = reactive({
      registeringParty: computed((): Array<PartyIF> => {
        let regParty: PartyIF = parties?.registeringParty
        if (getRegistrationFlowType.value !== RegistrationFlowType.NEW) {
          regParty = getOriginalAddSecuredPartiesAndDebtors.value?.registeringParty
        } else {
          regParty = getAddSecuredPartiesAndDebtors.value?.registeringParty
        }
        if (regParty !== null) {
          return [regParty]
        }
        return []
      }),
      registeringPartyHeaders: computed(function () {
        const headersToShow = [...registeringTableHeaders]
        return headersToShow
      }),
      registeringPartyOptions: {
        header: props.setHeader,
        iconColor: 'darkBlue',
        iconImage: 'mdi-account',
        isDebtorSummary: false,
        enableNoDataAction: props.setEnableNoDataAction,
        isRegisteringParty: true
      } as PartySummaryOptionsI
    })

    onMounted(async () => {
      const regParty = parties?.registeringParty
      if (regParty === null) {
        try {
          await getRegisteringParty()
        } catch (e) {
          console.error('RegisteringParty.vue onMounted error: ' + ((e as Error).message))
        }
      }
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
