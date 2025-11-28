<template>
  <div
    class="mt-5"
    data-test-id="previous-home-owners"
  >
    <v-divider class="my-15" />

    <CollapsibleCard
      header-label="Previous Home Owners"
      toggle-label="Previous Owners"
    >
      <template #infoSlot>
        <p class="px-6 mb-6">
          These were the homeowners at the time of the exemption or cancellation and will not
          appear on the re-registration of this manufactured home.
        </p>
        <v-divider class="mx-6" />
      </template>
      <template #mainSlot>
        <div class="mx-6 my-7">
          <span class="generic-label mr-5">
            Home Tenancy Type
          </span>
          <span data-test-id="home-owner-tenancy-type">
            {{ getMhrReRegistrationPreviousTenancyType }}
          </span>
        </div>
        <v-divider class="mx-6" />

        <div class="mx-6">
          <HomeOwnersTable
            :home-owner-groups="getMhrReRegistrationPreviousOwnerGroups"
            is-readonly-table
            hide-table-errors
            :force-show-groups="getMhrReRegistrationPreviousTenancyType === HomeTenancyTypes.COMMON"
            class="mx-6 mb-1"
          />
        </div>
      </template>
    </CollapsibleCard>
  </div>
</template>

<script setup lang="ts">
import { CollapsibleCard } from '@/components/common'
import { HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { HomeTenancyTypes } from '@/enums'

const {
  getMhrReRegistrationPreviousOwnerGroups,
  getMhrReRegistrationPreviousTenancyType
} = storeToRefs(useStore())

</script>

<style lang="scss" scoped>
@use '@/assets/styles/theme.scss' as *;
</style>
