import { DOMWrapper, config } from '@vue/test-utils'

export const dataTestId = (wrapper) => {
  function findByTestId(selector) {
    const dataSelector = `[data-test-id='${selector}']`
    const element = wrapper.element.querySelector(dataSelector)
    return new DOMWrapper(element)
  }

  function findInputByTestId(selector) {
    const dataSelector = `[data-test-id='${selector}']`
    const element = wrapper.element.querySelector(dataSelector)
    return new DOMWrapper(element).find('input')
  }

  return {
    findByTestId,
    findInputByTestId
  }
}

config.plugins.VueWrapper.install(dataTestId)
