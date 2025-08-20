import { ref, computed, watch } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import type { SubmittingPartyIF } from '@/interfaces'
import { useHomeOwners } from '@/composables'
import { HomeOwnerPartyTypes, ActionTypes } from '@/enums'

/**
 * Composable to manage the Party selection UI state and emitted payloads.
 * Supports three methods: 'manual', 'partycode', and 'owner'.
 */

/**
 * Structured payload emitted when an Owner is selected.
 */
export interface OwnerEmitPayload {
  personName: { first: string; middle: string; last: string }
  businessName: string
  emailAddress: string
  phoneNumber: string
  phoneExtension: string
  address: {
    street: string
    city: string
    region: string
    country: string
    postalCode: string
    streetAdditional: string
  }
}

/**
 * Event emitter signature for the party selector.
 * Emits:
 * - 'party' with a SubmittingPartyIF
 * - 'owner' with an OwnerEmitPayload
 */
export type PartySelectEmit =
  ((e: 'party', party: SubmittingPartyIF) => void) &
  ((e: 'owner', owner: OwnerEmitPayload) => void)

/** Current party selection method (manual | partycode | owner). */
const selectPartyMethod = ref<'manual' | 'partycode' | 'owner'>('manual')
/** Currently selected owner id (string) or null when none selected. */
const selectedOwner = ref<string | null>(null)

/**
 * Party selection composable.
 * @param isTransfer - True when in a transfer flow; false for registration.
 * @param emit - Emit callback to notify parent about selections.
 */
export function usePartySelect(isTransfer: boolean, emit: PartySelectEmit) {
  const { getTransferOrRegistrationHomeOwners } = useHomeOwners(isTransfer)

  /** Selector options for the available party methods. */
  const partyMethods = [
    { label: 'Manual Entry', value: 'manual' },
    { label: 'PPR PartyCode Lookup', value: 'partycode' },
    { label: 'Owner', value: 'owner' }
  ] as const

  /**
   * Owner dropdown options derived from Home Owners,
   * excluding those marked as REMOVED.
   */
  const ownerOptions = computed(() =>
    getTransferOrRegistrationHomeOwners()
      .filter(owner => owner.action !== ActionTypes.REMOVED)
      .map(owner => ({
        label: owner.partyType === HomeOwnerPartyTypes.OWNER_BUS
          ? owner.organizationName
          : [owner.individualName?.first, owner.individualName?.middle, owner.individualName?.last]
            .filter(Boolean)
            .join(' '),
        value: String(owner.ownerId)
      }))
  )

  /**
   * Normalize a Home Owner record into the OwnerEmitPayload structure.
   * @param owner - Raw owner object from the store.
   * @returns OwnerEmitPayload formatted for consumers.
   */
  function formatOwner(owner: any): OwnerEmitPayload {
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

  /** Reset selection state back to defaults. */
  function resetPartySelect() {
    selectPartyMethod.value = 'manual'
    selectedOwner.value = null
  }

  // When returning to the dashboard, clear any transient selection state.
  onBeforeRouteLeave((to) => {
    if (to.name === 'dashboard' || to.path === '/dashboard') {
      resetPartySelect()
    }
  })

  /**
   * Handle selection of an Owner by id and emit a formatted payload.
   * No-op if the id does not resolve to an owner.
   * @param ownerId - Owner identifier as a string.
   */
  function handleOwnerSelect(ownerId: string) {
    const owner = getTransferOrRegistrationHomeOwners().find(o => String(o.ownerId) === ownerId)
    if (owner) emit('owner', formatOwner(owner))
  }

  /**
   * Handle selection of a submitting party and emit it upstream.
   * @param party - The selected SubmittingPartyIF.
   */
  function handlePartySelect(party: SubmittingPartyIF) {
    emit('party', party)
  }

  // If the selection method changes, clear any previously chosen owner.
  watch(selectPartyMethod, () => {
    selectedOwner.value = null
  })

  return {
    selectPartyMethod,
    selectedOwner,
    partyMethods,
    ownerOptions,
    resetPartySelect,
    handleOwnerSelect,
    handlePartySelect
  }
}
