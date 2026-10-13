# macOS Sonoma — CLaunch 皮肤

[![CLaunch](https://img.shields.io/badge/CLaunch-4.20%2B-blue)](http://pyonkichi.g1.xrea.com/en/claunch.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

把 Windows 上的快速启动器 [CLaunch](http://pyonkichi.g1.xrea.com/en/claunch.html)
做成 macOS 浅色风格：圆角窗口、红黄绿交通灯、分段控制分页、系统蓝选中态。

![preview](preview.png)

## 特点

- **圆角 11px 窗口**，浅灰工具栏 + 发丝分隔线，主体 `#F7F7F9`
- **左上角三个圆钮**：关闭（红）/ 锁定（黄）/ 模式切换（绿），鼠标滑过显示 mac 字形（×、−、⤢）
- **分页为分段控制器胶囊**，选中页白色，未选中页浅灰
- **图标按钮常规无底色**，滑过显示浅灰圆角块，文字转系统蓝
- **右键子菜单**：选中项为 macOS 系统蓝 `#0A84FF` 白字
- 字体默认 **Microsoft YaHei UI**（含中文字形），可自行换成 SF Pro Text / Inter

## 安装

> ⚠️ CLaunch 4.x 的皮肤是 **zip 直放**，不要解压。

1. 下载 [`macOS Sonoma.zip`](macOS%20Sonoma.zip)
2. 把它整个复制到 CLaunch 安装目录下的 `Skins\`（注意是复数）：

   ```
   C:\Program Files\CLaunch\Skins\
   ```

3. 重启 CLaunch（皮肤列表在启动时扫描）
4. 面板上右键 → **选项** → **外观** → 选择 **macOS Sonoma**
5. 建议点同一对话框里的 **「应用推荐设置」**，让分页 / 按钮尺寸与本皮肤对齐

## 要求

| 项目 | 说明 |
|---|---|
| CLaunch | 4.20 或更高（Unicode 版），已在 4.23 上按官方皮肤结构对齐 |
| 显示色深 | 32bpp（Windows 默认即是） |

## 目录结构

```
macOS Sonoma.zip          安装包（zip 根目录即 skin.xml + 部件图）
src/macOS Sonoma/         皮肤源文件（同 zip 内容，方便直接查看 / 修改）
tools/                    构建脚本（Pillow，4 倍超采样 + LANCZOS 缩小）
  build_skin.py             生成全部部件图
  build_xml.py              生成 skin.xml 并打包 zip
  verify_render.py          按 CLaunch 的 9 宫格规则实拼窗口做一致性验证
  make_hero.py              生成 README 预览图
preview.html              浏览器交互预览（悬停可看交互态）
```

## 自己改

部件图全部由 `tools/` 里的脚本从零绘制，改色值重跑即可：

```bash
python tools/build_skin.py   # 重画部件图
python tools/build_xml.py    # 重写 skin.xml 并重新打包 zip
```

配色集中在 `build_skin.py` 顶部的调色板区块；字体在 `build_xml.py` 的
`FONT` 变量。`skin.xml` 是 **UTF-16 LE 带 BOM**，手改请用支持该编码的编辑器。

### 已知取舍

- 未内置窗口 / 菜单投影（需把阴影烘进切片图，权衡后保持切片简单可靠）
- 省略了可选的 `searchwindow` 元素，搜索窗口自动沿用 `submenu` 样式

## License

[MIT](LICENSE)
