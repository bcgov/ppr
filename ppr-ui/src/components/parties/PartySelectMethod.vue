<script setup lang="ts">
import type { SubmittingPartyIF } from '@/interfaces'
import { usePartySelect } from '@/composables'
import type { OwnerEmitPayload } from '@/composables'

const props = withDefaults(defineProps<{ isTransfer?: boolean }>(), { isTransfer: false })
const emit = defineEmits<{
  (e: 'party', party: SubmittingPartyIF): void
  (e: 'owner', owner: OwnerEmitPayload): void
}>()

const {
  selectPartyMethod,
  selectedOwner,
  partyMethods,
  ownerOptions,
  handleOwnerSelect,
  handlePartySelect
} = usePartySelect(props.isTransfer, emit)
</script>

<template>
  <UContainer class="grid grid-cols-12 bg-white rounded py-[26px] pl-8">
    <div class="col-span-3 generic-label pr-2">
      Select Submitting Party Entry Method
    </div>
    <div class="col-span-9">
      <URadioGroup
        v-model="selectPartyMethod"
        :items="partyMethods"
        orientation="horizontal"
        variant="list"
        class="w-full flex justify-between"
        color="primary"
        :ui="{
          base: 'ring-2 h-[20px] w-[20px] ring-bcGovColor-midGray ring-offset-0 has-data-[state=checked]:ring-primary!',
          label: 'cursor-pointer text-[16px]',
          item: 'flex w-full font-normal',
          fieldset: 'flex-auto',
          indicator: 'after:bg-primary after:rounded-full bg-bcGovColor-white/0 after:w-[10px]! after:h-[10px]!',
        }"
      />
    </div>
    <div
      class="col-start-3 col-span-12 ml-[14px] pt-0 mt-0 pl-10"
      :class="{'mx-6' : selectPartyMethod === 'owner'}"
    >
      <PartySearch
        v-if="selectPartyMethod === 'partycode'"
        is-mhr-party-search
        class="pt-0!"
        :hide-manual-search-label="true"
        @select-item="handlePartySelect($event)"
      />
      <USelect
        v-if="selectPartyMethod === 'owner'"
        v-model="selectedOwner"
        :items="ownerOptions"
        :disabled="!ownerOptions.length"
        placeholder="Select an Owner"
        class="cursor-pointer ml-4 w-[98%] min-h-[58px] rounded-sm bg-bcGovColor-lightGray/10 px-[16px]
         disabled:opacity-40 text-bcGovColor-midGray disabled:cursor-default"
        :content="{  bodyLock: false }"
        @update:model-value="handleOwnerSelect"
      />
    </div>
  </UContainer>
</template>
