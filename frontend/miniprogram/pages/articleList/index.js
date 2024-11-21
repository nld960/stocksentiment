// pages/articleList/index.js
const utils = require("../../utils/utils.js");

Page({
  /**
   * Page initial data
   */
  data: {
    list: [],
    possibilities: []
  },

  /**
   * Lifecycle function--Called when page load
   */
  onLoad(options) {
    const data = JSON.parse(options.data);
    this.setData({
      list: data,
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
          // add "from website" attribute
          result.forEach((item) => {
            item.from = utils.categorizeUrl(item.link);
          });
          this.setData({
            list: result,
            possibilities: [],
          });
        }
        console.log(`Get post list from ${ticker}`);
        console.log(result);
      }
    });
  },

  handleSelect(e) {
    let ticker = e.currentTarget.dataset.arg;
    this.setData({
      inputtedTicker: ticker
    });
    this.handleSearch(e);
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