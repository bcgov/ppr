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
  toRefs
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'

import { BasePartySummary } from '@/components/parties/summaries'
import { AddPartiesIF, PartySummaryOptionsI } from '@/interfaces' // eslint-disable-line no-unused-vars

import { registeringTableHeaders } from '@/resources'

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
    const { getAddSecuredPartiesAndDebtors } = useGetters<any>([
      'getAddSecuredPartiesAndDebtors'
    ])
    const { setAddSecuredPartiesAndDebtors } = useActions<any>([
      'setAddSecuredPartiesAndDebtors'
    ])
    const router = context.root.$router
    const parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value

    const localState = reactive({
      registeringParty:
        parties.registeringParty !== null ? [parties.registeringParty] : [],
      registeringPartyHeaders: computed(function () {
        const headersToShow = [...registeringTableHeaders]
        return headersToShow
      }),
      registeringPartyOptions: {
        header: props.setHeader,
        iconColor: '',
        iconImage: '',
        isDebtorSummary: false,
        enableNoDataAction: props.setEnableNoDataAction
      } as PartySummaryOptionsI
    })

    const goToParties = (): void => {
      parties.showInvalid = true
      setAddSecuredPartiesAndDebtors(parties)
      router.push({ path: '/add-securedparties-debtors' })
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
