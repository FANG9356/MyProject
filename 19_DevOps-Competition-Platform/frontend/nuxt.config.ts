import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },
  ssr: false,
  pages: true, // Enable screen switching system. (Router)

  build: {
    transpile: ['vuetify'],
  },

  modules: [
    '@pinia/nuxt', // Enable Pinia
    '@nuxtjs/tailwindcss',  // Enable tailwind
    (_options, nuxt) => {
      nuxt.hooks.hook('vite:extendConfig', (config) => {
        config.plugins.push(vuetify({ autoImport: true }))
      })
    },
  ],

  vite: {
    vue: {
      template: {
        transformAssetUrls,
      },
    },
  },
})