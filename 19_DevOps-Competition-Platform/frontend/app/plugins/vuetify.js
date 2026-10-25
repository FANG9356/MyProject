import { createVuetify } from 'vuetify'

import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

export default defineNuxtPlugin((nuxtApp) => {
  const vuetify = createVuetify({
    icons: {
      defaultSet: 'mdi',
    },
  })
  nuxtApp.vueApp.use(vuetify)
})
