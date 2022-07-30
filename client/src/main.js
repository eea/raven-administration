import { createApp } from 'vue'
import App from './App.vue'
import router from "./router"
import "@unocss/reset/tailwind.css"
import "uno.css"
import { registerElements } from './components/n-elements'

const app = createApp(App);
app.use(router);
registerElements(app);

app.mount('#app')
