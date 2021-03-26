<template>
  <v-row no-gutters justify="end">
    <v-btn v-if="!folioNumber" id='folio-add-btn' :class="$style['folio-btn']" depressed @click="folioEdit = true">
      <v-icon class="ma-0, pl-2" size="22" left>mdi-plus</v-icon>
      <span :class="[$style['folio-btn-txt'], 'ma-0']">Add Folio Number</span>
    </v-btn>
    <span v-else id='folio-display' :class="$style['folio-info']">
      <b :class="$style['folio-header']">Folio Number:</b> {{ folioNumber }}
      <v-btn id='folio-edit-btn' :class="[$style['folio-btn'], 'ml-n2']" icon @click="folioEdit = true">
        <v-icon size="13">mdi-pencil</v-icon>
      </v-btn>
    </span>
    <v-card v-if="folioEdit" id='folio-edit' :class="$style['folio-edit-card']">
      <v-row no-gutters class="pt-2">
        <v-col cols="auto">
          <v-card-text class="py-2 my-0">
            <v-text-field id="folio-edit-txt"
                          class="py-0 my-0"
                          :error-messages="folioEditError"
                          :hint="folioEditHint"
                          label="Add Folio Number"
                          persistent-hint
                          v-model="folioEditNumber"
                          @keydown.enter="updateFolioNumber"/>
          </v-card-text>
        </v-col>
        <v-col cols="auto">
          <v-btn id='folio-close-btn' :class="$style['folio-close-btn']" icon @click="folioEdit = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-col>
      </v-row>
    </v-card>
  </v-row>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'

export default defineComponent({
  props: {
    defaultFolioNumber: {
      type: String,
      default: ''
    }
  },
  setup (props, { emit }) {
    const localState = reactive({
      folioEdit: false,
      folioEditError: '',
      folioEditHint: `${15 - props.defaultFolioNumber?.length}`,
      folioEditNumber: props.defaultFolioNumber,
      folioNumber: props.defaultFolioNumber
    })
    const updateFolioNumber = () => {
      if (localState.folioEditNumber?.length < 16) {
        // update folio number + close edit
        localState.folioNumber = localState.folioEditNumber
        localState.folioEdit = false
      }
    }
    watch(() => localState.folioEditNumber, (val: string) => {
      if (val?.length > 15) localState.folioEditError = '0'
      else {
        localState.folioEditError = ''
        localState.folioEditHint = `${15 - val?.length}`
      }
    })
    watch(() => localState.folioNumber, (val: string) => {
      emit('folio-number', val)
    })

    return {
      ...toRefs(localState),
      updateFolioNumber
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.folio-btn {
  background-color: transparent !important;
  color: $primary-blue !important;
  font-size: 0.825rem !important;
}
.folio-btn::before {
  background-color: transparent !important;
  color: $primary-blue !important;
}
.folio-close-btn {
  background-color: transparent !important;
  color: $primary-blue !important;
  position: absolute;
}
.folio-close-btn::before {
  background-color: transparent !important;
  color: $primary-blue !important;
}
.folio-edit-card {
  width: 15rem;
  position: absolute;
  z-index: 3;
}
.folio-header {
  color: $gray9;
}
.folio-info {
  color: $gray7;
  font-size: 0.875rem;
}
</style>
