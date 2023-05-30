import { ActionTypes } from '@/enums'// Import ActionTypes from the appropriate file
import { setAmendmentList } from '@/utils' // Import the function to be tested

describe('setAmendmentList', () => {
    it('correctly updates the addList and deleteList arrays', () => {
        // Arrange
        const baseList = [
            { action: ActionTypes.ADDED, partyId: 1 },
            { action: ActionTypes.REMOVED, partyId: 2 },
            { action: ActionTypes.EDITED, partyId: 3 }
        ]
        const addList = []
        const deleteList = []

        setAmendmentList(baseList, addList, deleteList)

        expect(addList).toEqual([
            { action: ActionTypes.ADDED, partyId: 1, amendPartyId: 0 },
            { action: ActionTypes.EDITED, partyId: 3, amendPartyId: 3 }
        ])
        expect(deleteList).toEqual([
            { action: ActionTypes.REMOVED, partyId: 2 },
            { action: ActionTypes.EDITED, partyId: 3 }
        ])
    })
})
