
import { getVuexStore } from '@/store'


describe('Should properly mutate the state', () => { 

    it('mutate role SBC', () => {
        const store = getVuexStore()
        const authorization = store.state.stateModel.authorization
        store.commit('mutateAuthRoles', ['staff', 'ppr'])
        
        // Add SBC role
        store.commit('mutateRoleSbc', true)
        expect(authorization.authRoles.includes('sbc')).toBe(true)
        expect(authorization.authRoles.length).toBe(3)

        // Add duplicate SBC role
        store.commit('mutateRoleSbc', true)
        expect(authorization.authRoles.includes('sbc')).toBe(true)
        expect(authorization.authRoles.length).toBe(3)

        // Remove SBC role
        store.commit('mutateRoleSbc', false)
        expect(authorization.authRoles.includes('sbc')).toBe(false)
        expect(authorization.authRoles.length).toBe(2)

        expect(authorization.authRoles.includes('sbc')).toBe(false)
        expect(authorization.authRoles.length).toBe(2)

        // Add SBC role one more time
        store.commit('mutateRoleSbc', true)
        expect(authorization.authRoles.includes('sbc')).toBe(true)
        expect(authorization.authRoles.includes('staff')).toBe(true)
        expect(authorization.authRoles.includes('ppr')).toBe(true)
        expect(authorization.authRoles.length).toBe(3)
    })
 })