<template>
  <v-container class="pa-0" :class="{ 'border-error-left': showErrorBar }">
    <v-card
      id="general-collateral-amendment"
      :class="cardClass"
      flat
    >
      <v-row no-gutters class="py-4">
        <v-col class="generic-label">
          General Collateral
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col class="summary-text"
          >Indicate the General Collateral to be deleted from or added to this
          registration.
          <p class="pt-2 mb-0 mr-2">
            Note: If you are pasting text, <strong>we recommend pasting plain text</strong> to avoid formatting and font
            issues with PDF and printed registrations. If you have pasted text other than plain text, verify that your
            documents are correct. If they are not correct, they will need to be amended.
          </p>
        </v-col>
      </v-row>
      <v-row no-gutters class="pt-8">
        <v-col class="generic-label">
          General Collateral to be Deleted
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col class="pr-4">
          <tiptap-vuetify
            :extensions="extensions"
            v-model="delDesc"
            id="general-collateral-delete-desc"
            placeholder="Enter the General Collateral to be deleted from this registration"
            :card-props="{ flat: true, style: 'min-height: 350px; background: rgba(0, 0, 0, 0.06)' }"
            :editor-properties="{ editorProps: editorProperties }"
          />
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col class="generic-label">
          General Collateral to be Added
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col class="pr-4">
          <tiptap-vuetify
            :extensions="extensions"
            v-model="addDesc"
            id="general-collateral-add-desc"
            placeholder="Enter the General Collateral to be added to this registration"
            :card-props="{ flat: true, style: 'min-height: 350px; background: rgba(0, 0, 0, 0.06)' }"
            :editor-properties="{ editorProps: editorProperties }"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col class="pr-7">
          <div class="form__row form__btns">
            <v-btn
              large
              id="done-btn-gen-col"
              class="ml-auto"
              color="primary"
              @click="onSubmitForm()"
            >
              Done
            </v-btn>

            <v-btn
              id="cancel-btn-gen-col"
              large
              outlined
              color="primary"
              @click="resetFormAndData()"
            >
              Cancel
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  onMounted,
  computed
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
// import the component and the necessary extensions
import {
  TiptapVuetify,
  Heading,
  Bold,
  Italic,
  Strike,
  Underline,
  BulletList,
  OrderedList,
  ListItem,
  Blockquote,
  HardBreak,
  HorizontalRule,
  History,
  Table,
  TableCell,
  TableHeader,
  TableRow
} from 'tiptap-vuetify'
// local
import { GeneralCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  props: {
    showInvalid: {
      type: Boolean,
      default: false
    },
    setShowErrorBar: {
      type: Boolean,
      default: false
    }
  },
  components: {
    TiptapVuetify
  },
  setup (props, { emit }) {
    const { getGeneralCollateral } = useGetters<any>([
      'getGeneralCollateral'
    ])
    const { setGeneralCollateral } = useActions<any>(['setGeneralCollateral'])
    const extensions = [
      History,
      Blockquote,
      Underline,
      Strike,
      Italic,
      ListItem,
      BulletList,
      OrderedList,
      [
        Heading,
        {
          options: {
            levels: [1, 2, 3]
          }
        }
      ],
      Bold,
      HorizontalRule,
      HardBreak,
      Table,
      TableCell,
      TableHeader,
      TableRow
    ]

    const localState = reactive({
      delDesc: '',
      addDesc: '',
      generalCollateral: computed((): GeneralCollateralIF[] => {
        return (getGeneralCollateral.value as GeneralCollateralIF[]) || []
      }),
      showErrorComponent: computed((): boolean => {
        return props.showInvalid
      }),
      cardClass: computed((): string => {
        if (localState.showErrorComponent) {
          return 'invalid-message'
        }
        if (localState.showErrorBar) {
          return 'border-over'
        }
      }),
      showErrorBar: computed((): boolean => {
        return props.setShowErrorBar
      })
    })

    const onSubmitForm = () => {
      const newGeneralCollateral = localState.generalCollateral

      if (localState.addDesc.replace(/(<([^>]+)>)/ig, '').trim().length === 0) localState.addDesc = ''
      if (localState.delDesc.replace(/(<([^>]+)>)/ig, '').trim().length === 0) localState.delDesc = ''
      const amendedGC = {
        descriptionAdd: localState.addDesc,
        descriptionDelete: localState.delDesc
      }
      if (localState.addDesc || localState.delDesc) {
        if (newGeneralCollateral.length > 0) {
          // if there is no general collateral at the end of the array with a blank date time,
          // we know we are adding
          if (newGeneralCollateral[newGeneralCollateral.length - 1].addedDateTime !== undefined) {
            newGeneralCollateral.push(amendedGC)
          } else {
            // otherwise, pop the old general collateral off the end of the array, and push the new one
            // one (pop and push required to keep refs)
            newGeneralCollateral.pop()
            newGeneralCollateral.push(amendedGC)
          }
        } else {
          newGeneralCollateral.push(amendedGC)
        }
        setGeneralCollateral(newGeneralCollateral)
      }
      emit('closeGenColAmend', true)
    }

    const editorProperties = {
      transformPastedText (text) {
        return text.replaceAll(/[\u200B-\u200D\uFEFF\u200E\u200F]|(?:&#x200E;)/g, '') // eslint-disable-line
      },
      transformPastedHTML (html) {
        return html.replaceAll(/[\u200B-\u200D\uFEFF\u200E\u200F]|(?:&#x200E;)/g, '') // eslint-disable-line
      }
    }

    const resetFormAndData = () => {
      emit('closeGenColAmend', true)
    }

    onMounted(() => {
      const gc = localState.generalCollateral
      if (gc.length > 0) {
        if (gc[gc.length - 1].addedDateTime === undefined) {
          localState.addDesc = gc[gc.length - 1].descriptionAdd
          localState.delDesc = gc[gc.length - 1].descriptionDelete
        }
      }
    })

    return {
      editorProperties,
      extensions,
      onSubmitForm,
      resetFormAndData,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
::v-deep .tiptap-vuetify-editor__content {
  height: 350px; overflow-y: scroll;
}

::v-deep .tiptap-vuetify-editor__content table td {
  white-space: normal;
}
.border-error-left
{
  margin-left: -31px;
}
.border-over
{
  margin-left: 25px;
}
</style>
