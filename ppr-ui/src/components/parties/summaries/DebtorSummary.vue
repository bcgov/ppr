<template>
  <v-container class="pa-0 party-summary flat">
    <base-party-summary
      :setHeaders="debtorHeaders"
      :setItems="debtors"
      :setOptions="debtorOptions"
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
import { useRouter } from 'vue2-helpers/vue-router'
import { BasePartySummary } from '@/components/parties/summaries'
import { AddPartiesIF, PartySummaryOptionsI } from '@/interfaces' // eslint-disable-line no-unused-vars

import { debtorTableHeaders } from '@/resources'

export default defineComponent({
  name: 'DebtorSummary',
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
    const { getAddSecuredPartiesAndDebtors, setAddSecuredPartiesAndDebtors } = useStore()
    const parties: AddPartiesIF = getAddSecuredPartiesAndDebtors

    const localState = reactive({
      debtors: parties.debtors,
      debtorHeaders: computed(function () {
        const headersToShow = [...debtorTableHeaders]
        return headersToShow
      }),
      debtorOptions: {
        header: props.setHeader,
        iconColor: 'darkBlue',
        iconImage: 'mdi-account',
        isDebtorSummary: true,
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
