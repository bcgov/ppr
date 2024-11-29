/** Common Table Functions. **/
export const useTableFeatures = () => {
  /**
   * Simple date sort function
   * @param array The collection of values to sort
   * @param dateType The date property by which to sort from
   * @param reverse A flag to reverse the search to desc.
   */
  const sortDates = (array: Array<object>, dateType: string, reverse = false): Array<object> => {
    return array.sort((a, b) => {
      const dateA = new Date(a[dateType]) as any
      const dateB = new Date(b[dateType]) as any

      if (reverse) {
        return dateB - dateA // Sort in descending order
      } else {
        return dateA - dateB // Sort in ascending order
      }
    })
  }

  return {
    sortDates
  }
}
