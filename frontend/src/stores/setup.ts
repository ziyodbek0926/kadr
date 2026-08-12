import { defineStore } from 'pinia'
import { getSetupStatus } from '@/api/setup'

export const useSetupStore = defineStore('setup', {
  state: () => ({
    needsSetup: null as boolean | null,
  }),
  actions: {
    async checkStatus(): Promise<boolean> {
      const { needs_setup } = await getSetupStatus()
      this.needsSetup = needs_setup
      return needs_setup
    },
  },
})
