import { defineConfig } from 'vitepress'

export default defineConfig({
  title: '个人代理服务器搭建教程',
  description: '面向零基础用户的个人代理服务器搭建教程',
  lang: 'zh-CN',
  cleanUrls: true,
  srcExclude: [
    'README.md',
    'DEPLOY.md',
    'PROJECT_BRIEF.md',
    'PROJECT_MEMORY.md',
    'SUMMARY.md',
    '教程大纲-GitBook版.md',
    '翻墙梯子搭建教程.md'
  ],
  lastUpdated: true,
  themeConfig: {
    logo: '/assets/diagrams/proxy-chain-simple.svg',
    siteTitle: 'LadderHelper',
    search: {
      provider: 'local',
      options: {
        locales: {
          root: {
            translations: {
              button: {
                buttonText: '搜索文档',
                buttonAriaLabel: '搜索文档'
              },
              modal: {
                displayDetails: '显示详情',
                resetButtonTitle: '清除搜索',
                backButtonTitle: '关闭搜索',
                noResultsText: '没有找到结果',
                footer: {
                  selectText: '选择',
                  selectKeyAriaLabel: '回车',
                  navigateText: '切换',
                  navigateUpKeyAriaLabel: '上箭头',
                  navigateDownKeyAriaLabel: '下箭头',
                  closeText: '关闭',
                  closeKeyAriaLabel: 'Esc'
                }
              }
            }
          }
        }
      }
    },
    nav: [
      { text: '开始阅读', link: '/docs/00-使用前必读' },
      { text: '参考资料', link: '/docs/99-参考资料' }
    ],
    sidebar: [
      {
        text: '开始之前',
        items: [
          { text: '使用前必读', link: '/docs/00-使用前必读' },
          { text: '代理服务器原理', link: '/docs/01-代理服务器原理' },
          { text: '准备清单', link: '/docs/02-准备清单' }
        ]
      },
      {
        text: '购买与配置',
        items: [
          { text: '购买个人域名', link: '/docs/03-购买个人域名' },
          { text: '购买 VPS', link: '/docs/04-购买VPS' },
          { text: '配置域名解析', link: '/docs/05-配置域名解析' },
          { text: '连接 VPS', link: '/docs/06-连接VPS' },
          { text: '开放服务器端口', link: '/docs/07-开放服务器端口' }
        ]
      },
      {
        text: '安装与使用',
        items: [
          { text: '安装 3x-ui', link: '/docs/08-安装3x-ui' },
          { text: '创建代理节点', link: '/docs/09-创建代理节点' },
          { text: '客户端配置与测试', link: '/docs/10-客户端配置与测试' }
        ]
      },
      {
        text: '维护与附录',
        items: [
          { text: '多节点和日常维护', link: '/docs/11-多节点和日常维护' },
          { text: '常见问题', link: '/docs/12-常见问题' },
          { text: '素材清单', link: '/docs/98-素材清单' },
          { text: '参考资料', link: '/docs/99-参考资料' }
        ]
      }
    ],
    outline: {
      level: [2, 3],
      label: '本页目录'
    },
    docFooter: {
      prev: '上一章',
      next: '下一章'
    },
    lastUpdated: {
      text: '最后更新',
      formatOptions: {
        dateStyle: 'medium',
        timeStyle: 'short'
      }
    },
    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '菜单',
    darkModeSwitchLabel: '外观',
    lightModeSwitchTitle: '切换到浅色模式',
    darkModeSwitchTitle: '切换到深色模式',
    externalLinkIcon: true
  },
  markdown: {
    image: {
      lazyLoading: true
    }
  },
  head: [
    ['meta', { name: 'viewport', content: 'width=device-width, initial-scale=1.0' }],
    ['meta', { name: 'theme-color', content: '#2563eb' }]
  ]
})
