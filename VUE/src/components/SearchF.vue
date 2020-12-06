<template >
    <div>
        <Input search v-model="search_val" @on-search="list_s(search_val)" enter-button="Search" placeholder="Enter something..." />
        <div class="demo-spin-col" v-if="list_s_loading">
            <Spin fix>
                <Icon type="ios-loading" size=18 class="demo-spin-icon-load"></Icon>
                <div>Searching</div>
            </Spin>
        </div>
            <List>
              <ListItem  v-for="s in s_list">
              <ListItemMeta :title="s.title_yh" :description="'URL:'+String(s.url_yh)" />
              <Button  @click="click_event(s)"  type="primary">进入</Button>
              </ListItem>
            </List>
        </div>
    </div>

</template>
<script>
import {search_api} from '../api/api.js'

export default{
  name : "SearchF",
  data () {
    return {
      list_s_loading : false,
      search_val : '',
      cur_f:{},
      s_list:[],
    }
  },


  methods: {

    list_s(txt){
      this.list_s_loading = true
      search_api(txt).then(response => {
        this.s_list = response.data.data_yh
        if (this.s_list.length === 0)
          this.s_list = [{"title":"很遗憾,什么也没找到,试试更换关键词吧","sid":"很遗憾,什么也没找到,试试更换关键词吧"}]
        this.list_s_loading = false
      })
      
    },

    open_draw_val(){
      this.$store.commit('get_draw_val',true)
    },

    trans_cur_f(f){
      this.$store.commit("get_cur_f",f)
    },

    click_event(f){
      this.open_draw_val()
      this.trans_cur_f(f)
    }
  },

  created: function () {
    // this.list_e()
  },
}

</script>
<style>
    .demo-spin-icon-load{
        animation: ani-demo-spin 1s linear infinite;
    }
    @keyframes ani-demo-spin {
        from { transform: rotate(0deg);}
        50%  { transform: rotate(180deg);}
        to   { transform: rotate(360deg);}
    }

</style>