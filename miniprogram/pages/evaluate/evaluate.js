Page({
  data: {
    question: '',
    standardAnswer: '',
    userAnswer: '',
    score: ''
  },

  inputQuestion(e) {
    this.setData({ question: e.detail.value })
  },

  inputStandard(e) {
    this.setData({ standardAnswer: e.detail.value })
  },

  inputUser(e) {
    this.setData({ userAnswer: e.detail.value })
  },

  evaluate() {
    const { question, standardAnswer, userAnswer } = this.data
    
    if (!question || !standardAnswer || !userAnswer) {
      wx.showToast({ title: '请填写完整信息', icon: 'none' })
      return
    }

    wx.showLoading({ title: 'AI评测中...' })

    wx.request({
      url: 'http://127.0.0.1:8000/api/ai/evaluate',
      method: 'POST',
      data: {
        question: question,
        standard_answer: standardAnswer,
        user_answer: userAnswer
      },
      success: (res) => {
        wx.hideLoading()
        if (res.data.code === 200) {
          this.setData({ score: res.data.data.score })
        } else {
          wx.showToast({ title: '评测失败', icon: 'error' })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        wx.showToast({ title: '网络请求失败', icon: 'error' })
        console.log(err)
      }
    })
  }
})