// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import Vuex from 'vuex'
import App from './App'
import ViewUI from 'view-design';
import 'view-design/dist/styles/iview.css';

Vue.config.productionTip = false
Vue.use(ViewUI)
Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    is_mobile:false,
    update_fav:false,
    update_up:false,
    draw_val : false,
    cur_f:{},

  },
  mutations: {
    get_cur_f (state,payload) {
      state.cur_f = payload
    },
    get_draw_val (state,val) {
      state.draw_val = val
    },
    get_update_fav (state,val){
      state.update_fav = val
    },
    get_is_mobile (state,val){
      state.is_mobile = val
    },
  }
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store:store,
  components: { App },
  template: '<App/>'
})