import { createApp } from 'vue'
import App from './App.vue'
import "./assets/tailwind.css";
import "./assets/n-elements.css";

// INTERCEPT
import intercetor from "./helpers/interceptor";
intercetor.request();
intercetor.response();
intercetor.default();

const app = createApp(App); 

// ROUTER
import router from "./router"
app.use(router);

app.mount('#app')