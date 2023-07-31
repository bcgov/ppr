<template>
  <div id="qs-select-access">
    <section id="qs-access-type" class="mt-10">
      <h2>Qualified Supplier Access Type</h2>
      <p class="mt-4">
        If you are an active B.C. lawyer or notary, a home manufacturer or a home dealer, and would like to have access
        to perform additional transactions in the Manufactured Home Registry, you must apply to be a Qualified Supplier.
        Indicate the type of Qualified Supplier access you would like to request.
      </p>

        <SubProductSelector class="mt-6" :subProductConfig="MhrSubProductConfig" />
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue-demi'
import { SubProductSelector } from '@/components/common'
import { MhrSubProductConfig } from '@/resources'

export default defineComponent({
  name: 'QsSelectAccess',
  components: {
    SubProductSelector
  },
  props: {},
  setup (props, context) {
    const localState = reactive({})

    return {
      MhrSubProductConfig,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
