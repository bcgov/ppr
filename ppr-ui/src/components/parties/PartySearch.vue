<template>
  <v-container fluid no-gutters class="white pa-0">
    <v-row class="px-6" align="center">
      <v-col cols="6">
        <v-text-field
          filled
          label="Secured Party Code or Name"
          id="txt-code"
          :hide-details="true"
          persistent-hint
        />
      </v-col>
      <v-col cols="6">
        or
        <a id="add-party" @click="goToAddSecuredParty"
          >Add a Secured Party that doesn't have a code</a
        >
      </v-col>
    </v-row>
    <v-row class="px-6" align="center">
      <v-col cols="auto">
        <v-checkbox
          id="add-registering-party"
          class="reg-checkbox pa-0 ma-0"
          @click="addRegisteringParty"
          :hide-details="true"
          >
        </v-checkbox>
      </v-col>
      <v-col>
        Include the registering party as a secured party
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs
} from '@vue/composition-api'

export default defineComponent({
  emits: ['showSecuredPartyAdd'],
  setup (props, context) {
    const localState = reactive({})

    const goToAddSecuredParty = () => {
      context.emit('showSecuredPartyAdd')
    }

    const addRegisteringParty = () => {
      context.emit('addRegisteringParty')
    }

    return {
      goToAddSecuredParty,
      addRegisteringParty,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
