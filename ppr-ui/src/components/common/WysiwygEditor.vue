<template>
  <div id="wysiwyg-editor">
    <!-- Insert Table Dialog -->
    <base-dialog
      :width="'450px'"
      :setDisplay="displayTableInput"
      :setOptions="insertTableOptions"
      @proceed="handleDialogAction($event)"
    >
      <template v-slot:content>
        <v-text-field
          filled
          id="insert-rows-input"
          label="Number of Rows"
          v-model.number="insertTableRows"
          :rules="isNumber('Rows', null, 20)"
        />

        <v-text-field
          filled
          id="insert-columns-input"
          class="mt-3"
          label="Number of Columns"
          v-model.number="insertTableCols"
          :rules="isNumber('Columns', null,20)"
        />
      </template>
    </base-dialog>

    <!-- Actions Toolbar -->
    <div v-if="editor" class="editor-toolbar rounded-top">
      <v-tooltip
        v-for="tool in wysiwygToolkitConfig"
        :key="tool.id"
        top content-class="top-tooltip text-center toolbar-tooltip"
        transition="fade-transition"
      >
        <template v-slot:activator="{ on }">
          <v-btn
            v-on="on" text
            :class="{ 'is-active': editor.isActive(tool.isActiveClass) }"
            @click="getToolAction(editor, tool)"
          >
            <v-icon small>{{ tool.icon }}</v-icon>
          </v-btn>
        </template>
        <div class="pt-2 pb-2">
          {{ tool.tooltipText }}
        </div>
      </v-tooltip>

      <!-- Clear editor content -->
      <v-btn
        text small
        class="clear-editor-btn float-right mt-2"
        color="primary"
        :ripple="false"
        @click="setEditorContent(null)"
      >
        Clear
        <v-icon small class="mt-1">mdi-close</v-icon>
      </v-btn>
    </div>

    <!-- Editor content block -->
    <editor-content class="editor-block ProseMirror" :editor="editor" />
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch, onMounted, computed } from 'vue-demi'
import BaseDialog from '@/components/dialogs/BaseDialog.vue'
import { DialogOptionsIF } from '@/interfaces'
import { useInputRules } from '@/composables'

// External editor package and extensions
import { Editor, EditorContent } from '@tiptap/vue-2'
import StarterKit from '@tiptap/starter-kit'
import Table from '@tiptap/extension-table'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import TableRow from '@tiptap/extension-table-row'
import { Underline } from '@tiptap/extension-underline'
import { Placeholder } from '@tiptap/extension-placeholder'

// local header toolkit configurations
import { wysiwygToolkitConfig } from '@/resources'

export default defineComponent({
  name: 'WysiwygEditor',
  emits: ['emitEditorContent'],
  components: {
    BaseDialog,
    EditorContent
  },
  props: {
    editorContent: {
      type: String,
      default: null
    },
    placeHolderText: {
      type: String,
      default: ''
    }
  },
  setup (props, { emit }) {
    const { isNumber } = useInputRules()
    const localState = reactive({
      editor: null, // configurable editor instance
      displayTableInput: false,
      insertTableRows: null,
      insertTableCols: null,
      wysiwygEditorContent: computed((): string => {
        return localState.editor?.getHTML() || null
      })
    })

    /** Initialize the editor instance on mount **/
    onMounted(() => {
      localState.editor = new Editor({
        content: props.editorContent || null,
        editorProps: editorProperties,
        extensions: [
          Underline,
          Table,
          TableRow,
          TableHeader,
          TableCell,
          StarterKit.configure(),
          Placeholder.configure({
            placeholder: props.placeHolderText
          })
        ]
      })
    })

    /** Set the content of the editor block */
    const setEditorContent = (val: string) => {
      localState.editor.commands.setContent(val)
    }

    /** Returns the toolkit formatting function **/
    const getToolAction = (editor, tool) => {
      if (tool.action === 'insertTable') localState.displayTableInput = true
      else return editor.chain().focus()[tool.action](tool.hLevel ? { level: tool.hLevel } : null).run()
    }

    /** Handle user input from dialog actions **/
    const handleDialogAction = (val) => {
      if (val) {
        localState.editor.chain().focus().insertTable({
          rows: localState.insertTableRows,
          cols: localState.insertTableCols,
          withHeaderRow: false
        }).run()
      }
      localState.displayTableInput = false
    }

    /** Local configurations **/
    const insertTableOptions: DialogOptionsIF = {
      acceptText: 'Insert Table',
      cancelText: 'Cancel',
      text: '',
      title: 'Insert Table'
    }

    const editorProperties = {
      transformPastedText (text) {
        return text.replaceAll(/[\u200B-\u200D\uFEFF\u200E\u200F]|(?:&#x200E;)/g, '')
      },
      transformPastedHTML (html) {
        return html.replaceAll(/[\u200B-\u200D\uFEFF\u200E\u200F]|(?:&#x200E;)/g, '')
      }
    }

    /** Emit the editor content as it updates **/
    watch(() => localState.wysiwygEditorContent, (val: string) => {
      // Omit setting blank <p> tag to store
      emit('emitEditorContent', val !== '<p></p>' ? val : null)
    })

    return {
      StarterKit,
      isNumber,
      getToolAction,
      setEditorContent,
      handleDialogAction,
      insertTableOptions,
      wysiwygToolkitConfig,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#wysiwyg-editor {
  width: 100%;
  overflow: hidden;
}
.editor-toolbar {
  background-color: #f5f5f5!important;
}
.is-active {
  background-color: $gray3!important;
}
.toolbar-tooltip {
  width: 120px !important;
}
.editor-block {
  width: 100%;
  height: 450px;
  overflow: auto;
  padding-right: 0; /* Remove any padding that may affect scrollbar visibility */
  box-sizing: border-box; /* Adjust the box-sizing to include the padding in the width */
  background-color: rgba(0, 0, 0, 0.06);
}
</style>
