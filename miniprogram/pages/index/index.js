Page({
  data: {
    templates: [],
    title: '',
    content: ''
  },

  inputTitle(e) {
    this.setData({ title: e.detail.value })
  },

  inputContent(e) {
    this.setData({ content: e.detail.value })
  },

  addTemplate() {
    if (!this.data.title || !this.data.content) {
      wx.showToast({ title: '请填写完整', icon: 'none' })
      return
    }

    wx.request({
      url: 'http://127.0.0.1:8000/api/templates',
      method: 'POST',
      data: {
        title: this.data.title,
        content: this.data.content,
        category: '通用'
      },
      success: (res) => {
        if (res.data.code === 201) {
          wx.showToast({ title: '新增成功！', icon: 'success' })
          this.setData({ title: '', content: '' })
          this.loadData()
        }
      },
      fail: (err) => {
        wx.showToast({ title: '请求失败', icon: 'error' })
        console.log(err)
      }
    })
  },

  loadData() {
    wx.request({
      url: 'http://127.0.0.1:8000/api/templates',
      method: 'GET',
      success: (res) => {
        if (res.data.code === 200) {
          this.setData({ templates: res.data.data })
        }
      },
      fail: (err) => {
        console.log('请求失败', err)
      }
    })
  },

  deleteTemplate(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这条提示词吗？',
      success: (res) => {
        if (res.confirm) {
          wx.request({
            url: `http://127.0.0.1:8000/api/templates/${id}`,
            method: 'DELETE',
            success: (res) => {
              if (res.data.code === 200) {
                wx.showToast({ title: '删除成功！', icon: 'success' })
                this.loadData()
              }
            },
            fail: (err) => console.log('请求失败', err)
          })
        }
      }
    })
  }
})