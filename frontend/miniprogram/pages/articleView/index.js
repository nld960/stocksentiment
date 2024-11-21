// pages/articleView/index.js
const utils = require("../../utils/utils.js");

Page({

  /**
   * Page initial data
   */
  data: {
    url: "",
    content: "",
    author: "",
    time: "",
    from: "",
  },

  /**
   * Lifecycle function--Called when page load
   */
  onLoad(options) {
    const url = options.url;
    const author = options.author;
    const time = options.time;
    const from = options.from;
    this.setData({
      author: author,
      time: time,
      from: from,
    });
    this.getContent(url);
  },

  getContent(url) {
    let appid = "prod-2g8rsja1342f2517";
    var self = this;
    self.setData({
      content: "努力加载中..."
    });
    wx.cloud.callContainer({
      config: {
        env: appid,
      },
      path: '/getpost',
      header: {
        "X-WX-SERVICE": 'flask-o99h', // xxx中填入服务名称（微信云托管 - 服务管理 - 服务列表 - 服务名称）
        "Content-Type": 'application/json'
      },
      method: 'POST',
      data: {
        url: url
      },
      success: (response) => {
        self.setData({
          content: response.data.content,
        });
        console.log(`Get post content from ${url}`);
        console.log(response);
      },
      fail: (response) => {
        console.log(`Get post content from ${url} (Failed)`);
        console.log(response);
      }
    });
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
  },

  handleInputChange(e) {
    this.setData({
      inputtedTicker: e.detail.value
    })
  },

  /**
   * Lifecycle function--Called when page is initially rendered
   */
  onReady() {

  },

  /**
   * Lifecycle function--Called when page show
   */
  onShow() {

  },

  /**
   * Lifecycle function--Called when page hide
   */
  onHide() {

  },

  /**
   * Lifecycle function--Called when page unload
   */
  onUnload() {

  },

  /**
   * Page event handler function--Called when user drop down
   */
  onPullDownRefresh() {

  },

  /**
   * Called when page reach bottom
   */
  onReachBottom() {

  },

  /**
   * Called when user click on the top right corner to share
   */
  onShareAppMessage() {

  }
})