<template>
  <section id="qs-submitting-party">
    <AccountInfo
      title="Submitting Party for this Application"
      tooltipContent="The default Submitting Party is based on your BC Registries user account information. This
        information can be updated within your account settings."
      :accountInfo="getMhrQsSubmittingParty"
    />
  </section>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue-demi'
import { AccountInfo } from '@/components/common'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'

export default defineComponent({
  name: 'QsReviewConfirm',
  components: { AccountInfo },
  props: {},
  setup () {
    const { getMhrQsSubmittingParty } = storeToRefs(useStore())
    const localState = reactive({})

    return {
      getMhrQsSubmittingParty,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
