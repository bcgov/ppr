<template>
  <v-container class="pa-0 party-summary flat">
    <base-party-summary
      :is-review="isReview"
      :set-headers="debtorHeaders"
      :set-items="debtors"
      :set-options="debtorOptions"
      @trigger-no-data-action="goToParties()"
    />
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue'
import { useStore } from '@/store/store'
import { useRouter } from 'vue-router'
import { BasePartySummary } from '@/components/parties/summaries'
import type { AddPartiesIF, PartySummaryOptionsI } from '@/interfaces'
import { debtorTableHeaders } from '@/resources'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'DebtorSummary',
  components: {
    BasePartySummary
  },
  props: {
    setEnableNoDataAction: {
      type: Boolean,
      default: false
    },
    setHeader: {
      type: String,
      default: ''
    },
    isReview: {
      type: Boolean,
      default: false
    },
  },
  setup (props) {
    const router = useRouter()
    const { setAddSecuredPartiesAndDebtors } = useStore()
    const { getAddSecuredPartiesAndDebtors } = storeToRefs(useStore())
    const parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value

    const localState = reactive({
      debtors: parties.debtors,
      debtorHeaders: computed(function () {
        return [...debtorTableHeaders]
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
