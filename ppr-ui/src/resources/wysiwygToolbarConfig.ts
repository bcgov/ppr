import { WysiwygToolsIF } from '@/interfaces'

export const wysiwygToolkitConfig: Array<WysiwygToolsIF> = [
  {
    id: 'editor-undo',
    tooltipText: 'Undo',
    action: 'undo',
    hLevel: null,
    isActiveClass: 'undo',
    icon: 'mdi-undo'
  },
  {
    id: 'editor-redo',
    tooltipText: 'Redo',
    action: 'redo',
    hLevel: null,
    isActiveClass: 'redo',
    icon: 'mdi-redo'
  },
  {
    id: 'editor-bold',
    tooltipText: 'Bold',
    action: 'toggleBold',
    hLevel: null,
    isActiveClass: 'bold',
    icon: 'mdi-format-bold'
  },
  {
    id: 'editor-italic',
    tooltipText: 'Italic',
    action: 'toggleItalic',
    hLevel: null,
    isActiveClass: 'italic',
    icon: 'mdi-format-italic'
  },
  {
    id: 'editor-underline',
    tooltipText: 'Underline',
    action: 'toggleUnderline',
    hLevel: null,
    isActiveClass: 'underline',
    icon: 'mdi-format-underline'
  },
  {
    id: 'editor-bullet-list',
    tooltipText: 'Bulleted List',
    action: 'toggleBulletList',
    hLevel: null,
    isActiveClass: 'bulletList',
    icon: 'mdi-format-list-bulleted'
  },
  {
    id: 'editor-ordered-list',
    tooltipText: 'Numbered List',
    action: 'toggleOrderedList',
    hLevel: null,
    isActiveClass: 'orderedList',
    icon: 'mdi-format-list-numbered'
  },
  {
    id: 'editor-heading-1',
    tooltipText: 'Level 1 Header',
    action: 'toggleHeading',
    hLevel: 1,
    isActiveClass: 'heading1',
    icon: 'mdi-format-header-1'
  },
  {
    id: 'editor-heading-2',
    tooltipText: 'Level 2 Header',
    action: 'toggleHeading',
    hLevel: 2,
    isActiveClass: 'heading2',
    icon: 'mdi-format-header-2'
  },
  {
    id: 'editor-heading-3',
    tooltipText: 'Level 3 Header',
    action: 'toggleHeading',
    hLevel: 3,
    isActiveClass: 'heading3',
    icon: 'mdi-format-header-3'
  },
  {
    id: 'editor-horizontal-rule',
    tooltipText: 'Hairline',
    action: 'setHorizontalRule',
    hLevel: null,
    isActiveClass: 'rule',
    icon: 'mdi-minus'
  },
  {
    id: 'editor-table',
    tooltipText: 'Insert Table',
    action: 'insertTable',
    hLevel: null,
    isActiveClass: 'table',
    icon: 'mdi-table'
  }
]
