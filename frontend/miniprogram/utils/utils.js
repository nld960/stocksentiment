function categorizeUrl(url) {
  if (url.includes("eastmoney")) {
    return "东方财富";
  } else if (url.includes("xueqiu")) {
    return "雪球";
  } else {
    return "?";
  }
}

module.exports = {
  categorizeUrl
};