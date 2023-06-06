<template>
  <v-container class="pa-0 flat">
    <v-row v-if="options.header" class="summary-header rounded-top" no-gutters>
      <v-col cols="auto" class="pa-4">
        <v-icon v-if="options.iconImage" :color="options.iconColor">{{ options.iconImage }}</v-icon>
        <label class="pl-3 sectionText">
          <strong>{{ options.header }}</strong>
        </label>
      </v-col>
    </v-row>

    <v-row no-gutters>
      <v-col>
        <v-simple-table class="party-summary-table party-data-table">
          <template v-slot:default>
            <!-- Table Headers -->
            <thead>
              <tr>
                <th v-for="header in headers" :key="header.value" :class="header.class">
                  {{ header.text }}
                </th>
              </tr>
            </thead>

            <!-- Table Body -->
            <tbody v-if="items.length > 0">
              <tr
                v-for="(item, index) in items" :key="`${item}: ${index}`"
                class="party-row"
                :class="{ 'disabled-text-not-first': item.action === ActionTypes.REMOVED}"
              >
                <td class="list-item__title title-text" style="padding-left:30px">
                  <v-row no-gutters>
                    <v-col cols="auto">
                      <div class="icon-div mt-n1 pr-4">
                        <v-icon v-if="isBusiness(item)">mdi-domain</v-icon>
                        <v-icon v-else>mdi-account</v-icon>
                      </div>
                    </v-col>
                    <v-col cols="9">
                      <div :class="{ 'disabled-text': item.action === ActionTypes.REMOVED}">
                        {{ getName(item) }}
                      </div>
                      <div v-if="item.action && registrationFlowType === RegistrationFlowType.AMENDMENT">
                        <v-chip
                          v-if="item.action === ActionTypes.REMOVED"
                          x-small label color="#grey lighten-2" text-color="$gray9"
                        >
                          {{ item.action }}
                        </v-chip>
                        <v-chip v-else x-small label color="primary" text-color="white">
                          {{ item.action }}
                        </v-chip>
                      </div>
                    </v-col>
                  </v-row>
                </td>
                <td>
                  <base-address
                    :editing="false"
                    :schema="DefaultSchema"
                    :value="item.address"
                  />
                </td>
                <td>{{ item.emailAddress }}</td>
                <td v-if="options.isDebtorSummary">{{ getFormattedBirthdate(item) }}</td>
                <td v-else>{{ item.code }}</td>
              </tr>
            </tbody>
            <tbody v-else-if="options.enableNoDataAction">
              <tr class="text-center">
                <td :colspan="2" class="border-error-left">
                  <v-icon color="error">mdi-information-outline</v-icon>
                  <span class="invalid-message">This step is unfinished.</span>
                  <span class="invalid-link" @click="noDataAction()">Return to this step to complete it.</span>
                </td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  computed,
  toRefs
} from 'vue-demi'
import { useStore } from '@/store/store'
import { BaseAddress } from '@/composables/address'
import { DefaultSchema } from '@/composables/address/resources'
import { useParty } from '@/composables/useParty'
import { BaseHeaderIF, PartyIF, PartySummaryOptionsI } from '@/interfaces' // eslint-disable-line no-unused-vars
import { RegistrationFlowType, ActionTypes, APIRegistrationTypes } from '@/enums'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'BasePartySummary',
  components: {
    BaseAddress
  },
  props: {
    setHeaders: {
      default: () => [] as Array<BaseHeaderIF>
    },
    setItems: {
      default: () => [] as Array<PartyIF>
    },
    setOptions: {
      default: () => {
        return {
          enableNoDataAction: false,
          header: '',
          iconColor: '',
          iconImage: '',
          isDebtorSummary: false,
          isRegisteringParty: false
        } as PartySummaryOptionsI
      }
    }
  },
  emits: ['triggerNoDataAction'],
  setup (props, { emit }) {
    const { getRegistrationFlowType, getRegistrationType } = storeToRefs(useStore())
    const registrationFlowType = getRegistrationFlowType.value
    const registrationType = getRegistrationType.value.registrationTypeAPI
    const localState = reactive({
      headers: props.setHeaders,
      items: computed((): PartyIF[] => {
        if ((registrationFlowType === RegistrationFlowType.AMENDMENT) && (!localState.options.isRegisteringParty) &&
         (registrationType !== APIRegistrationTypes.REPAIRERS_LIEN)) {
          const displayArray = []
          for (let i = 0; i < props.setItems.length; i++) {
            if (props.setItems[i].action) {
              displayArray.push(props.setItems[i])
            }
          }
          return displayArray
        } else {
          return props.setItems
        }
      }),
      options: props.setOptions as PartySummaryOptionsI
    })
    const noDataAction = (): void => {
      emit('triggerNoDataAction', true)
    }
    const { getFormattedBirthdate, getName, isBusiness } = useParty()

    return {
      ...toRefs(localState),
      registrationFlowType,
      RegistrationFlowType,
      ActionTypes,
      getFormattedBirthdate,
      getName,
      isBusiness,
      noDataAction,
      DefaultSchema
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.sectionText {
  color: $gray9;
}
</style>
