<template>
  <v-card
    class="pa-0 mx-0"
    flat
    role="region"
  >
    <v-row
      v-if="options.header"
      class="summary-header rounded-top"
      noGutters
    >
      <v-col
        cols="auto"
        class="pa-4"
      >
        <v-icon
          v-if="options.iconImage"
          :color="options.iconColor"
        >
          {{ options.iconImage }}
        </v-icon>
        <label class="pl-3 sectionText">
          <strong>{{ options.header }}</strong>
        </label>
      </v-col>
    </v-row>

    <v-row noGutters>
      <v-col>
        <v-table class="party-summary-table party-data-table">
          <template #default>
            <!-- Table Headers -->
            <thead>
              <tr>
                <th
                  v-for="header in headers"
                  :key="header.value"
                  :class="header.class"
                >
                  {{ header.text }}
                </th>
              </tr>
            </thead>

            <!-- Table Body -->
            <tbody v-if="items.length > 0">
              <tr
                v-for="(item, index) in items"
                :key="`${item}: ${index}`"
                class="party-row"
                :class="{ 'disabled-text-not-first': item?.action === ActionTypes.REMOVED}"
              >
                <td
                  class="list-item__title"
                >
                  <v-row
                    noGutters
                    :aria-label="`${isBusiness(item) ? 'Business' : 'Person'} ${getName(item)}`"
                  >
                    <v-col cols="auto">
                      <div class="icon-div mt-n1 pr-2">
                        <v-icon v-if="isBusiness(item)">
                          mdi-domain
                        </v-icon>
                        <v-icon v-else>
                          mdi-account
                        </v-icon>
                      </div>
                    </v-col>
                    <v-col
                      cols="9"
                      aria-hidden="true"
                    >
                      <div :class="{ 'disabled-text': item?.action === ActionTypes.REMOVED}">
                        <span class="font-weight-bold">{{ getName(item) }}</span>
                      </div>
                      <div v-if="item?.action && registrationFlowType === RegistrationFlowType.AMENDMENT">
                        <v-chip
                          v-if="item?.action === ActionTypes.REMOVED"
                          xSmall
                          variant="elevated"
                          color="greyLighten"
                        >
                          {{ item?.action }}
                        </v-chip>
                        <v-chip
                          v-else
                          xSmall
                          variant="elevated"
                          color="primary"
                        >
                          {{ item?.action }}
                        </v-chip>
                      </div>
                    </v-col>
                  </v-row>
                </td>
                <td>
                  <BaseAddress
                    :editing="false"
                    :schema="DefaultSchema"
                    :value="item?.address"
                  />
                </td>
                <td>{{ item?.emailAddress }}</td>
                <td v-if="options.isDebtorSummary">
                  {{ getFormattedBirthdate(item) }}
                </td>
                <td v-else>
                  {{ item?.code }}
                </td>
              </tr>
            </tbody>
            <tbody v-else-if="options.enableNoDataAction">
              <tr>
                <td
                  :colspan="headers.length"
                  class="error-text text-left border-error-left"
                >
                  <v-icon color="error ml-2">
                    mdi-information-outline
                  </v-icon>
                  <span class="error-text fs-16 ml-2">This step is unfinished.</span>
                  <span
                    class="generic-link fs-16"
                    @click="noDataAction()"
                  >Return to this step to complete it.</span>
                </td>
              </tr>
            </tbody>
          </template>
        </v-table>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  computed,
  toRefs
} from 'vue'
import { useStore } from '@/store/store'
import { BaseAddress } from '@/composables/address'
import { DefaultSchema } from '@/composables/address/resources'
import { useParty } from '@/composables/useParty'
import { BaseHeaderIF, PartyIF, PartySummaryOptionsI } from '@/interfaces'
import { RegistrationFlowType, ActionTypes, APIRegistrationTypes } from '@/enums'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'BasePartySummary',
  components: {
    BaseAddress
  },
  props: {
    setHeaders: {
      type: Array,
      default: () => [] as Array<BaseHeaderIF>
    },
    setItems: {
      type: Array,
      default: () => [] as Array<PartyIF>
    },
    setOptions: {
      type: Object,
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
    const registrationType = getRegistrationType.value?.registrationTypeAPI
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
