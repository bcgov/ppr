<script setup lang="ts">
import type { SubmittingPartyIF } from '@/interfaces'
import { useHomeOwners } from '@/composables'
import { HomeOwnerPartyTypes } from '@/enums'

const props = withDefaults(defineProps<{ isTransfer?: boolean }>(), { isTransfer: false })
const emit = defineEmits<{
  (e: 'party', party: SubmittingPartyIF): void
  (e: 'owner', owner: string): void
}>()

const { getTransferOrRegistrationHomeOwners } = useHomeOwners(props.isTransfer)
const selectPartyMethod = ref('manual')
const selectedOwner = ref(null)
const partyMethods = [
  { label: 'Manual Entry', value: 'manual' },
  { label: 'PPR PartyCode Lookup', value: 'partycode' },
  { label: 'Owner', value: 'owner' }
]

// Map to USelect items
const ownerOptions = computed(() =>
  getTransferOrRegistrationHomeOwners()
    .filter(owner => owner.action !== ActionTypes.REMOVED)
    .map(owner => ({
    label: owner.partyType === HomeOwnerPartyTypes.OWNER_BUS
      ? owner.organizationName
      : [owner.individualName?.first, owner.individualName?.middle, owner.individualName?.last]
        .filter(Boolean)
        .join(' '),
    value: owner.ownerId
  }))
)

function formatOwner(owner: any) {
  return {
    personName: owner.individualName || { first: '', middle: '', last: '' },
    businessName: owner.organizationName || '',
    emailAddress: owner.emailAddress || '',
    phoneNumber: owner.phoneNumber || '',
    phoneExtension: owner.phoneExtension || '',
    address: {
      street: owner.address?.street || '',
      city: owner.address?.city || '',
      region: owner.address?.region || '',
      country: owner.address?.country || '',
      postalCode: owner.address?.postalCode || '',
      streetAdditional: owner.address?.streetAdditional || ''
    }
  }
}

function handleOwnerSelect(ownerId: string) {
  const owner = getTransferOrRegistrationHomeOwners().find(o => o.ownerId === ownerId)
  if (owner) {
    emit('owner', formatOwner(owner))
  }
}

function handlePartySelect(party: SubmittingPartyIF) {
  emit('party', party)
}
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
        @update:model-value="handleOwnerSelect"
      />
    </div>
  </UContainer>
</template>
