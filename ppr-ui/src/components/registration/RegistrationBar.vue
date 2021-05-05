<template>
  <v-container fluid no-gutters class="white pa-6">
    <v-row no-gutters class="pt-1">
      <v-col cols="3">
        <v-select :id="$style['registration-type-select']"
                  class="registration-bar-type-select"
                  :error-messages="categoryMessage ? categoryMessage : ''"
                  filled
                  :items="registrationTypes"
                  item-disabled="selectDisabled"
                  item-text="registrationTypeUI"
                  :label="selectedRegistrationType ? '' : registrationTypeLabel"
                  return-object
                  v-model="selectedRegistrationType">
        </v-select>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useActions } from 'vuex-composition-helpers'
import { RegistrationTypes } from '@/resources'
import { RegistrationTypeIF } from '@/interfaces' // eslint-disable-line no-unused-vars
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
  setup (props, { emit }) {
    const { setRegistrationType } = useActions<any>(['setRegistrationType'])
    const localState = reactive({
      autoCompleteIsActive: true,
      autoCompleteRegistrationValue: '',
      hideDetails: false,
      registrationTypes: RegistrationTypes,
      registrationTypeLabel: '+ New Security Agreement',
      selectedRegistrationType: props.defaultSelectedRegistrationType
    })
    watch(() => localState.selectedRegistrationType, (val: RegistrationTypeIF) => {
      if (val) {
        // alert('New Registration')
        setRegistrationType(val)
        emit('selected-registration-type', localState.selectedRegistrationType)
      }
    })
    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
#registration-btn {
  background-color: $primary-blue;
  color: white;
  height: 2.85rem;
  min-width: 0 !important;
  width: 3.5rem;
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
</style>
