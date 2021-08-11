<template>
  <v-container fluid class="pa-0">
    <v-btn
      id="registration-bar-btn"
      :class="[$style['registration-bar-btn'], 'copy-normal']"
      color="primary"
      @click="selectRegistration(registrationTypeValues.SECURITY_AGREEMENT)"
    >
      <template>
        <v-icon class="pr-1">mdi-plus</v-icon>
        Add New {{ registrationTypes.SECURITY_AGREEMENT }}
      </template>
    </v-btn>
    <!-- dropdown menu -->
    <v-menu offset-y left nudge-bottom="4" v-model="showMenu">
      <template v-slot:activator="{ on }">
        <v-btn
          id="registration-more-actions-btn"
          color="primary"
          :class="$style['actions__more-actions__btn']"
          class="px-0"
          v-on="on"
        >
          <v-icon v-if="showMenu">mdi-menu-up</v-icon>
          <v-icon v-else>mdi-menu-down</v-icon>
        </v-btn>
      </template>
      <v-list :class="[$style['actions__more-actions'], 'more-actions']">
        <v-list-item
          id="btn-security"
          class="copy-normal"
          @click="selectRegistration(registrationTypeValues.SECURITY_AGREEMENT)"
        >
          <v-list-item-title>
            {{ registrationTypes.SECURITY_AGREEMENT }}
            ({{ registrationTypeValues.SECURITY_AGREEMENT }})
          </v-list-item-title>
        </v-list-item>

        <v-list-item
          id="btn-reparers"
          class="copy-normal"
          @click="selectRegistration(registrationTypeValues.REPAIRERS_LIEN)"
        >
          <v-list-item-title>
            {{ registrationTypes.REPAIRERS_LIEN }}
            ({{ registrationTypeValues.REPAIRERS_LIEN }})
          </v-list-item-title>
        </v-list-item>

        <v-list-item
          id="btn-marriage"
          class="copy-normal"
          @click="selectRegistration(registrationTypeValues.MARRIAGE_MH)"
        >
          <v-list-item-title>
            {{ registrationTypes.MARRIAGE_MH }}
            ({{ registrationTypeValues.MARRIAGE_MH }})
          </v-list-item-title>
        </v-list-item>

        <v-list-item
          id="btn-land"
          class="copy-normal"
          @click="selectRegistration(registrationTypeValues.LAND_TAX_LIEN)"
        >
          <v-list-item-title>
            {{ registrationTypes.LAND_TAX_LIEN }}
            ({{ registrationTypeValues.LAND_TAX_LIEN }})
          </v-list-item-title>
        </v-list-item>

        <v-list-item
          id="btn-sale"
          class="copy-normal"
          @click="selectRegistration(registrationTypeValues.SALE_OF_GOODS)"
        >
          <v-list-item-title>
            {{ registrationTypes.SALE_OF_GOODS }}
            ({{ registrationTypeValues.SALE_OF_GOODS }})
          </v-list-item-title>
        </v-list-item>

        <v-list-item
          id="btn-mhl"
          class="copy-normal"
          @click="
            selectRegistration(registrationTypeValues.MANUFACTURED_HOME_LIEN)
          "
        >
          <v-list-item-title>
            {{ registrationTypes.MANUFACTURED_HOME_LIEN }}
            ({{ registrationTypeValues.MANUFACTURED_HOME_LIEN }})
          </v-list-item-title>
        </v-list-item>

        <v-list-item
          id="btn-fcl"
          class="copy-normal"
          @click="
            selectRegistration(registrationTypeValues.FORESTRY_CONTRACTOR_LIEN)
          "
        >
          <v-list-item-title>
            {{ registrationTypes.FORESTRY_CONTRACTOR_LIEN }}
            ({{ registrationTypeValues.FORESTRY_CONTRACTOR_LIEN }})
          </v-list-item-title>
        </v-list-item>

        <v-list-item
          id="btn-fcc"
          class="copy-normal"
          @click="
            selectRegistration(
              registrationTypeValues.FORESTRY_CONTRACTOR_CHARGE
            )
          "
        >
          <v-list-item-title>
            {{ registrationTypes.FORESTRY_CONTRACTOR_CHARGE }}
            ({{ registrationTypeValues.FORESTRY_CONTRACTOR_CHARGE }})
          </v-list-item-title>
        </v-list-item>

        <v-list-item
          id="btn-fsl"
          class="copy-normal"
          @click="
            selectRegistration(
              registrationTypeValues.FORESTRY_SUBCONTRACTOR_LIEN
            )
          "
        >
          <v-list-item-title>
            {{ registrationTypes.FORESTRY_SUBCONTRACTOR_LIEN }}
            ({{ registrationTypeValues.FORESTRY_SUBCONTRACTOR_LIEN }})
          </v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-container>
</template>
<script lang="ts">
import { defineComponent, reactive, toRefs } from '@vue/composition-api'

import { RegistrationTypes } from '@/resources'
import { UIRegistrationTypes, APIRegistrationTypes } from '@/enums'

export default defineComponent({
  name: 'RegistrationBarButtonList',
  emits: ['selected'],
  setup (props, { emit }) {
    const localState = reactive({
      registrationTypes: UIRegistrationTypes,
      registrationTypeValues: APIRegistrationTypes,
      showMenu: false
    })
    const selectRegistration = (val: APIRegistrationTypes) => {
      const reg = RegistrationTypes.find(
        function (reg, index) {
          if (reg.registrationTypeAPI === val) {
            return true
          }
        })
      emit('selected', reg)
    }

    return {
      selectRegistration,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" module>
@import "@/assets/styles/theme.scss";
.actions__more-actions__btn {
  width: 50px;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  box-shadow: none;
  margin-left: 1px;
}
.registration-bar-btn {
  min-width: 0 !important;
  width: 270px;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  background-color: $primary-blue;
  color: white;
  height: 2.85rem;
  font-weight: normal;
  box-shadow: none;
}
.registration-list-item {
  color: $gray7 !important;
}
</style>
