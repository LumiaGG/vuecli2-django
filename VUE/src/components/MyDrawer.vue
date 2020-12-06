<template >
    <div>
    <Drawer title="Basic Drawer" :width="drawer_width" :inner="true"  :scrollable="true" v-model="draw_val" @on-close="close_draw">
    <ButtonGroup slot="header">
      <Button  @click="close_draw"  type="primary">关闭</Button>
      <Button  id="fav_button" @click="set_fav"  type="primary">收藏</Button>
      <Button  @click="list_s(cur_f.title_yh)" type="primary">刷新匹配番剧</Button>
      <Button :loading="list_loading" shape="circle" type="primary"></Button>
    </ButtonGroup>
    
    <Collapse simple>
        <Panel name="剧集">
            {{cur_f.title_yh}}
            <div slot="content" class="liste" style="margin:0.25in;" >
              <Row v-for="n in Math.ceil(e_list.length/8)" :key="n" style="height:40px;" >
                <Col v-for="e in e_list.slice((n-1)*8,(n-1)*8+8)" :key="e.id" span=3 >
                  <!-- <Button type="text" @click="palay_f(e)"  > {{e.title.slice(0,3)}} </Button>
                   -->
                   <Poptip trigger="hover" :content="e.long_title!=''?e.long_title:e.title">
                    <Button type="text" @click="palay_f(e)"  > {{e.title.slice(0,3)}} </Button>
                  </Poptip>
                </Col>
              </Row>
            </div>
        </Panel>
        <Panel name="匹配">
            匹配番剧
            <div slot="content" class="liste" style="margin:0.25in;" >
              <List>
                <Input search v-model="search_val" @on-search="list_s(search_val)" enter-button="Search" placeholder="Enter something..." />
                <ListItem  v-for="s in s_list">
                <ListItemMeta :title="s.title" :description="'SID:'+String(s.sid)" />
                <Button  @click="match(s)"  type="primary">匹配</Button>
                </ListItem>
              </List>
            </div>
        </Panel>
    </Collapse>
    </Drawer>

    <Drawer title="播放" :width="this.$store.state.is_mobile?drawer_width:800"  :inner="true"  :scrollable="true" v-model="play_draw_val" @on-close="close_draw_frame">
      <ButtonGroup slot="header">
      <Button  @click="close_play_draw"  type="primary">后台播放</Button>
      <Button  @click="reload_frame" :disabled='!url_got' type="primary">重载播放器</Button>
      <Button  @click="reload_comment" :disabled='!url_got' type="primary">重载弹幕</Button>
      <Button :loading="!url_got" shape="circle" type="primary"></Button>
    </ButtonGroup>
    <div class="demo-spin-col" v-if="!url_got">
            <Spin fix>
                <Icon type="ios-loading" size=18 class="demo-spin-icon-load"></Icon>
                <div>Loading</div>
            </Spin>
    </div>
    <h3>视频链接</h3>
    <p id="set_url" hidden="hidden" >{{mp4_url}}</p>
    <p id="set_cid" hidden="hidden" >{{cid}}</p>
    <Input v-model="mp4_url" />
    <br/>
    <br/>
    
    <div>
      <p v-show="is_m3u8">M3U8格式的视频暂时无法播放</p>
    <iframe v-if="play_f_frame" id="iframe" name="iframe"  src="../static/player.html" width=100% height=500px  scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true">></iframe>
    </div>
    </Drawer>

    </div>

</template>
<script>
import {list_e_api,search_api,get_mp4_url_api,add_tag_f_api,delete_tag_f_api,match_api} from '../api/api.js'

window.get_frame_state = function(){
      let ifrmae = parent.frames["iframe"]
      let url = document.getElementById('set_url').innerText
      let cid = document.getElementById('set_cid').innerText
      iframe.init_and_set(url,cid)
    }

export default{
  name : "MyDraw",
  data () {
    return {
      drawer_width : 600,
      play_f_frame:false,
      play_draw_val : false,
      list_loading : false,
      list_s_loading : false,
      search_val : '',
      draw_val:false,
      cur_f:{},
      e_list : [],
      s_list:[],
      mp4_url:"",
      cid : "",
      is_m3u8:false,
      url_got:false,
      add_tag_state:0,
      match_state:0,
      is_fav : false,
    }
  },

  computed: {
    get_cur_f(){
      return this.$store.state.cur_f
    },
    get_draw_val(){
      return this.$store.state.draw_val
    }
  },

  watch: {
    get_cur_f(newVal,oldVal){
      this.cur_f = this.$store.state.cur_f
      if(this.cur_f.tags.indexOf(1) != -1){
        this.is_fav = true
        document.getElementById('fav_button').innerText = "取消收藏"
      }
      else{
        document.getElementById('fav_button').innerText = "收藏"
        this.is_fav = false
      }
      this.list_e()
    },
    get_draw_val(newVal,oldVal){
      this.draw_val = this.$store.state.draw_val
    },
  },

  methods: {
    close_draw(){
      this.$store.commit('get_draw_val',false)
    },
    close_play_draw(){
      this.play_draw_val = false
    },
    close_draw_frame(){
      this.play_drawer_val = false
      this.play_f_frame = false
    },

    list_e(){
      this.list_loading = true
      list_e_api(this.cur_f.sid,this.cur_f.url_yh).then(response => {
        this.e_list = response.data
      this.list_loading = false
      })
    },

    list_s(txt){
      this.list_loading = true
      this.search_val = txt
      search_api(txt).then(response => {
        this.s_list = response.data.data_bili
        this.list_loading = false
        if (this.s_list.length === 0){
          this.s_list = [{"title":"很遗憾,什么也没找到,试试更换关键词吧","sid":"很遗憾,什么也没找到,试试更换关键词吧"}]
        }
      })
    },

    get_mp4_url(url_yh){
        let split_list = url_yh.split("/")
        let yid = split_list[split_list.length-1].replace(".html","")
        get_mp4_url_api(yid).then(response => {
          this.mp4_url = response.data.mp4_url
          if(this.mp4_url.search("m3u8") != -1){
            this.is_m3u8 = true
            this.url_got = true
          }
          else
          {
            this.is_m3u8 = false
            this.url_got = true
            this.play_f_frame = true 
          }
        })
         
    },

    palay_f(e){
        this.url_got = false
        this.play_draw_val=true
        this.cid = e.cid
        this.get_mp4_url(e.url)
    },

    reload_frame(){
      iframe.init_and_set(this.mp4_url)
    },

    reload_comment(){
      iframe.load_commment(this.cid)
    },

    update_fav(){
      this.$store.commit("get_update_fav",true)
    },

    set_fav(){
      if(this.is_fav)
      {
        delete_tag_f_api('Favorite',this.cur_f.title_yh).then(response => {
          if(response.data.success === true){
            document.getElementById('fav_button').innerText = "收藏"
            this.is_fav = false
            this.add_tag_state -= 1
            this.update_fav()
          }
        })
      }
      else
      {
        add_tag_f_api('Favorite',this.cur_f.title_yh).then(response => {
          if(response.data.success === true){
            document.getElementById('fav_button').innerText = "取消收藏"
            this.is_fav = true
            this.add_tag_state += 1
            this.update_fav()
          }
        })
      }
      
    },

    match(s){
      match_api(this.cur_f.title_yh,s.title,s.sid).then(response => {
        if (response.data.success === true){
          this.match_state += 1
          this.cur_f.sid = s.sid
          this.list_e()
          }
        })
    },

    is_mobile(){
      this.drawer_width = 415
    },
  },

  created: function () {
      if(this.$store.state.is_mobile){
      this.is_mobile()
    }
  },

  components: {
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
