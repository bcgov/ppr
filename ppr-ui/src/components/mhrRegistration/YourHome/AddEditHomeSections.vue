<template>
  <v-card
    id="add-edit-home-sections-form"
    flat
    rounded
    class="mt-2 mb-5 pa-7"
    :class="{'border-error-left': validate && isNewHomeSection }"
  >
    <v-form
      ref="addEditHomeSectionsForm"
      v-model="addEditValid"
    >
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
        >
          <label
            class="generic-label"
            :class="{ 'error-text': validate }"
          >
            {{ isNewHomeSection ? 'Add' : 'Edit' }} Section
          </label>
        </v-col>
        <v-col
          cols="12"
          sm="9"
          class="pl-2"
        >
          <!-- Add Edit Form -->
          <label class="generic-label">Serial Number</label>
          <v-text-field
            id="serial-number"
            v-model="serialNumber"
            variant="filled"
            class="pt-4"
            label="Serial Number"
            :rules="serialNumberRules"
            persistent-hint
          />

          <label class="generic-label">Length</label>
          <v-row
            no-gutters
            class="pt-4"
          >
            <v-col>
              <v-text-field
                id="length-feet"
                v-model.number="lengthFeet"
                variant="filled"
                class="numberInput pr-2"
                label="Feet"
                :rules="lengthFeetRules"
                persistent-hint
                @keydown.space.prevent
              />
            </v-col>
            <v-col>
              <v-text-field
                id="length-inches"
                v-model.number="lengthInches"
                variant="filled"
                class="numberInput pl-2"
                label="Inches (Optional)"
                :rules="isNumber('Inches', 2, 12)"
                persistent-hint
                @keydown.space.prevent
              />
            </v-col>
          </v-row>

          <label class="generic-label">Width</label>
          <v-row
            no-gutters
            class="pt-4"
          >
            <v-col>
              <v-text-field
                id="width-feet"
                v-model.number="widthFeet"
                variant="filled"
                class="numberInput pr-2"
                label="Feet"
                :rules="widthFeetRules"
                persistent-hint
                @keydown.space.prevent
              />
            </v-col>
            <v-col>
              <v-text-field
                id="numberInput width-inches"
                v-model.number="widthInches"
                variant="filled"
                class="pl-2"
                label="Inches (Optional)"
                :rules="(isNumber('Inches', 2, 12))"
                persistent-hint
                @keydown.space.prevent
              />
            </v-col>
          </v-row>

          <!-- Action buttons -->
          <v-row no-gutters>
            <v-col>
              <div class="form__row form__btns">
                <v-btn
                  id="remove-btn-party"
                  size="large"
                  variant="outlined"
                  color="error"
                  class="remove-btn"
                  :disabled="isNewHomeSection"
                  @click="remove()"
                >
                  Remove
                </v-btn>

                <span class="float-right">
                  <v-btn
                    id="done-btn-party"
                    size="large"
                    class="mx-2"
                    color="primary"
                    @click="submit()"
                  >
                    Done
                  </v-btn>

                  <v-btn
                    id="cancel-btn-party"
                    size="large"
                    variant="outlined"
                    color="primary"
                    @click="close()"
                  >
                    Cancel
                  </v-btn>
                </span>
              </div>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-form>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, nextTick } from 'vue'
/* eslint-disable no-unused-vars */
import { FormIF, HomeSectionIF } from '@/interfaces'
import { useInputRules } from '@/composables/useInputRules'
/* eslint-disable no-unused-vars */

export default defineComponent({
  name: 'AddEditHomeSections',
  props: {
    isNewHomeSection: { type: Boolean, default: true },
    editHomeSection: { type: Object as () => HomeSectionIF, default: () => {} },
    validate: { type: Boolean, default: false }
  },
  emits: ['close', 'remove', 'submit'],
  setup (props, context) {
    const {
      customRules,
      invalidSpaces,
      isNumber,
      maxLength,
      required
    } = useInputRules()
    const addEditHomeSectionsForm = ref(null) as FormIF

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
      await nextTick()

      addEditHomeSectionsForm.value?.validate()

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
      addEditHomeSectionsForm,
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
