// index.js
// const app = getApp()
const { envList } = require('../../envList.js');
const utils = require("../../utils/utils.js");

Page({
  data: {
    showUploadTip: false,
    envList,
    time: "08:00",
    selectedEnv: envList[0],
    haveCreateCollection: false,
    inputtedTicker: "",
    possibilities: [],
  },

  onLaunch() {
    console.log("bozo");
  },

  bindTimeChange(e) {
    this.setData({
      time: e.detail.value
    })
  },

  handleInputChange(e) {
    this.setData({
      inputtedTicker: e.detail.value
    })
  },

  handleSearch(e) {
    var self = this;
    let ticker = self.data.inputtedTicker;
    let appid = "prod-2g8rsja1342f2517";
    wx.cloud.callContainer({
      config: {
        env: appid,
      },
      path: '/list',
      header: {
        "X-WX-SERVICE": 'flask-o99h', // xxx中填入服务名称（微信云托管 - 服务管理 - 服务列表 - 服务名称）
        "Content-Type": 'application/json'
      },
      method: 'POST',
      data: {
        ticker
      },
      success: (response) => {
        let status = response.data.status;
        let result = response.data.result;
        if (status == "many_possibilities") {
          this.setData({
            possibilities: result
          });
        } else if (status == "success") {
          // NOTE TO SELF: add in "success" status in next commit.
          // currently is undefined so catching in else
          result.forEach((item) => {
            item.from = utils.categorizeUrl(item.link);
          });
          let data = JSON.stringify(result);
          let url = '/pages/articleList/index?data=' + data;
          wx.navigateTo({
            url: url
          });
        }
        console.log(`Get post list from ${ticker}`);
        console.log(response);
      }
    });
  },

  handleSelect(e) {
    let ticker = e.currentTarget.dataset.arg
    this.setData({
      inputtedTicker: ticker
    })
    this.handleSearch(e)
  }
});