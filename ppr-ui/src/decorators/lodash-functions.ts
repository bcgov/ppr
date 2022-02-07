import { createDecorator } from 'vue-class-component'
import _ from 'lodash'

export const Throttle = (delay: number) =>
  createDecorator((options, key) => {
    if (options.methods && options.methods[key]) {
      const originalMethod = options.methods[key]
      const throttleMethod = _.throttle(originalMethod, delay, { trailing: false })

      options.methods[key] = async function (...args: any) {
        await throttleMethod.apply(this, args)
      }
    }
  })
