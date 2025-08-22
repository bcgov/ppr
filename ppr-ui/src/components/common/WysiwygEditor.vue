<template>
  <div id="wysiwyg-editor">
    <!-- Insert Table Dialog -->
    <BaseDialog
      :width="'450px'"
      :set-display="displayTableInput"
      :set-options="insertTableOptions"
      @proceed="handleDialogAction($event)"
    >
      <template #content>
        <v-text-field
          id="insert-rows-input"
          v-model.number="insertTableRows"
          variant="filled"
          color="primary"
          label="Number of Rows"
          :rules="isNumber('Rows', null, 20)"
        />

        <v-text-field
          id="insert-columns-input"
          v-model.number="insertTableCols"
          variant="filled"
          color="primary"
          class="mt-3"
          label="Number of Columns"
          :rules="isNumber('Columns', null,20)"
        />
      </template>
    </BaseDialog>

    <!-- Actions Toolbar -->
    <div
      v-if="editor"
      class="editor-toolbar rounded-top"
    >
      <v-tooltip
        v-for="tool in wysiwygToolkitConfig"
        :key="tool.id"
        location="top"
        content-class="top-tooltip text-center toolbar-tooltip"
        transition="fade-transition"
      >
        <template #activator="{ props }">
          <v-btn
            size="50px"
            variant="plain"
            :class="{ 'is-active': isActiveTool(tool) }"
            v-bind="props"
            @click="getToolAction(tool)"
          >
            <v-icon
              size="small"
              class="toolbar-icon"
              :class="tool.isActiveClass === 'heading' ? 'fs-17' : 'fs-21'"
            >
              {{ tool.icon }}
            </v-icon>
          </v-btn>
        </template>
        <div class="pt-2 pb-2">
          {{ tool.tooltipText }}
        </div>
      </v-tooltip>

      <!-- Clear editor content -->
      <v-btn
        variant="plain"
        size="small"
        class="clear-editor-btn float-right mt-2"
        color="primary"
        :ripple="false"
        @click="setEditorContent(null)"
      >
        Clear
        <v-icon
          size="small"
          class="mt-1"
        >
          mdi-close
        </v-icon>
      </v-btn>
    </div>

    <!-- Editor content block -->
    <EditorContent
      class="editor-block ProseMirror"
      :editor="editor"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch, onMounted, computed } from 'vue'
import type { DialogOptionsIF, WysiwygToolsIF } from '@/interfaces'
import { useInputRules } from '@/composables'

// External editor package and extensions
import { Editor, EditorContent } from '@tiptap/vue-3'
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
  components: {
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
  emits: ['emitEditorContent'],
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
        enableInputRules: false,
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

    /** Returns true if the current tool is active on the selected content **/
    const isActiveTool = (tool: WysiwygToolsIF) => {
      return tool.isActiveClass === 'heading'
        ? localState.editor?.isActive(tool.isActiveClass, { level: tool.hLevel })
        : localState.editor?.isActive(tool.isActiveClass)
    }

    /** Returns the toolkit formatting function **/
    const getToolAction = (tool: WysiwygToolsIF) => {
      if (tool.action === 'insertTable') localState.displayTableInput = true
      else return localState.editor?.chain().focus()[tool.action](tool.hLevel ? { level: tool.hLevel } : null).run()
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
      isActiveTool,
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
  width: 120px!important;
}
.toolbar-icon {
  color: $gray7!important;
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
