<template>
  <v-container class="pa-0">
    <v-card
      id="general-collateral"
      :class="{ 'invalid-message': showErrorComponent }"
      flat
    >
      <v-row no-gutters class="py-6">
        <v-col cols="3" class="generic-label pa-4">
          General Collateral
        </v-col>
        <v-col cols="9" class="pr-6">
          <WysiwygEditor
            v-if="isTiptapEnabled"
            placeHolderText="Description of General Collateral"
            :editorContent="newDesc"
            @emitEditorContent="newDesc = $event"
          />

          <tiptap-vuetify
            v-else
            :extensions="extensions"
            v-model="newDesc"
            id="general-collateral-new-desc"
            placeholder="Description of General Collateral"
            :card-props="{
              flat: true,
              style: 'background: rgba(0, 0, 0, 0.06)',
            }"
            :editor-properties="{ editorProps: editorProperties }"
          />
          <p class="summary-text mt-8">
            Note: If you are pasting text,
            <strong>we recommend pasting plain text</strong>
            to avoid formatting and font issues with PDF and printed
            registrations. If you have pasted text other than plain text, verify
            that your documents are correct. If they are not correct, they will
            need to be amended.
          </p>
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
  watch,
  onMounted,
  computed
} from 'vue-demi'
import { useStore } from '@/store/store'
// local
import { RegistrationFlowType } from '@/enums' // eslint-disable-line no-unused-vars
import { GeneralCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars
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
import { storeToRefs } from 'pinia'

import { WysiwygEditor } from '@/components/common'

export default defineComponent({
  name: 'GenColEdit',
  components: {
    TiptapVuetify,
    WysiwygEditor
  },
  props: {
    showInvalid: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const { setGeneralCollateral } = useStore()
    const { getGeneralCollateral, getRegistrationFlowType, isTiptapEnabled } = storeToRefs(useStore())
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

    const editorProperties = {
      transformPastedText (text) {
        return text.replaceAll(/[\u200B-\u200D\uFEFF\u200E\u200F]|(?:&#x200E;)/g, '') // eslint-disable-line
      },
      transformPastedHTML (html) {
        return html.replaceAll(/[\u200B-\u200D\uFEFF\u200E\u200F]|(?:&#x200E;)/g, '') // eslint-disable-line
      }
    }

    const localState = reactive({
      newDesc: getGeneralCollateral.value[0]?.description || '',
      generalCollateral: computed((): GeneralCollateralIF[] => {
        return (getGeneralCollateral.value as GeneralCollateralIF[]) || []
      }),
      showErrorComponent: computed((): boolean => {
        return props.showInvalid
      })
    })

    onMounted(() => {
      if (getRegistrationFlowType.value === RegistrationFlowType.NEW) {
        if (localState.generalCollateral.length > 0) {
          localState.newDesc = localState.generalCollateral[0].description
        }
      }
    })

    watch(
      () => localState.newDesc,
      (val: string) => {
        if (getRegistrationFlowType.value === RegistrationFlowType.NEW) {
          if (val) {
            setGeneralCollateral([{ description: val }])
          } else {
            setGeneralCollateral([])
          }
        }
      }
    )

    watch(
      () => localState.generalCollateral,
      (val: GeneralCollateralIF[]) => {
        if (getRegistrationFlowType.value === RegistrationFlowType.NEW) {
          if (val.length > 0 && val[0].description !== localState.newDesc) {
            localState.newDesc = val[0].description
          }
        }
      }
    )

    return {
      isTiptapEnabled,
      extensions,
      editorProperties,
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
</style>
