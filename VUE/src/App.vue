<template>

  <div class="hello">    
      <Button  @click="drawer_up_val = true" shape="circle" type="primary">更新</Button>
      <Button  @click="drawer_fav_val = true" shape="circle" type="primary">收藏</Button>
      <Button  @click="drawer_sea_val = true" shape="circle" type="primary">搜索</Button>

      <Drawer title="更新" placement="right" :width="drawer_width" :scrollable="true"  v-model="drawer_up_val">
        <LastF/>
      </Drawer>
      <Drawer title="收藏" placement="right" :width="drawer_width" :scrollable="true"  v-model="drawer_fav_val">
        <ListF/>
      </Drawer>
      <Drawer title="搜索" placement="right" :width="drawer_width" :scrollable="true"  v-model="drawer_sea_val">
        <SearchF/>
      </Drawer>
      <MyDrawer/>
  </div>
 
</template>

<script>

import ListF from "./components/ListF.vue"
import LastF from "./components/LastF.vue"
import SearchF from "./components/SearchF.vue"
import MyDrawer from "./components/MyDrawer.vue"


export default {
  name: 'App',
  
  computed: {

  },

  data () {
    return {
      drawer_width : 600,
      drawer_fav_val:false,
      drawer_up_val:false,
      drawer_sea_val:false,
    }
  },

  methods: {
    _isMobile() {
      let flag = navigator.userAgent.match(/(phone|pad|pod|iPhone|iPod|ios|iPad|Android|Mobile|BlackBerry|IEMobile|MQQBrowser|JUC|Fennec|wOSBrowser|BrowserNG|WebOS|Symbian|Windows Phone)/i)
      if(flag){
        this.$store.commit('get_is_mobile',true)
        this.drawer_width = 415
      }
    },
  },

  created: function () {
    this._isMobile()
  },

  components: {
    ListF,
    LastF,
    SearchF,
    MyDrawer,
  },

}


</script>

<style>

  .hello{
    border-radius: 20px;
    width: 250px;
    height: 100px;
    margin: auto;
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
  }


</style>