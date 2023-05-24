<template>
  <v-card flat rounded id="add-edit-home-sections-form" class="mt-2 mb-5 pa-7">
    <v-form ref="addEditHomeSectionsForm" v-model="addEditValid">
      <v-row no-gutters>
        <v-col cols="12" sm="2">
          <label class="generic-label">{{ isNewHomeSection ? 'Add' : 'Edit' }} Section</label>
        </v-col>
        <v-col cols="12" sm="10" class="pl-2">
          <!-- Add Edit Form -->
          <label class="generic-label">Serial Number</label>
          <v-text-field
            filled
            id="serial-number"
            class="pt-4"
            label="Serial Number"
            v-model="serialNumber"
            :rules="serialNumberRules"
            persistent-hint
          />

          <label class="generic-label">Length</label>
          <v-row no-gutters class="pt-4">
            <v-col>
              <v-text-field
                filled
                id="length-feet"
                class="numberInput pr-2"
                label="Feet"
                v-model.number="lengthFeet"
                :rules="lengthFeetRules"
                persistent-hint
                @keydown.space.prevent
              />
            </v-col>
            <v-col>
              <v-text-field
                filled
                id="length-inches"
                class="numberInput pl-2"
                label="Inches (Optional)"
                v-model.number="lengthInches"
                :rules="isNumber('Inches', 2, 12)"
                persistent-hint
                @keydown.space.prevent
              />
            </v-col>
          </v-row>

          <label class="generic-label">Width</label>
          <v-row no-gutters class="pt-4">
            <v-col>
              <v-text-field
                filled
                id="width-feet"
                class="numberInput pr-2"
                label="Feet"
                v-model.number="widthFeet"
                :rules="widthFeetRules"
                persistent-hint
                @keydown.space.prevent
              />
            </v-col>
            <v-col>
              <v-text-field
                filled
                id="numberInput width-inches"
                class="pl-2"
                label="Inches (Optional)"
                v-model.number="widthInches"
                :rules="(isNumber('Inches', 2, 12))"
                persistent-hint
                @keydown.space.prevent
              />
            </v-col>
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
                  @click="remove()"
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
import { computed, defineComponent, reactive, toRefs } from 'vue-demi'
/* eslint-disable no-unused-vars */
import { HomeSectionIF } from '@/interfaces'
import { useInputRules } from '@/composables/useInputRules'
/* eslint-disable no-unused-vars */

export default defineComponent({
  name: 'AddEditHomeSections',
  emits: ['close', 'remove', 'submit'],
  props: {
    isNewHomeSection: { type: Boolean, default: true },
    editHomeSection: { type: Object as () => HomeSectionIF, default: () => {} }
  },
  setup (props, context) {
    const {
      customRules,
      invalidSpaces,
      isNumber,
      maxLength,
      required
    } = useInputRules()

    const localState = reactive({
      addEditValid: false,
      serialNumber: props.editHomeSection?.serialNumber || '',
      lengthFeet: props.editHomeSection?.lengthFeet || null,
      lengthInches: props.editHomeSection?.lengthInches || null,
      widthFeet: props.editHomeSection?.widthFeet || null,
      widthInches: props.editHomeSection?.widthInches || null,
      hasSubmit: false,
      serialNumberRules: computed((): Array<Function> => {
        let rules = customRules(maxLength(20))
        // Only validate required on submission
        if (localState.hasSubmit) rules = customRules(...rules, required('Enter a serial number'))
        return rules
      }),
      lengthFeetRules: computed((): Array<Function> => {
        let rules = customRules(isNumber('Feet', 2))
        // Only validate required on submission
        if (localState.hasSubmit) rules = customRules(...rules, required('Enter the length in feet'))
        return rules
      }),
      widthFeetRules: computed((): Array<Function> => {
        let rules = customRules(isNumber('Feet', 2))
        // Only validate required on submission
        if (localState.hasSubmit) rules = customRules(...rules, required('Enter the width in feet'))
        return rules
      })
    })

    const close = (): void => { context.emit('close') }
    const remove = (): void => { context.emit('remove') }
    const submit = async (): Promise<void> => {
      localState.hasSubmit = true
      // @ts-ignore - function exists
      await context.refs.addEditHomeSectionsForm.validate()

      if (localState.addEditValid) {
        context.emit('submit', {
          serialNumber: localState.serialNumber.replace(/\s/g, ''),
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
      remove,
      submit,
      required,
      invalidSpaces,
      isNumber,
      customRules,
      maxLength,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
