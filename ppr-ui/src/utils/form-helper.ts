export function focusOnFirstError(formName: string): void {
  setTimeout(() => {
    const firstErrorField = document
      .getElementById(formName)
      .getElementsByClassName('v-input--error')
      .item(0)
      .getElementsByTagName('input')
      .item(0) as HTMLElement | null

    firstErrorField.focus()
  }, 50)
}

// Scroll to first designated error on Information or Review page
export async function scrollToFirstErrorComponent(defaultIndex: number = 0): Promise<void> {
  setTimeout(() => {
    document?.getElementsByClassName('border-error-left').length > 0 &&
    document?.getElementsByClassName('border-error-left')[defaultIndex]
      .scrollIntoView({ block: 'start', inline: 'nearest', behavior: 'smooth' })
  }, 500)
}

/**
 * Scroll to first visible instance of designated error class.
 * Useful for multiple instances of error class across different views.
 **/
export async function scrollToFirstVisibleErrorComponent(): Promise<void> {
  const errorElements = document.getElementsByClassName('border-error-left')
  for (const [index, element] of Array.from(errorElements).entries()) {
    if (isElementInViewport(element)) {
      await scrollToFirstErrorComponent(index)
      return
    }
  }
}

/** Returns true when the element is within the current viewport **/
function isElementInViewport(el: any): boolean {
  const rect = el.getBoundingClientRect()
  return (rect.top !== 0 && rect.left !== 0 && rect.bottom !== 0 && rect.right !== 0)
}
