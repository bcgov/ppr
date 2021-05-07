<template>
  <v-container fluid no-gutters class="registration-bar">
    <v-row no-gutters class="pt-1">
      <v-col cols="4">
        <div class="actions">
        <v-btn
          class="registration-bar-btn"
          color="primary"
          :error-messages="categoryMessage ? categoryMessage : ''"
          :disabled="selectDisabled"
          @click="newRegistration(registrationTypeValues.SECURITY_AGREEMENT)"
        >
          <template>
            <span
              ><v-icon>mdi-plus</v-icon> Add New
              {{ registrationTypes.SECURITY_AGREEMENT }}</span
            >
          </template>
        </v-btn>
        <!-- dropdown menu -->
        <v-menu offset-y left nudge-bottom="4">
          <template v-slot:activator="{ on }">
            <v-btn
              color="primary"
              class="actions__more-actions__btn px-0"
              v-on="on"
              id="menu-activator"
            >
              <v-icon>mdi-menu-down</v-icon>
            </v-btn>
          </template>
          <v-list class="actions__more-actions">
            <v-list-item
              id="btn-reparers"
              @click="newRegistration(registrationTypeValues.REPAIRERS_LIEN)"
            >
              <v-list-item-title>{{
                registrationTypes.REPAIRERS_LIEN
              }}</v-list-item-title>
            </v-list-item>

            <v-list-item
              id="btn-marriage"
              @click="newRegistration(registrationTypeValues.MARRIAGE_MH)"
            >
              <v-list-item-title>{{
                registrationTypes.MARRIAGE_MH
              }}</v-list-item-title>
            </v-list-item>
            <v-list-item
              id="btn-sale"
              @click="newRegistration(registrationTypeValues.SALE_OF_GOODS)"
            >
              <v-list-item-title>{{
                registrationTypes.SALE_OF_GOODS
              }}</v-list-item-title>
            </v-list-item>
            <v-list-item
              id="btn-land"
              @click="newRegistration(registrationTypeValues.LAND_TAX_LIEN)"
            >
              <v-list-item-title>{{
                registrationTypes.LAND_TAX_LIEN
              }}</v-list-item-title>
            </v-list-item>
            <v-list-item
              id="btn-mhl"
              @click="
                newRegistration(registrationTypeValues.MANUFACTURED_HOME_LIEN)
              "
            >
              <v-list-item-title>{{
                registrationTypes.MANUFACTURED_HOME_LIEN
              }}</v-list-item-title>
            </v-list-item>
            <v-list-item
              id="btn-fcl"
              @click="
                newRegistration(registrationTypeValues.FORESTRY_CONTRACTOR_LIEN)
              "
            >
              <v-list-item-title>{{
                registrationTypes.FORESTRY_CONTRACTOR_LIEN
              }}</v-list-item-title>
            </v-list-item>
            <v-list-item
              id="btn-fcc"
              @click="
                newRegistration(
                  registrationTypeValues.FORESTRY_CONTRACTOR_CHARGE
                )
              "
            >
              <v-list-item-title>{{
                registrationTypes.FORESTRY_CONTRACTOR_CHARGE
              }}</v-list-item-title>
            </v-list-item>
            <v-list-item
              id="btn-fsl"
              @click="
                newRegistration(
                  registrationTypeValues.FORESTRY_SUBCONTRACTOR_LIEN
                )
              "
            >
              <v-list-item-title>{{
                registrationTypes.FORESTRY_SUBCONTRACTOR_LIEN
              }}</v-list-item-title>
            </v-list-item>
            <v-list-item
              id="btn-mr"
              @click="
                newRegistration(
                  registrationTypeValues.MISCELLANEOUS_REGISTRATION
                )
              "
            >
              <v-list-item-title>{{
                registrationTypes.MISCELLANEOUS_REGISTRATION
              }}</v-list-item-title>
            </v-list-item>
            <v-list-item
              id="btn-mo"
              @click="
                newRegistration(registrationTypeValues.MISCELLANEOUS_OTHER)
              "
            >
              <v-list-item-title>{{
                registrationTypes.MISCELLANEOUS_OTHER
              }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from '@vue/composition-api'
import { useActions } from 'vuex-composition-helpers'
import { RegistrationTypeIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { UIRegistrationTypes, APIRegistrationTypes } from '@/enums'
import { RegistrationTypes } from '@/resources'

// import AutoComplete from '@/components/registration/AutoComplete.vue'

export default defineComponent({
  // components: {
  //  AutoComplete
  // },
  props: {
    defaultSelectedRegistrationType: {
      type: Object as () => RegistrationTypeIF
    },
    registrationTitle: {
      type: String,
      default: 'My Registrations'
    }
  },
  emits: ['selected-registration-type'],
  setup (props, { emit }) {
    const { setRegistrationType } = useActions<any>(['setRegistrationType'])
    const localState = reactive({
      autoCompleteIsActive: true,
      autoCompleteRegistrationValue: '',
      hideDetails: false,
      categoryMessage: '',
      selectDisabled: false,
      registrationTypes: UIRegistrationTypes,
      registrationTypeValues: APIRegistrationTypes,
      registrationTypeLabel: '+ New Security Agreement',
      selectedRegistrationType: props.defaultSelectedRegistrationType
    })
    const newRegistration = (val: APIRegistrationTypes) => {
      const reg = RegistrationTypes.find(
        function (reg, index) {
          if (reg.registrationTypeAPI === val) {
            return true
          }
        })
      setRegistrationType(reg)
      console.log(reg)
      emit('selected-registration-type', reg)
    }

    return {
      newRegistration,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import "@/assets/styles/theme.scss";

::v-deep .registration-bar-btn {
  min-width: 0 !important;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  background-color: $primary-blue;
  color: white;
  height: 2.85rem;
  font-weight: normal;
  box-shadow: none;
}
::v-deep .actions__more-actions__btn {
  width: 40;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  box-shadow: none;
}

#search-btn-info {
  color: $gray8;
  font-size: 0.725rem;
}
.registration-info {
  color: $gray8;
  font-size: 0.875rem;
}
.registration-title {
  color: $gray9;
  font-size: 1rem;
}
.registration-select {
  background-color: $BCgovBlue3;
  color: white;
}
::v-deep .v-list-item .v-list-item__title {
  font-size: 0.875rem;
  color: $gray9;
}
::v-deep .v-list-item:hover {
  background-color: $gray3;
  color: $primary-blue;
}
</style>
