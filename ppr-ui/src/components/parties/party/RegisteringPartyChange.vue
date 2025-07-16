<template>
  <v-row
    id="reg-party-change"
    no-gutters
  >
    <v-col v-if="!openChangeScreen">
      <RegisteringParty
        @change-registering-party="changeRegisteringParty"
        @editing-registering-party="editingRegisteringParty"
        @email-required-validation="emitRequiredEmail"
      />
    </v-col>
    <v-col
      v-else
      class="mt-2 mb-8"
    >
      <v-card
        flat
        class="add-party-container"
        :class="{ 'border-error-left': showErrorBar }"
      >
        <div class="px-6 pt-8">
          <h3
            v-if="!isSbc"
            class="pb-2"
          >
            Change Registering Party
          </h3>
          <span class="body-text">
            {{ !isSbc ? 'Change' : 'Include' }} the Registering Party
            by entering the registering party code
            or their name (business or person), or if the Registering Party you
            want to include is new (i.e., they do not have a registering party
            code) you can add their information manually.
          </span>
        </div>
        <PartySearch
          :is-auto-complete-disabled="addEditInProgress"
          :is-registering-party="true"
          @show-secured-party-add="initAdd"
          @hide-search="resetData"
        />
        <EditParty
          v-if="showAddRegisteringParty"
          :is-registering-party="true"
          @reset-event="resetData"
        />
        <div
          v-if="!showAddRegisteringParty"
          class="px-5 pt-0 pb-8"
          style="height:80px"
        >
          <v-btn
            v-if="!isSbc"
            id="cancel-btn-chg-reg-party"
            size="large"
            variant="outlined"
            color="primary"
            class="float-right"
            @click="resetData"
          >
            Cancel
          </v-btn>
        </div>
      </v-card>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  onMounted,
  watch,
  computed
} from 'vue'
import { useStore } from '@/store/store'
import type { PartyIF } from '@/interfaces'
import { storeToRefs } from 'pinia'

export default defineComponent({
  props: {
    isSummary: {
      type: Boolean,
      default: false
    },
    setShowErrorBar: {
      type: Boolean,
      default: false
    },
    changePartyProp: {
      type: Boolean,
      default: false
    }
  },
  emits: ['registeringPartyOpen', 'emailRequiredValidation'],
  setup (props, context) {
    const { getAddSecuredPartiesAndDebtors, isRoleStaffSbc } = storeToRefs(useStore())
    const localState = reactive({
      openChangeScreen: false,
      isSbc: isRoleStaffSbc.value,
      showAddRegisteringParty: false,
      addEditInProgress: false,
      registeringParty: computed((): PartyIF => {
        return getAddSecuredPartiesAndDebtors.value.registeringParty
      }),
      summaryView: computed((): boolean => {
        return props.isSummary
      }),
      showErrorBar: computed((): boolean => {
        return props.setShowErrorBar
      })
    })

    onMounted(() => {
      if ((isRoleStaffSbc.value) && ((!localState.registeringParty) || (!localState.registeringParty?.action))) {
        localState.openChangeScreen = true
        context.emit('registeringPartyOpen', true)
      }
    })

    const changeRegisteringParty = () => {
      localState.openChangeScreen = true
      context.emit('registeringPartyOpen', true)
    }

    const editingRegisteringParty = (val) => {
      context.emit('registeringPartyOpen', val)
    }

    const emitRequiredEmail = (val) => {
      context.emit('emailRequiredValidation', val)
    }

    const closeChangeRegisteringParty = () => {
      localState.openChangeScreen = false
      context.emit('registeringPartyOpen', false)
    }

    const initAdd = () => {
      localState.addEditInProgress = true
      localState.showAddRegisteringParty = true
      context.emit('registeringPartyOpen', true)
    }

    const resetData = () => {
      localState.addEditInProgress = false
      localState.showAddRegisteringParty = false
      localState.openChangeScreen = isRoleStaffSbc.value && ((!localState.registeringParty) ||
        (!localState.registeringParty.action))
      context.emit('registeringPartyOpen', false)
    }

    watch(() => localState.registeringParty, (rp) => {
      if (!rp && localState.isSbc) {
        localState.openChangeScreen = true
      }
    })

    watch(() => props.changePartyProp, (val) => {
      val ? changeRegisteringParty() : closeChangeRegisteringParty()
    })

    return {
      emitRequiredEmail,
      changeRegisteringParty,
      editingRegisteringParty,
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
