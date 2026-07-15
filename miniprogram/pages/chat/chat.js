Page({
  data: {
    messages: [],
    question: ''
  },

  inputQuestion(e) {
    this.setData({ question: e.detail.value })
  },

  sendMessage() {
    const q = this.data.question.trim()
    if (!q) {
      wx.showToast({ title: '请输入问题', icon: 'none' })
      return
    }

    let newMessages = [...this.data.messages, { role: 'user', content: q }]
    this.setData({ messages: newMessages, question: '' })

    wx.request({
      url: 'http://127.0.0.1:8000/api/ai/chat',
      method: 'POST',
      data: { prompt: q },
      success: (res) => {
        if (res.data.code === 200) {
          let aiMsg = { role: 'ai', content: res.data.data.answer }
          this.setData({ messages: [...this.data.messages, aiMsg] })
        } else {
          wx.showToast({ title: 'AI调用失败', icon: 'error' })
        }
      },
      fail: () => {
        wx.showToast({ title: '请求失败', icon: 'error' })
      }
    })
  }
})