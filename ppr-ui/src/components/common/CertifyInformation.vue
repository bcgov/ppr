<template>
  <v-container
    id="certify-summary"
    class="px-0"
    role="region"
  >
    <h2>
      {{ `${sectionNumber ? sectionNumber + '.' : ''} Authorization` }}
    </h2>
    <p class="pb-6 pt-4">
      {{ infoText }}
    </p>
    <v-row
      no-gutters
      class="mb-5 party-summary"
    >
      <v-col>
        <v-table class="party-summary-table party-data-table">
          <template #default>
            <!-- Table Headers -->
            <thead>
              <tr>
                <th
                  v-for="header in authorizedTableHeaders"
                  :key="header.value"
                  :class="header.class"
                >
                  {{ header.text }}
                </th>
              </tr>
            </thead>

            <!-- Table Body -->
            <tbody v-if="registeringParty.length > 0">
              <tr
                v-for="(item, index) in registeringParty"
                :key="`${item}: ${index}`"
                class="party-row"
              >
                <td
                  class="list-item__title title-text icon-text"
                >
                  <v-icon class="v-icon">
                    mdi-account
                  </v-icon>
                  <span>{{ legalName }}</span>
                </td>
                <td class="pl-1">
                  {{ item.businessName }}
                </td>
                <td>
                  <base-address
                    :editing="false"
                    :schema="DefaultSchema"
                    :value="item.address"
                  />
                </td>
                <td>{{ item.emailAddress }}</td>
              </tr>
            </tbody>
          </template>
        </v-table>
      </v-col>
    </v-row>

    <v-row no-gutters>
      <v-col
        cols="12"
        class="pa-0"
        :class="showErrorComponent ? 'border-error-left': ''"
      >
        <v-card
          id="certify-information"
          flat
          class="px-6"
        >
          <v-row
            no-gutters
          >
            <v-col
              cols="3"
              class="generic-label pt-8"
            >
              <span :class="showErrorComponent ? 'error-text': ''">Confirm<br>Authorization</span>
            </v-col>
            <v-col
              cols="9"
              class="pt-2 ml-n1"
            >
              <v-row
                no-gutters
                class="pa-0"
              >
                <v-col
                  cols="12"
                  class="summary-text"
                >
                  <v-checkbox
                    id="checkbox-certified"
                    v-model="certified"
                    class="py-0 pr-0 pl-2 ma-0"
                    hide-details
                  >
                    <template #label>
                      <div class="pt-6">
                        <span :class="showErrorComponent ? 'error-text': ''">
                          I, <span
                            class="font-weight-bold"
                            :class="showErrorComponent ? 'error-text': ''"
                          >
                            {{ legalName }}</span>, have relevant knowledge of, and am authorized to submit,
                          this registration.
                        </span>
                      </div>
                    </template>
                  </v-checkbox>
                </v-col>
              </v-row>
              <v-row
                no-gutters
                class="pt-3 pb-8"
              >
                <v-col
                  cols="12"
                  class="pl-12 ma-0"
                >
                  <span class="summary-text"><span class="font-weight-bold">Date: </span>{{ currentDate }}</span>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
  watch,
  onMounted
} from 'vue'
import { useStore } from '@/store/store'
import { convertDate, getRegisteringPartyFromAuth } from '@/utils'
import { BaseAddress } from '@/composables/address'
import { DefaultSchema } from '@/composables/address/resources'
import type { CertifyIF, ContentIF, PartyIF } from '@/interfaces'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { storeToRefs } from 'pinia'
import { authorizedTableHeaders } from '@/resources'

export default defineComponent({
  name: 'CertifyInformation',
  components: {
    BaseAddress
  },
  props: {
    sectionNumber: {
      type: Number,
      required: false,
      default: null
    },
    setShowErrors: {
      type: Boolean,
      default: false
    },
    isMhr: {
      type: Boolean,
      default: false
    },
    content: {
      type: Object as () => ContentIF,
      default: () => {
      }
    }
  },
  emits: ['certifyValid'],
  setup (props, { emit }) {
    const { setCertifyInformation } = useStore()
    const {
      // Getters
      getCertifyInformation,
      getUserFirstName,
      getUserLastName,
      isRoleStaff,
      isRoleStaffSbc,
      isRoleStaffBcol,
      getUserEmail
    } = storeToRefs(useStore())

    const localState = reactive({
      legalName: '',
      certified: getCertifyInformation.value?.certified || false,
      infoText: props.content?.description ||
        'The following account information will be recorded by BC Registries upon registration and payment. ' +
        'This information is used to confirm you have the authority to submit this registration.',
      showErrors: computed((): boolean => {
        return props.setShowErrors
      }),
      showErrorComponent: computed((): boolean => {
        return (localState.showErrors && !localState.valid)
      }),
      certifyInformation: null,
      registeringParty: [] as Array<PartyIF>,
      currentDate: computed((): string => {
        return convertDate(new Date(), false, false)
      }),
      valid: computed((): boolean => {
        return localState.certified
      })
    })

    watch(
      () => localState.certified,
      (val: boolean) => {
        emit('certifyValid', localState.valid)
        localState.certifyInformation.certified = val
        localState.certifyInformation.valid = localState.valid
        setCertifyInformation(localState.certifyInformation)
      }
    )

    onMounted(async () => {
      const certifyInfo: CertifyIF = getCertifyInformation.value
      let update: boolean = false
      let email = ''
      if ((!certifyInfo.registeringParty) && (!isRoleStaff.value)) {
        update = true
        const regParty = await getRegisteringPartyFromAuth()
        if (regParty) {
          certifyInfo.registeringParty = regParty
        }
      }

      if (!certifyInfo.legalName) {
        update = true
        if (getUserFirstName.value && getUserLastName.value) {
          certifyInfo.legalName = `${getUserFirstName.value} ${getUserLastName.value}`
          if (certifyInfo.registeringParty) certifyInfo.registeringParty.emailAddress = getUserEmail.value
        } else {
          try {
            const token = sessionStorage.getItem(SessionStorageKeys.KeyCloakToken)
            const decodedToken = JSON.parse(atob(token?.split('.')[1]))
            if (decodedToken.firstname && decodedToken.lastname) {
              certifyInfo.legalName = decodedToken.firstname + ' ' + decodedToken.lastname
            } else if (decodedToken.name) {
              certifyInfo.legalName = decodedToken.name
            } else if (decodedToken.firstname) {
              certifyInfo.legalName = decodedToken.firstName
            } else if (decodedToken.lastname) {
              certifyInfo.legalName = decodedToken.lastname
            } else if (decodedToken.username) {
              certifyInfo.legalName = decodedToken.username
            } else {
              certifyInfo.legalName = 'Not Available'
            }
            email = decodedToken.email
          } catch (e) {
            console.error(e)
            certifyInfo.legalName = 'Not Available'
          }
        }
      }
      if (isRoleStaff.value) {
        if (isRoleStaffSbc.value) {
          certifyInfo.registeringParty = {
            businessName: 'SBC Staff',
            emailAddress: email
          }
        } else if (isRoleStaffBcol.value) {
          certifyInfo.registeringParty = {
            businessName: 'BC Online Help',
            emailAddress: email
          }
        } else {
          certifyInfo.registeringParty = {
            businessName: 'BC Registries Staff',
            emailAddress: email
          }
        }
      }

      if (update) {
        setCertifyInformation(certifyInfo)
      }
      localState.certifyInformation = certifyInfo
      if (localState.certifyInformation.registeringParty) {
        localState.registeringParty = [localState.certifyInformation.registeringParty]
      }
      localState.registeringParty = [certifyInfo.registeringParty]
      localState.legalName = localState.certifyInformation.legalName
      localState.certified = localState.certifyInformation.certified
    })

    return {
      DefaultSchema,
      authorizedTableHeaders,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.party-summary-table {
  .party-row {
    vertical-align: top;
  }
}
</style>
