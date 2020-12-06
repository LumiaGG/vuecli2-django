<template>
  <div class="listf">
    <!-- <h1>最近更新</h1> -->
    <Row v-for="n in row_num" :key="n" style="height:100%;">
      <Col v-for="f in f_list.slice((n-1)*col_num,(n-1)*col_num+col_num)" :key="f.id" :span="span">
        <Card :bordered="false"  :padding="Number(4)" style="width:95%;">
            <div style="text-align:center"  >
            <img @click="click_event(f)" :src="f.cover" width=90% >
            <h3 @click="click_event(f)" style="white-space:nowrap;text-overflow:ellipsis;overflow:hidden">{{f.title_yh}}</h3>
            </div>
        </Card>
      </Col>
    </Row>
    <!-- <MyDrawer/> -->
  </div>
</template>
<script>
import {last_fan_api} from '../api/api.js'

export default{
  name : "LastF",
    data () {
    return {
      row_num:2,
      col_num:4,
      span:6,
      f_list:[],
    }
  },

  methods: {
    last_fan(){
      last_fan_api().then(response => {
        this.f_list = response.data.data
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
    },

    is_mobile(){
      this.row_num = 4
      this.col_num = 2
      this.span = 12
    }

  },

  created: function () {
    if(this.$store.state.is_mobile){
      this.is_mobile()
    }
    this.last_fan()
  },

  components: {
  },
}

</script>
