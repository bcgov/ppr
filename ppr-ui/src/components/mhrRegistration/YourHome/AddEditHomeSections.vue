<template>
  <v-card flat rounded id="add-edit-home-sections-form" class="mt-8 pa-8">
    <v-form ref="addEditHomeSectionsForm" v-model="addEditValid">
      <v-row no-gutters>
        <v-col cols="12" sm="2">
          <label class="generic-label">Add Section</label>
        </v-col>
        <v-col cols="12" sm="10">
          <!-- Add Edit Form -->
          <label class="generic-label">Serial Number</label>
          <v-text-field
            filled
            id="serial-number"
            class="pt-4"
            label="Serial Number"
            v-model="serialNumber"
            :rules="hasSubmit ? requiredStringRules('serial number') : []"
            persistent-hint
          />

          <label class="generic-label">Length</label>
          <v-row no-gutters class="pt-4">
            <v-text-field
              filled
              id="length-feet"
              class="numberInput pr-2"
              label="Feet"
              v-model.number="lengthFeet"
              :rules="hasSubmit ? requiredNumberRules('foot length') : []"
              persistent-hint
            />
            <v-text-field
              filled
              id="length-inches"
              class="numberInput pl-2"
              label="Inches (Optional)"
              v-model.number="lengthInches"
              :rules="hasSubmit ? optionalNumberRules() : []"
              persistent-hint
            />
          </v-row>

          <label class="generic-label">Width</label>
          <v-row no-gutters class="pt-4">
            <v-text-field
              filled
              id="width-feet"
              class="numberInput pr-2"
              label="Feet"
              v-model.number="widthFeet"
              :rules="hasSubmit ? requiredNumberRules('foot width') : []"
              persistent-hint
            />
            <v-text-field
              filled
              id="numberInput width-inches"
              class="pl-2"
              label="Inches (Optional)"
              v-model.number="widthInches"
              :rules="hasSubmit ? optionalNumberRules() : []"
              persistent-hint
            />
          </v-row>

          <!-- Action buttons -->
          <v-row>
            <v-col>
              <div class="form__row form__btns">
                <v-btn
                  large
                  outlined
                  color="error"
                  id="remove-btn-party"
                  class="remove-btn"
                  :disabled="isNewHomeSection"
                >
                  Remove
                </v-btn>

                <v-btn
                  large
                  id="done-btn-party"
                  class="ml-auto"
                  color="primary"
                  @click="submit()"
                >
                  Done
                </v-btn>

                <v-btn
                  id="cancel-btn-party"
                  large
                  outlined
                  color="primary"
                  @click="close()"
                >
                  Cancel
                </v-btn>
              </div>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-form>
  </v-card>
</template>

<script lang="ts">
/* eslint-disable no-unused-vars */
import Vue from 'vue'
import { computed, defineComponent, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { FormIF, HomeSectionIF } from '@/interfaces'
import { useInputRules } from '@/composables/useInputRules'
/* eslint-disable no-unused-vars */

export default defineComponent({
  name: 'AddEditHomeSections',
  props: {
    isNewHomeSection: { type: Boolean, default: true }
  },
  setup (props, context) {
    const {
      requiredStringRules,
      optionalNumberRules,
      requiredNumberRules
    } = useInputRules()

    const localState = reactive({
      addEditValid: false,
      serialNumber: '',
      lengthFeet: null,
      lengthInches: null,
      widthFeet: null,
      widthInches: null,
      hasSubmit: false
    })

    const close = (): void => { context.emit('close') }
    const submit = async (): Promise<void> => {
      // Set submission flag to apply validation rules
      localState.hasSubmit = true
      // @ts-ignore - function exists
      await context.refs.addEditHomeSectionsForm.validate()

      if (localState.addEditValid) {
        context.emit('submit', {
          serialNumber: localState.serialNumber,
          lengthFeet: localState.lengthFeet,
          lengthInches: localState.lengthInches,
          widthFeet: localState.widthFeet,
          widthInches: localState.widthInches
        })
        close()
      }
    }

    return {
      close,
      submit,
      requiredStringRules,
      optionalNumberRules,
      requiredNumberRules,
      ...toRefs(localState)
    }
  }
})
/* eslint-enable no-unused-vars */
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
