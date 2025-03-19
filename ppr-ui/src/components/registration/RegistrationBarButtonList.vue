<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue'
import { RegistrationTypes } from '@/resources'
import { UIRegistrationTypes, APIRegistrationTypes } from '@/enums'
import { getFeatureFlag } from '@/utils'

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
        function (reg) {
          if (reg.registrationTypeAPI === val) {
            return true
          }
        })
      emit('selected', reg)
    }

    return {
      getFeatureFlag,
      selectRegistration,
      ...toRefs(localState)
    }
  }
})
</script>
<template>
  <v-container
    id="reg-btn-list"
    fluid
    class="pa-0"
  >
    <div class="d-flex">
      <v-btn
        id="registration-bar-btn"
        class="registration-bar-btn copy-normal"
        color="primary"
        @click="selectRegistration(registrationTypeValues.SECURITY_AGREEMENT)"
      >
        <template #append />
        <v-icon class="pr-2">
          mdi-note-plus-outline
        </v-icon>
        Create New {{ registrationTypes.SECURITY_AGREEMENT }}
      </v-btn>
      <!-- dropdown menu -->
      <v-menu
        v-model="showMenu"
        location="bottom"
        attach="#reg-btn-list"
      >
        <template #activator="{ props }">
          <v-btn
            id="registration-more-actions-btn"
            color="primary"
            class="actions__more-actions__btn"
            v-bind="props"
          >
            <v-icon v-if="showMenu">
              mdi-menu-up
            </v-icon>
            <v-icon v-else>
              mdi-menu-down
            </v-icon>
          </v-btn>
        </template>
        <v-list class="actions__more-actions more-actions registration-list">
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
            v-if="getFeatureFlag('cla-enabled')"
            id="btn-commercial-lien"
            class="copy-normal"
            @click="selectRegistration(registrationTypeValues.COMMERCIAL_LIEN)"
          >
            <v-list-item-title>
              {{ registrationTypes.COMMERCIAL_LIEN }}
              ({{ registrationTypeValues.COMMERCIAL_LIEN }})
            </v-list-item-title>
          </v-list-item>

          <v-list-item
            v-else
            id="btn-repairers"
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
    </div>
  </v-container>
</template>
<style lang="scss" scoped>
@import "@/assets/styles/theme.scss";
.registration-bar-btn {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}
.actions__more-actions__btn {
  min-width: unset;
  width: 45px;
  margin-left: 1px;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}
.registration-list {
  left: -272px;
}
</style>
