<script setup lang="ts">
import { useStore } from '@/store/store'
import { useUserAccess } from '@/composables'
import { storeToRefs } from 'pinia'
import { ref } from 'vue'

defineEmits(['confirmQsRequirements'])

const { getIsAccountAdministrator } = storeToRefs(useStore())
const { downloadServiceAgreement } = useUserAccess()

const activePanels = ref<number[]>([0])
const qsUserGuideUrl = 'https://www2.gov.bc.ca/assets/gov/employment-business-and-economic-development/' +
  'business-management/permits-licences-and-registration/registries-other-assets/qs_transfers_sale_user_guide.pdf'
</script>

<template>
  <v-expansion-panels
    v-model="activePanels"
    multiple
  >
    <v-expansion-panel>
      <!-- Default Title -->
      <v-expansion-panel-title>
        <v-expand-transition>
          <v-row
            noGutters
            class="fs-14"
          >
            <v-col
              cols="12"
              class="d-inline-flex"
            >
              <v-icon color="primary pt-3">
                mdi-information-outline
              </v-icon>
              <h3 class="ml-2">
                Update to Qualified Supplier Accounts for Home Dealers
              </h3>
            </v-col>
          </v-row>
        </v-expand-transition>
      </v-expansion-panel-title>

      <!-- Panel Content-->
      <v-expansion-panel-text class="py-0 fs-14">
        <v-row noGutters>
          <v-col cols="12">
            <p>
              Your Qualified Supplier – Home Dealers' account now includes the following features, regardless of the
              home's location or ownership:
            </p>
          </v-col>

          <v-col
            cols="12"
            class="mt-4 ml-5"
          >
            <ul>
              <li class="my-1">
                Transfer due to Sale or Gift
                <a
                  :href="qsUserGuideUrl"
                  target="_blank"
                  class="text-decoration-none pl-0"
                >Read User Guide
                  <v-icon size="18">mdi-open-in-new</v-icon>
                </a>
              </li>
              <li>Transport Permits</li>
            </ul>
          </v-col>

          <v-divider
            v-if="getIsAccountAdministrator"
            class="ml-0 my-5"
          />
        </v-row>

        <v-row
          noGutters
        >
          <template v-if="getIsAccountAdministrator">
            <v-col cols="12">
              <p>
                <b>Terms</b>:  Your obligations are set out in the Qualified Supplier Agreement (QSA), and you are
                encouraged to review the QSA in its entirety.
              </p>
            </v-col>

            <v-col
              class="my-4"
              cols="12"
            >
              <p>
                Your responsibilities when electronically filing a transfer or transport permit are described in section
                4 of the QSA, and include:
              </p>
            </v-col>

            <v-col
              cols="12"
              class="ml-5"
            >
              <ul>
                <li class="my-1">
                  Verifying registered manufactured home ownership and location information.
                </li>
                <li>Verifying legal names, signatures and witnessing.</li>
                <li class="my-1">
                  Accurately recording the type of tenancy and ownership share.
                </li>
                <li>Correctly completing any forms that must be filed.</li>
                <li class="my-1">
                  Retaining documentation.
                </li>
              </ul>
            </v-col>

            <v-col
              class="mt-4"
              cols="12"
            >
              <p>
                For transfers, you must store bills of sale, other signed forms and supporting documentation for 7
                years.
                If requested, you must provide a copy or certified copy of stored documents to the requesting party
                within 7 business days at the fee level set by the Registrar.
              </p>
            </v-col>

            <v-col
              class="mt-4"
              cols="12"
            >
              <p>
                For transport permits, you must verify that a tax collectors certificate or confirmation stating that
                no taxes are outstanding for the current tax year has been issued, when applicable.
              </p>
            </v-col>

            <v-col cols="12">
              <v-btn
                class="generic-link px-0 mt-3 text-decoration-none"
                variant="plain"
                :ripple="false"
                @click="downloadServiceAgreement"
              >
                <img
                  alt=""
                  src="@/assets/svgs/pdf-icon-blue.svg"
                >
                <span class="pl-1">Review Qualified Supplier Agreement</span>
              </v-btn>
            </v-col>
          </template>

          <v-col
            v-if="!getIsAccountAdministrator"
            cols="12"
          >
            <p class="fs-12 mt-4 mb-4">
              <b>Note</b>: The administrator of the account must confirm the account updates.
            </p>
          </v-col>

          <v-col
            v-if="getIsAccountAdministrator"
            cols="12"
          >
            <v-btn
              class="mb-4 mt-4"
              :ripple="false"
              @click="$emit('confirmQsRequirements')"
            >
              <span class="font-weight-bold">Confirm Account Updates</span>
            </v-btn>
          </v-col>
        </v-row>
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>
<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
