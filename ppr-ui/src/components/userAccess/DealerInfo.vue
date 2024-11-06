<script setup lang="ts">
import { useStore } from '@/store/store'
import { useUserAccess } from '@/composables'
import { storeToRefs } from 'pinia'
import { ref } from 'vue'

const { getIsAccountAdministrator } = storeToRefs(useStore())
const { downloadServiceAgreement } = useUserAccess()

const activePanels = ref<number[]>([0])
const qsUserGuideUrl = 'https://www2.gov.bc.ca/assets/gov/employment-business-and-economic-development/' +
  'business-management/permits-licences-and-registration/registries-other-assets/qs_transfers_sale_user_guide.pdf'

const acceptTerms = () => {
  console.log('API PUT accepted agreement terms here')
}
</script>

<template>
  <v-expansion-panels
    v-model="activePanels"
    multiple
  >
    <v-expansion-panel>
      <!-- Default Notice Title Content -->
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

      <!-- Add/Edit Notice/Order Content-->
      <v-expansion-panel-text class="py-0 fs-14">
        <v-col cols="12">
          <p class="mt-n5">
            We’ve recently updated features and policies within your Qualified Supplier – Home Dealers account to
            now include:
          </p>
        </v-col>

        <v-col
          cols="12"
          class="pt-1 ml-5"
        >
          <ul>
            <li class="my-1">
              Transfer due to Sale or Gift, including cases where you are not the owner.
              <a
                :href="qsUserGuideUrl"
                target="_blank"
                class="text-decoration-none pl-0"
              >Read User Guide
                <v-icon size="18">mdi-open-in-new</v-icon>
              </a>
            </li>
            <li>Transport Permits can now be filed no matter the location of the home.</li>
          </ul>
        </v-col>

        <v-divider
          v-if="getIsAccountAdministrator"
          class="ml-0 mb-5 mt-2"
        />

        <v-row
          noGutters
        >
          <v-col
            v-if="getIsAccountAdministrator"
            cols="12"
          >
            <p>
              <b>Terms</b>: All filed documents and supporting documents will be stored for 7 years. If requested, a
              copy or certified copy of filed documents (such as the Bill of Sale, or other signed forms), will be
              provided within 7 business days, at the fee level set by the Registrar.
            </p>
          </v-col>

          <v-col
            v-if="getIsAccountAdministrator"
            cols="12"
          >
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

          <v-col cols="12">
            <p class="fs-12 mt-2 mb-4">
              <b>Note</b>: The administrator of the account must confirm the account updates.
            </p>
          </v-col>

          <v-col
            v-if="getIsAccountAdministrator"
            cols="12"
          >
            <v-btn
              class="mb-4 mt-1"
              :ripple="false"
              @click="acceptTerms"
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
