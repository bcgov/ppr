<template>
  <v-row no-gutters>
      <v-col v-if="!openChangeScreen">
        <registering-party
          @changeRegisteringParty="changeRegisteringParty"
        />
      </v-col>
      <v-col v-else>
        <v-card flat class="add-party-container mt-2 mb-8">
          <div class="px-6 pt-8">
            <h3 v-if="!isSbc" class="pb-2">Change Registering Party</h3>
            <span class="body-text">
            {{ !isSbc ? 'Change' : 'Include' }} the Registering Party
            by entering the registering party code
            or their name (business or person), or if the Registering Party you
            want to include is new (i.e., they do not have a registering party
            code) you can add their information manually.
            </span>
          </div>
          <party-search
            :isAutoCompleteDisabled="addEditInProgress"
            :setIsRegisteringParty="true"
            @showSecuredPartyAdd="initAdd"
            @hideSearch="openChangeScreen = false"
          />
          <div v-if="showAddRegisteringParty">
            <edit-party :setIsRegisteringParty="true" @resetEvent="resetData" />
          </div>
          <div v-if="!showAddRegisteringParty" class="px-5 pt-0 pb-8" style="height:80px">
            <v-btn
              v-if="!isSbc"
              id="cancel-btn-chg-reg-party"
              large
              outlined
              color="primary"
              class="float-right"
              @click="openChangeScreen = false"
            >
              Cancel
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>
</template>

<script lang="ts">
// external libraries
import {
  defineComponent,
  reactive,
  toRefs,
  onMounted,
  watch,
  computed
} from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
// local components
import { EditParty, PartySearch, RegisteringParty } from '@/components/parties/party'
// local helpers / types / etc.
import { PartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  components: {
    PartySearch,
    EditParty,
    RegisteringParty
  },
  props: {
    isSummary: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { getAddSecuredPartiesAndDebtors } = useGetters<any>([
      'getAddSecuredPartiesAndDebtors'
    ])
    const { isRoleStaffSbc } = useGetters<any>(['getRegistrationType', 'isRoleStaffSbc'])
    const localState = reactive({
      securedParties: getAddSecuredPartiesAndDebtors.value.securedParties,
      debtors: getAddSecuredPartiesAndDebtors.value.debtors,
      openChangeScreen: false,
      isSbc: isRoleStaffSbc.value,
      showAddRegisteringParty: false,
      addEditInProgress: false,
      cautionTxt: 'The Registry will not send the verification statement for this registration ' +
        'to the Registering Party named above.',
      registeringParty: computed((): PartyIF => {
        return getAddSecuredPartiesAndDebtors.value.registeringParty
      }),
      summaryView: computed((): boolean => {
        return props.isSummary
      })
    })

    onMounted(() => {
      if ((isRoleStaffSbc.value) && ((!localState.registeringParty) || (!localState.registeringParty?.action))) {
        localState.openChangeScreen = true
      }
    })

    const changeRegisteringParty = () => {
      localState.openChangeScreen = true
    }

    const initAdd = () => {
      localState.addEditInProgress = true
      localState.showAddRegisteringParty = true
    }

    const resetData = () => {
      localState.addEditInProgress = false
      localState.showAddRegisteringParty = false
      localState.openChangeScreen = false
      if ((isRoleStaffSbc.value) && (!localState.registeringParty.action)) {
        localState.openChangeScreen = true
      }
    }

    watch(() => localState.registeringParty, (rp) => {
      if (!rp && localState.isSbc) {
        localState.openChangeScreen = true
      }
    })

    return {
      changeRegisteringParty,
      initAdd,
      resetData,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
  .body-text {
    color: $gray7;
  }
</style>
