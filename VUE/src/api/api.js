// appfront/src/api/api.js
import Vue from 'vue'
import axios from 'axios'

Vue.prototype.$http = axios
axios.defaults.baseURL = '/api'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.xsrfCookieName = 'csrftoken'


export const list_fav_fan_api = (num) => {return axios.get("http://127.0.0.1:9000/api/listtagf?num="+num+"&tag=Favorite")}
export const last_fan_api = () => {return axios.get("http://127.0.0.1:9000/api/lastupdate")}
export const list_e_api = (sid,url_yh) => {return axios.get("http://127.0.0.1:9000/api/listepisodes?sid="+sid+"&url_yh="+url_yh)}
export const search_api = (txt) => {return axios.get("http://127.0.0.1:9000/api/search?kw="+txt)}
export const get_mp4_url_api = (yid) => {return axios.get("http://127.0.0.1:9000/api/getmp4url?yid="+yid)}
export const add_tag_f_api = (tag,title_yh) => {return axios.get("http://127.0.0.1:9000/api/addtagf?tag="+tag+"&title_yh="+title_yh)}
export const delete_tag_f_api = (tag,title_yh) => {return axios.get("http://127.0.0.1:9000/api/deletetagf?tag="+tag+"&title_yh="+title_yh)}
export const match_api = (title_yh,title,sid) => {return axios.post("http://127.0.0.1:9000/api/match",{"title_yh":title_yh,"title":title,"sid":sid,})}
