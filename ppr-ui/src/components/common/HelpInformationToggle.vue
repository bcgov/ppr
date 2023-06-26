<template>
  <SimpleHelpToggle
    class="mb-7"
    toggleButtonTitle="Need Help? Contact Us"
  >
    <h3 class="text-center mb-2">
      Contact BC Registries
    </h3>
    <div class="ml-7">
      <DialogContent
        :setBaseText="helpText"
        :setHasContactInfo="true"
      />
      <div class="mt-3">
        <h4>Hours of Operation:</h4>
        <p class="mb-0">Monday to Friday, 8:30 am - 4:30 pm Pacific time</p>
      </div>
    </div>
  </SimpleHelpToggle>
</template>

<script lang="ts">
import { defineComponent } from 'vue-demi'
import { SimpleHelpToggle } from '@/components/common'
import { DialogContent } from '@/components/dialogs/common'

export default defineComponent({
  name: 'HelpInformationToggle',
  components: {
    SimpleHelpToggle,
    DialogContent
  },
  props: {
    helpText: {
      type: String,
      required: true
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
