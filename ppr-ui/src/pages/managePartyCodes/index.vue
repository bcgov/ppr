<template>
  <div class="mx-auto py-6">

    <div class="grid grid-cols-1 lg:grid-cols-12">
      <!-- Main column -->
      <main class="lg:col-span-9 pr-2">
        <div class="py-6 rounded bg-inherit" aria-label="header">
          <h1 class="text-2xl font-semibold text-slate-800">Party Codes</h1>
          <p class="mt-1 text-sm">Party codes allow for quick entry of Registering and Secured party
            information when creating registrations. There is no fee to create a party code. Changes to a party code
            will update the name, mailing address, and/or email address in all active registrations where the code was
            used, and incur a $100.00 change fee.</p>

          <SimpleHelpToggle
            toggle-button-title="Help with Party Codes"
            class="my-2"
          >
            <template #content>
              <h3 class="mb-7">What is a party code</h3>
              <p>
                The Form 3 Registering\/Secured party code is a short numeric code that references the name, mailing
                address, and email address to be used when you are identified as the Registering Party and\/or the
                Secured Party in a registration in the Personal Property Registry.
              </p>

              <p class="mt-4 mb-1">A party code has several benefits:</p>
              <ol class="ml-6">
                <li>
                  Quick entry of a Registering and\/or Secured Party name, mailing address, and email address when
                  creating a registration in which you or a third party (e.g., a law firm) are a party.
                </li>
                <li>
                  When you change your legal name, mailing address, or email address, updating the party code updates
                  all active prior registrations where the code was used, avoiding individual amendments and associated
                  fees.
                </li>
                <li>
                  If a third party amends or discharges registrations where you are a secured party and your party code
                  was used, you will automatically receive verification statements for those registrations in your
                  Personal Property Registry account dashboard.
                </li>
              </ol>

              <h4 class="mt-4">How to create a code</h4>
              <p>
                A party code consists of two main parts:
              </p>
              <ol class="ml-6">
                <li>the party name that you want to appear on your registrations</li>
                <li>a location, consisting of a mailing address and an email address</li>
              </ol>
              <ul class="ml-6 mt-4 list-disc">
                <li>
                  The party name used in the code should be the complete legal name of either a person or business. The address should be the mailing address of this person or business.
                </li>
                <li>
                  There can be only one party name used with your account, but you can have as many locations as you want, for example, if your business has multiple branches and you create registrations using the different branches.
                </li>
                <li>
                  To create your code, you can use the default name that is associated with your BC Registries account, or you can change this to a custom name (remember \- this name will be the name that appears on your registrations and has legal implications).
                </li>
                <li>
                  Once you have your name entered, select <em>Add a Location</em> to enter the address and email address for the code.
                </li>
                <li>
                  When you are done entering your location information, a party code will automatically be generated and displayed in your Locations table.
                </li>
                <li>
                  Complete your code creation by reviewing and confirming the information in the code.
                </li>
                <li>
                  It is not possible to request a specific party code.
                </li>
              </ul>

              <h4 class="mt-4">How to use a code</h4>
              <ul class="ml-6 list-disc">
                <li>
                  When you are creating registrations your default party code information will be displayed as the Registering Party. However, you can change this code by entering one of your party codes or your party name in the Registering Party selection field.
                </li>
                <li>
                  You can add yourself as a secured party in the same manner: by entering one of your party codes or your party name in the Secured Party selection field.
                </li>
                <li>
                  Third parties (e.g., a law firm) can similarly create registrations using your party code or party name to identify you as the Registering Party and/or Secured Party.
                </li>
                <li>
                  You can update your party name or mailing address, or email address in any active, prior registration in which a code was used simply by changing the information in the code. Registering Party and Secured Party information in discharged or expired registrations is not updated by party code changes.
                </li>
              </ul>

              <h4 class="mt-4">Fees</h4>
              <p>
                There is no fee to create a new code. <br>A fee of $100.00 applies when updating all active prior
                registrations by changing the party name, mailing address, or email address of a code.
              </p>
            </template>
          </SimpleHelpToggle>
        </div>

        <!-- Party Codes Card -->
        <section>
          <div class="px-6">
            <div class="flex items-start justify-between">
              <div>
                <h2 class="text-lg font-medium text-slate-800">Party Name Section</h2>
                <p class="mt-1 text-sm text-slate-500">
                  Party Name Section allows users to create, edit, and delete party codes.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section>
          <div class="py-6">
            <div class="flex items-start justify-between">
              <div>
                <h2 class="text-lg font-medium text-slate-800">Party Locations Section</h2>
                <p class="mt-1 text-sm text-slate-500">
                  Party locations Section allows users to add locations to the party
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <!-- Sidebar -->
      <div class="col-span-3 ml-4 mt-[30px]">
        <aside>
          <ConnectFeeWidget />
        </aside>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { onMounted } from 'vue'
import { SimpleHelpToggle } from '@/components/common'
import { useConnectFeesHandler } from '@/composables'
import { storeToRefs } from 'pinia'
import { useConnectFeeStore } from '@/store/connectFee'
import { FeeSummaryTypes } from '@/composables/fees/enums'

const { setRegistrationFees } = useConnectFeesHandler()
const { feeOptions, userSelectedPaymentMethod } = storeToRefs(useConnectFeeStore())

onMounted(() => {
  setRegistrationFees(FeeSummaryTypes.PARTY_CODES)
})
</script>
<style scoped lang="scss">
ol {
  list-style-type: revert;
}

</style>
