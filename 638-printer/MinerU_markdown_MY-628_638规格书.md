# MY-628/638

打印模组规格书

![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-01/9f4f97fa-ad5f-4dcb-b225-af1e0ead5221/53ef478dbb64360d45cb879f3b91f9d65fd09ff9e763517065aacf7985bf493e.jpg)


# 目 录

1 简介 ..

$\textcircled{1}$ 628. 

$\textcircled{2}$ 主要特点..

2 尺寸图与引脚定义.

2.1 628 638 尺寸图 .

2.2 引脚定义.

3 技术规格参数. 4

4 指令列表.. 5

5 指令详解..

$\textcircled{1}$ 打印及进纸指令..

打印并进纸..

回车..

打印并进纸 n 点.

打印并进纸 n 行.. 8

$\textcircled{2}$ 打印设置指令. 8

设置行间距为 n 点 8

设置行间距为默认值. 8

设置打印位置. 9

设置左侧空白量.. 9

设置左边边距 10

设置字符右间距. . 10

选择字型. .10

设置字符打印方式.

设定字符大小.. . 12

设定、解除反白打印.. 12

设定、解除下划线. 13

设定、解除 $9 0 ^ { \circ }$ 旋转打印. . 14

设定、解除粗体打印. 14

设定、解除重叠打印. 15

设定、解除颠倒打印. 15

设置打印对齐方式.. 16

设定汉字模式. 17

设置汉字字符打印模式组合. 17

取消汉字模式. . 18

定义用户自定义汉字. 19

选择国际字符集. .. 20

选择字符代码页.. 21

切换双字节编码.. 23

$\textcircled{3}$ 图形打印指令. . 23

图形垂直取模数据填充 .. 23

图片水平取模数据打印. 24

定义下传位图. . 26

打印下传位图. 27

定义 NV 位图. .27

打印 NV 位图. ..30

打印光栅位图. . 30

水平位置打印行线段（曲线打印命令） ... 31

$\textcircled{4}$ 制表指令.. .36

水平制表.. ..36

设置水平制表位置 37

$\textcircled{5}$ 一维条码打印指令. . 37

设置一维条码可读字符（HRI）打印位置 . 37

设置一维条码高度. . 38

设置一维条码宽度 . 38

打印一维条码. . 39

$\textcircled{6}$ 二维码打印指令. . 44

设置 QR 码的模块类型. ..44

设置 QR 码的错误校正水平误差 ..44

存储 QR 码的数据到 QR 码缓冲区. . 45

打印 QR 码.. .. 45

设置 QR 码的图形信息. ..46

打印二维码. . 47

$\textcircled{7}$ 状态指令.. ..47

传送状态. ..47

实时传送状态. . 48

实时打印机请求.. . 50

允许、禁止自动状态回复（ASB） . 51

$\textcircled{8}$ 其他指令. .52

初始化打印机. . 52

打印自测页.. . 53

设置打印浓度. . 53

产生钱箱脉冲（OnlyForDrawer） .54

# 1 简介

# $\textcircled{1}$ MY-628/638

MY-628 是一款58mm热敏打印模组，符合众多行业票据打印。低功耗高品质，性能稳定，马达与热敏打印头经过无数测试达到高标准，一直以来受到商户青睐的一款热敏打印机。

支持的操作系统列表：

WINDOWS XP 

WINDOWS 7 32/64 

WINDOWS 8 

WINDOWS 10 

UBUNTU 12.04 32/64 

UBUNTU 14.04 32/64 

安卓

单片机

# 2 尺寸图与引脚定义

# 2.1 MY-628(58mm）尺寸图

![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-01/9f4f97fa-ad5f-4dcb-b225-af1e0ead5221/af51810c6285fc5c6db53d4a066d83531785e41e6f8f0e99cc4b9ff7cd59edd9.jpg)


# 2.2 MY-638（80mm）尺寸图

![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-01/9f4f97fa-ad5f-4dcb-b225-af1e0ead5221/ded2881cc4930e7642ab5dbd24572250b4422c3af17c43d50f164f5e396a344d.jpg)


# 2.3 引脚定义

![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-01/9f4f97fa-ad5f-4dcb-b225-af1e0ead5221/440bff4ae05e63fe39b4a9c5cb6ebac65665f99c74b5eb016e2ba0c9c966374b.jpg)



RS232 接口定义（XH2.54-5）


<table><tr><td>Pin number</td><td>Signal name</td><td>说明</td><td>方向</td></tr><tr><td>1</td><td>VH</td><td>Power</td><td>正极(5-9V)</td></tr><tr><td>2</td><td>DTR</td><td>Flow control</td><td>数据终端就绪（可接可不接）</td></tr><tr><td>3</td><td>TX</td><td>printer output</td><td>输出</td></tr><tr><td>4</td><td>RX</td><td>printer input</td><td>输入</td></tr><tr><td>5</td><td>GND</td><td>GND</td><td>接地</td></tr></table>


TTL 接口定义（XH2.54-5）


<table><tr><td>Pin number</td><td>Signal name</td><td>说明</td><td>方向</td></tr><tr><td>1</td><td>VH</td><td>Power</td><td>正极(5-9V)</td></tr><tr><td>2</td><td>DTR</td><td>Flow control</td><td>数据终端就绪（可接可不接）</td></tr><tr><td>3</td><td>TX</td><td>printer output</td><td>输出</td></tr><tr><td>4</td><td>RX</td><td>printer input</td><td>输入</td></tr><tr><td>5</td><td>GND</td><td>GND</td><td>接地</td></tr></table>


3 技术规格参数


<table><tr><td colspan="2">型号</td><td>MY-628</td><td>MY-638</td></tr><tr><td rowspan="6">打印</td><td>打印方式</td><td colspan="2">热敏行式打印</td></tr><tr><td>分辨率</td><td colspan="2">203Dpi(8dot/mm)</td></tr><tr><td>打印速度</td><td colspan="2">MAX. 80nn/s</td></tr><tr><td>有效打印宽度</td><td>48mm</td><td>72mm</td></tr><tr><td>接口</td><td colspan="2">RS232+TTL</td></tr><tr><td>串口配置</td><td colspan="2">波特率: 9600 数据位: 8 停止位: 1 奇偶校验: 无</td></tr><tr><td rowspan="5">纸张</td><td>纸张类型</td><td colspan="2">热敏纸</td></tr><tr><td>纸张宽度</td><td>57.5±0.5mm</td><td>79.5±0.5mm</td></tr><tr><td>纸卷直径</td><td colspan="2">Max. 50mm</td></tr><tr><td>纸张厚度</td><td colspan="2">0.053-0.1mm</td></tr><tr><td>撕纸方式</td><td colspan="2">手撕</td></tr><tr><td>可靠性</td><td>打印头寿命</td><td colspan="2">50KM</td></tr><tr><td rowspan="2">字体</td><td>中文</td><td colspan="2">GBK:16x16, 24x24</td></tr><tr><td>西文</td><td colspan="2">ASCII:8x16, 9x17, 9x24, 12x24</td></tr><tr><td rowspan="2">条码</td><td>一维</td><td colspan="2">UPC-A, UPC-E, EAN8, EAN13, code39, ITF, CODEBAR, CODE128, CODE93</td></tr><tr><td>二维</td><td colspan="2">QR code, PDF417</td></tr><tr><td rowspan="2">内存</td><td>RAM</td><td colspan="2">64K</td></tr><tr><td>Flash</td><td colspan="2">4M</td></tr><tr><td>电源</td><td>电源供应</td><td colspan="2">5-9V/1.5A</td></tr><tr><td rowspan="3">软件</td><td>指令集</td><td colspan="2">ESC/POS(票据)</td></tr><tr><td>驱动</td><td colspan="2">Windows XP、7、8、10/ Linux</td></tr><tr><td>SDK</td><td colspan="2">Windows SDK/Linux SDK/Android SDK</td></tr><tr><td rowspan="4">环境</td><td>工作温度</td><td colspan="2">-10°C-50°C</td></tr><tr><td>工作湿度</td><td colspan="2">20%RH-85% RH</td></tr><tr><td>存储温度</td><td colspan="2">-20°C-60°C</td></tr><tr><td>存储湿度</td><td colspan="2">5%-90%RH</td></tr><tr><td rowspan="3">物理特性</td><td>机芯尺寸(WxDxH)</td><td>69*33*15mm</td><td>91.4*33*15mm</td></tr><tr><td>主板尺寸(WxDxH)</td><td>47*37mm</td><td>47*37mm</td></tr><tr><td>重量(g)</td><td>45g</td><td>50g</td></tr></table>


4 指令列表


<table><tr><td>LF</td><td>打印并进纸</td><td rowspan="4">打印及进纸指令</td></tr><tr><td>CR</td><td>回车</td></tr><tr><td>ESC J</td><td>打印并进纸 n 点</td></tr><tr><td>ESC d</td><td>打印并进纸 n 行</td></tr><tr><td>ESC 3</td><td>设置行间距为 n 点</td><td rowspan="23">打印设置指令</td></tr><tr><td>ESC 2</td><td>设置行间距为默认值</td></tr><tr><td>ESC $</td><td>设置打印位置</td></tr><tr><td>GS L nL nH</td><td>设置左侧空白量</td></tr><tr><td>ESC B n</td><td>设置左边边距</td></tr><tr><td>ESC SP n</td><td>设置字符右间距</td></tr><tr><td>ESC !</td><td>设置字符打印方式</td></tr><tr><td>ESC M n</td><td>选择字型</td></tr><tr><td>GS ! n</td><td>设定字符大小</td></tr><tr><td>GS B n</td><td>设定、解除反白打印</td></tr><tr><td>ESC - n</td><td>设定、解除下划线</td></tr><tr><td>ESC V n</td><td>设定、解除90°旋转打印</td></tr><tr><td>ESC E n</td><td>设定、解除粗体打印</td></tr><tr><td>ESC G n</td><td>设定、解除重叠打印</td></tr><tr><td>ESC { n</td><td>设定、解除颠倒打印</td></tr><tr><td>ESC a</td><td>设置打印对齐方式</td></tr><tr><td>FS &amp;</td><td>设定汉字模式</td></tr><tr><td>FS ! n</td><td>设置汉字字符打印模式组合</td></tr><tr><td>FS .</td><td>取消汉字模式</td></tr><tr><td>FS 2</td><td>定义用户自定义汉字</td></tr><tr><td>ESC R n</td><td>选择国际字符集</td></tr><tr><td>ESC t n</td><td>选择字符代码页</td></tr><tr><td>ESC 9 n</td><td>切换双字节编码</td></tr><tr><td>ESC *</td><td>图形垂直取模数据填充</td><td rowspan="8">图形打印指令</td></tr><tr><td>GS v 0</td><td>图片水平取模数据打印</td></tr><tr><td>GS *</td><td>定义下传位图</td></tr><tr><td>GS / m</td><td>打印下传位图</td></tr><tr><td>FS q</td><td>定义 NV 位图</td></tr><tr><td>FS p n m</td><td>打印 NV 位图</td></tr><tr><td>GS v 0 m</td><td>打印光栅位图</td></tr><tr><td>GS n</td><td>水平位置打印行线段(曲线打印命令)</td></tr><tr><td>HT</td><td>水平制表</td><td rowspan="2">制表指令</td></tr><tr><td>ESC D</td><td>设置水平制表位置</td></tr><tr><td>GS H</td><td>设置一维条码可读字符(HRI)打印位置</td><td rowspan="2">一维条码打印指令</td></tr><tr><td>GS h</td><td>设置一维条码高度</td></tr><tr><td>GS w</td><td>设置一维条码宽度</td><td rowspan="2"></td></tr><tr><td>GS k</td><td>打印一维条码</td></tr><tr><td>GS (</td><td>打印二维码</td><td rowspan="6">二维码打印指令</td></tr><tr><td>GS (k pL pH cn fn n</td><td>设置 QR 码的模块类型</td></tr><tr><td>GS (k pL pH cn fn n</td><td>设置 QR 码的错误校正水平误差</td></tr><tr><td>GS(k pL pH cn fn m dl…dk</td><td>存储 QR 码的数据到 QR 码缓冲区</td></tr><tr><td>GS(k pL pH cn fn m</td><td>打印 QR 码</td></tr><tr><td>GS(k pL pH cn fn m</td><td>设置 QR 码的图形信息</td></tr><tr><td>GS r n</td><td>传送状态</td><td rowspan="4">状态指令</td></tr><tr><td>DLE EOT n</td><td>实时传送状态</td></tr><tr><td>DLE ENQ n</td><td>实时打印机请求</td></tr><tr><td>GS a n</td><td>允许、禁止自动状态回复(ASB)</td></tr><tr><td>ESC @</td><td>初始化打印机</td><td rowspan="4">其他指令</td></tr><tr><td>DC2 T</td><td>打印自测页</td></tr><tr><td>ESC 7</td><td>设置打印浓度</td></tr><tr><td>ESC p m t1 t2</td><td>产生钱箱脉冲</td></tr></table>

# 5 指令详解

# $\textcircled{1}$ 打印及进纸指令

# 打印并进纸

<table><tr><td>指令名称</td><td>打印并进纸</td></tr><tr><td>指令代码</td><td>ASCII : LF
十进制 : 10
十六进制 : 0A</td></tr><tr><td>功能描述</td><td>将打印缓存里的内容打印,之后根据当前的行间距设置进纸一行,并调整打印位置至下一行的起始位置</td></tr><tr><td>参数范围</td><td>无</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>无</td></tr><tr><td>使用示例</td><td>无</td></tr></table>

# 回车

<table><tr><td>指令名称</td><td>回车</td></tr><tr><td>指令代码</td><td>ASCII : CR
十进制 : 13
十六进制 : 0D</td></tr><tr><td>功能描述</td><td>当打印缓存不为空时作用同LF,否则无作用</td></tr><tr><td>参数范围</td><td>无</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td></td></tr><tr><td>使用示例</td><td>无</td></tr></table>

# 打印并进纸n点

<table><tr><td>指令名称</td><td>打印并进纸 n 点</td></tr><tr><td>指令代码</td><td>ASCII : ESC J n
十进制 : 27 74 n
十六进制 : 1B 4A n</td></tr><tr><td>功能描述</td><td>将打印缓存里的内容打印并进纸 n 点</td></tr><tr><td>参数范围</td><td>0 ≤ n ≤ 255</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>当打印缓存为空时，只进纸 n 点
本指令执行后，打印位置移动至下一行的起始位置</td></tr><tr><td>使用示例</td><td>1b 40 30 31 32 1b 4a 10</td></tr></table>


打印并进纸n行


<table><tr><td>指令名称</td><td>打印并进纸 n 行</td></tr><tr><td>指令代码</td><td>ASCII : ESC d n
十进制 : 27 100 n
十六进制 : 1B 64 n</td></tr><tr><td>功能描述</td><td>将打印缓存里的内容打印并进纸 n 行</td></tr><tr><td>参数范围</td><td>0 ≤ n ≤ 255</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>该命令设置打印起始位置为行起点</td></tr><tr><td>使用示例</td><td>1b 40 30 31 32 1b 64 01</td></tr></table>

# $\textcircled{2}$ 打印设置指令


设置行间距为 $\mathbf { n }$ 点


<table><tr><td>指令名称</td><td>设置行间距为n点</td></tr><tr><td>指令代码</td><td>ASCII : ESC 3 n十进制 : 27 51 n十六进制 : 1B 33 n</td></tr><tr><td>功能描述</td><td>设置行间距为n点</td></tr><tr><td>参数范围</td><td>0 ≤ n ≤ 255</td></tr><tr><td>默认值</td><td>n = 33</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>行间距示意如下:字符宽度 AAAAAAAAAAAAA 行间距 BBBBBBBBBBBBB 若设定的行间距小于一行中的最大字符高度,那么该行行间距等于最大字符高度若 ESC 2、ESC @、打印机复位、打印机断电,行间距恢复为默认值</td></tr><tr><td>使用示例</td><td>1b 401b 33 3030 31 32 0d 0a30 31 32 0d 0a1b 3230 31 32 0d 0a30 31 32 0d 0a</td></tr></table>


设置行间距为默认值


<table><tr><td>指令名称</td><td>设置行间距为默认值</td></tr><tr><td>指令代码</td><td>ASCII : ESC 2
十进制 : 27 50
十六进制 : 1B 32</td></tr><tr><td>功能描述</td><td>设置行间距为默认的 33 点</td></tr><tr><td>参数范围</td><td>无</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>行间距示意详看 ESC 3 指令
    若设定的行间距小于一行中的最大字符高度,那么该行行间距等于最大字符高度
    可使用 ESC 3 自定义行间距</td></tr><tr><td>使用示例</td><td>无</td></tr></table>


设置打印位置


<table><tr><td>指令名称</td><td>设置打印位置</td></tr><tr><td>指令代码</td><td>ASCII : ESC $ nL nH
十进制 : 27 36 nL nH
十六进制 : 1B 24 nL nH</td></tr><tr><td>功能描述</td><td>调整打印位置到距离打印起始位置的 (nL+nH×256) 点处</td></tr><tr><td>参数范围</td><td>0 ≤ nL ≤ 255, 0 ≤ nH ≤ 255</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>此指令只对本行有效，换行后打印位置复位为打印起始位置
超出打印范围则移到下一行打印</td></tr><tr><td>使用示例</td><td>1b 40 1b 24 08 00
30 31 32 0d 0a
30 31 32 0d 0a</td></tr></table>


设置左侧空白量


<table><tr><td>指令名称</td><td>设置打印位置</td></tr><tr><td>指令代码</td><td>ASCII : GS L nL nH十进制 : 29 76 nL nH十六进制 : 1D 4C nL nH</td></tr><tr><td>功能描述</td><td>设置左侧空白量为 (nL+nH×256) 点</td></tr><tr><td>参数范围</td><td>0 ≤ nL ≤ 255, 0 ≤ nH ≤ 255</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>该命令仅在一行的起始位置处理时有效。图例示意如下:打印区域左边空白 打印区域宽度</td></tr><tr><td></td><td>如果设置超出了可打印范围,则使用可打印单位的最大值</td></tr><tr><td>使用示例</td><td>1b 40 1d 4c 08 0030 31 32 0d 0a30 31 32 0d 0a</td></tr></table>


设置左边边距


<table><tr><td>指令名称</td><td>设置左边边距</td></tr><tr><td>指令代码</td><td>ASCII : ESC B n十进制 : 27 66 n十六进制 : 1B 42 n</td></tr><tr><td>功能描述</td><td>设置字符左边边距为n点</td></tr><tr><td>参数范围</td><td>0 ≤ n ≤ 47</td></tr><tr><td>默认值</td><td>0</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td></td></tr><tr><td>使用示例</td><td>1B 401B 42 0830 31 32 0D 0A</td></tr></table>


设置字符右间距


<table><tr><td>指令名称</td><td>设置字符右间距</td></tr><tr><td>指令代码</td><td>ASCII : ESC SP n十进制 : 27 32 n十六进制 : 1B 20 n</td></tr><tr><td>功能描述</td><td>设置字符右侧的间距为[n×0.125毫米]。</td></tr><tr><td>参数范围</td><td>0 ≤ n ≤ 255</td></tr><tr><td>默认值</td><td>0</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>对于倍宽模式,右侧字符间距是一般模式下的两倍。当字符被放大,右侧字符间距是一般模式下的n倍。该命令不影响汉字字符的设定。</td></tr><tr><td>使用示例</td><td>1B 401B 20 1830 31 32 0D 0A</td></tr></table>


选择字型


<table><tr><td>指令名称</td><td colspan="2">选择字型</td></tr><tr><td>指令代码</td><td colspan="2">ASCII : ESC M n十进制 : 27 77 n十六进制 : 1b 4d n</td></tr><tr><td rowspan="3">功能描述</td><td colspan="2">选择字符字型</td></tr><tr><td>n</td><td>功能</td></tr><tr><td>0,48</td><td>选择字型 A (12×24)。</td></tr></table>

<table><tr><td rowspan="4"></td><td rowspan="4"></td><td>1,49</td><td>选择字型 B (9×24)。</td><td rowspan="4"></td></tr><tr><td>2,50</td><td>选择字型 C (9×17)</td></tr><tr><td>3,51</td><td>选择字型 D (8×16)</td></tr><tr><td>4,52</td><td>选择字型 E (16×18)</td></tr><tr><td>参数范围</td><td colspan="4">n = 0, 1,2,3,4, 48, 49, 50,51,52</td></tr><tr><td>默认值</td><td colspan="4">n = 0</td></tr><tr><td>支持型号</td><td colspan="4">部分型号</td></tr><tr><td>注意事项</td><td colspan="4">·ESC ! 也可以选择字体类型。但是最后接收到的命令所做的设置有效。</td></tr><tr><td>使用示例</td><td colspan="4">1b 401b 4d 0030 31 32 0d 0a1b 4d 0130 31 32 0d 0a1b 4d 0230 31 32 0d 0a1b 4d 0330 31 32 0d 0a1b 4d 0430 31 32 0d 0a</td></tr></table>

# 设置字符打印方式

<table><tr><td>指令名称</td><td>设置字符打印方式</td></tr><tr><td>指令代码</td><td>ASCII : ESC ! n十进制 : 2733 n十六进制 : 1B 21 n</td></tr><tr><td>功能描述</td><td>设置字符打印方式(字型、反白、倒置、粗体、倍高、倍宽、和下划线),参数n的位定义如下:位功能值0 10 字型正常小字1 未定义2 未定义3 粗体取消设定4 倍 高取消设定5 倍 宽取消设定6 未定义7 下划线取消设定</td></tr><tr><td>参数范围</td><td>无</td></tr><tr><td>默认值</td><td>n=0</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>此指令对中文字体及外文字体均有效当ESC@、打印机复位、断电后,本指令的设置失效</td></tr><tr><td>使用示例</td><td>1B 40 1B 21 01 30 31 32 0D 0A</td></tr></table>

<table><tr><td>1B 40 1B 21 02 30 31 32 0D 0A</td></tr><tr><td>1B 40 1B 21 04 30 31 32 0D 0A</td></tr><tr><td>1B 40 1B 21 08 30 31 32 0D 0A</td></tr><tr><td>1B 40 1B 21 10 30 31 32 0D 0A</td></tr><tr><td>1B 40 1B 21 20 30 31 32 0D 0A</td></tr><tr><td>1B 40 1B 21 40 30 31 32 0D 0A</td></tr><tr><td>1B 40 1B 21 80 30 31 32 0D 0A</td></tr></table>


设定字符大小


<table><tr><td>指令名称</td><td colspan="6">设定字符大小</td></tr><tr><td>指令代码</td><td colspan="6">ASCII : GS ! n十进制 : 2933 n十六进制 : 1d21 n</td></tr><tr><td rowspan="9">功能描述</td><td>设置字符大小为1-8倍宽,1-8倍高定义如下:用0到3位设定字符高度4到7位设定字符宽度如下所示表1字符宽度设定 表2字符高度设定十六进制</td><td>十进制</td><td>宽度</td><td>十六进制</td><td>十进制</td><td>宽度</td></tr><tr><td>00</td><td>0</td><td>1(普通)</td><td>00</td><td>0</td><td>1(普通)</td></tr><tr><td>10</td><td>16</td><td>2(倍宽)</td><td>01</td><td>1</td><td>2(倍高)</td></tr><tr><td>20</td><td>32</td><td>3</td><td>02</td><td>2</td><td>3</td></tr><tr><td>30</td><td>48</td><td>4</td><td>03</td><td>3</td><td>4</td></tr><tr><td>40</td><td>64</td><td>5</td><td>04</td><td>4</td><td>5</td></tr><tr><td>50</td><td>80</td><td>6</td><td>05</td><td>5</td><td>6</td></tr><tr><td>60</td><td>96</td><td>7</td><td>06</td><td>6</td><td>7</td></tr><tr><td>70</td><td>112</td><td>8</td><td>07</td><td>7</td><td>8</td></tr><tr><td>参数范围</td><td colspan="6">无</td></tr><tr><td>默认值</td><td colspan="6">n=0</td></tr><tr><td>支持型号</td><td colspan="6">所有型号</td></tr><tr><td>注意事项</td><td colspan="6">此指令对除HRI字符外的中文字体及外文字体均有效当ESC@、打印机复位、断电后,本指令的设置失效</td></tr><tr><td>使用示例</td><td colspan="6">1b 40 1d 21 1130 31 32 0d 0a30 31 32 0d 0a</td></tr></table>


设定、解除反白打印


<table><tr><td>指令名称</td><td>设定、解除反白打印</td></tr><tr><td>指令代码</td><td>ASCII : GS B n
十进制 : 29 66 n</td></tr><tr><td></td><td>十六进制:1d42n</td></tr><tr><td>功能描述</td><td>设定或解除反白打印模式。当n的最低有效位为0时,反白模式关闭。当n的最低有效位为1时,反白模式打开。</td></tr><tr><td>参数范围</td><td>无</td></tr><tr><td>默认值</td><td>n=0</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>仅n的最低位有效。该命令对内置字符和用户自定义字符均有效。当反白模式打开时,它对ESC SP设定的空白也有效。该命令不影响位图、用户自定义位图、条形码、HRI字符、和由HT跳过的空间,ESC$。该命令不影响行间距。反白模式优先于下划线模式。当设定反白模式时,即使下划线模式打开也被禁止(但是不取消)。当ESC@、打印机复位、断电后,本指令的设置失效</td></tr><tr><td>使用示例</td><td>1b 40 1d 42 0130 31 32 0d 0a30 31 32 0d 0a</td></tr></table>

# 设定、解除下划线

<table><tr><td>指令名称</td><td colspan="2">设定、解除下划线</td></tr><tr><td>指令代码</td><td colspan="2">ASCII : ESC - n十进制 : 2745 n十六进制 : 1B 2D n</td></tr><tr><td rowspan="5">功能描述</td><td colspan="2">基于以下的n值,设定/解除下划线模式:</td></tr><tr><td>n</td><td>功能</td></tr><tr><td>0,48</td><td>解除下划线模式</td></tr><tr><td>1,49</td><td>设定下划线模式(1点粗)</td></tr><tr><td>2,50</td><td>设定下划线模式(2点粗)</td></tr><tr><td>参数范围</td><td colspan="2">0 ≤ n ≤ 2,48 ≤ n ≤ 50</td></tr><tr><td>默认值</td><td colspan="2">n = 0</td></tr><tr><td>支持型号</td><td colspan="2">所有型号</td></tr><tr><td>注意事项</td><td colspan="2">打印机可以给所有字符打印下划线(包括字符右边的间隔),但是被HT设置的空白除外。打印机不能给顺时针旋转90°的字符以及反白字符打印下划线。当通过设置n的值为0或48解除下划线模式时,其后的数据不被打印下划线,并且在解除下划线模式之前设置的下划线的粗度不改变。缺省的下划线粗度为1点。改变字符大小不影响当前下划线的粗度。使用ESC!也可以设定或解除下划线模式。可是要注意,最后接收的命令是有效的。</td></tr><tr><td rowspan="6">使用示例</td><td colspan="2">1b 40 1b 2d 01</td></tr><tr><td colspan="2">30 31 32 0d 0a</td></tr><tr><td colspan="2">1b 40 1b 2d 02</td></tr><tr><td colspan="2">30 31 32 0d 0a</td></tr><tr><td colspan="2">1b 40 1b 2d 00</td></tr><tr><td colspan="2">30 31 32 0d 0a</td></tr></table>

# 设定、解除 $9 0 ^ { \circ }$ 旋转打印

<table><tr><td>指令名称</td><td>设定、解除顺时针90°旋转打印</td></tr><tr><td>指令代码</td><td>ASCII : ESC V n十进制 : 27 86 n十六进制 : 1B 56 n</td></tr><tr><td>功能描述</td><td>设定或解除90°旋转打印。当n等于0或48时,解除90°旋转打印。当n等于1或49时,设置90°旋转打印。</td></tr><tr><td>参数范围</td><td>0≤n≤1, 48≤n≤49</td></tr><tr><td>默认值</td><td>n=0</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>当设置了下划线模式时,对于顺时针90°旋转的字符,打印机不加下划线。在顺时针90°旋转模式下,倍高和倍宽命令放大字符的方向与一般模式下倍高倍宽命令放大字符的方向相反。当ESC@、打印机复位、断电后,本指令的设置失效</td></tr><tr><td>使用示例</td><td>1b 40 1b 56 0130 31 32 0d 0a30 31 32 0d 0a</td></tr></table>

# 设定、解除粗体打印

<table><tr><td>指令名称</td><td>设定、解除粗体打印</td></tr><tr><td>指令代码</td><td>ASCII : ESC En十进制 : 27 69 n十六进制 : 1B 45 n</td></tr><tr><td>功能描述</td><td>设定或解除粗体打印模式。当n的最低有效位为0时,解除粗体打印模式。当n的最低有效位为1时,设定粗体打印模式。</td></tr><tr><td>参数范围</td><td>0 ≤ n ≤ 255</td></tr><tr><td>默认值</td><td>n = 0</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>仅n的最低有效位允许使用该命令和ESC!以同一方式设定和解除粗体打印模式。当这个命令和ESC!同时使用,时要小心。当ESC@、打印机复位、断电后,本指令的设置失效</td></tr><tr><td>使用示例</td><td>1b 40 1b 45 0130 31 32 0d 0a</td></tr></table>

<table><tr><td>1b 40 1b 45 00
30 31 32 0d 0a
1b 40 1b 45 01
B0 AE C9 CF D7 D4 BC BA OD OA
1b 40 1b 45 00
B0 AE C9 CF D7 D4 BC BA OD OA</td></tr></table>

# 设定、解除重叠打印

<table><tr><td>指令名称</td><td>设定、解除重叠打印</td></tr><tr><td>指令代码</td><td>ASCII : ESC G n十进制 : 27 71 n十六进制 : 1B 47 n</td></tr><tr><td>功能描述</td><td>设定或解除重叠打印模式。当n的最低有效位为0时,解除重叠打印模式。当n的最低有效位为1时,设定重叠打印模式。</td></tr><tr><td>参数范围</td><td>0 ≤ n ≤ 255</td></tr><tr><td>默认值</td><td>n = 0</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>仅n的最低有效位允许使用。在重叠模式和粗体模式中打印机输出是相同的。当ESC@、打印机复位、断电后,本指令的设置失效</td></tr><tr><td>使用示例</td><td>1b 40 1b 47 0030 31 32 0d 0a1b 40 1b 47 0130 31 32 0d 0a1b 40 1b 47 01BO AE C9 CF D7 D4 BC BA OD OA</td></tr></table>

# 设定、解除颠倒打印

<table><tr><td>指令名称</td><td>设定、解除颠倒打印</td></tr><tr><td>指令代码</td><td>ASCII : ESC {n
十进制 : 27 123 n
十六进制 : 1B 7B n}</td></tr><tr><td>功能描述</td><td>设置或解除颠倒打印模式。
当n的最低有效位为0时，关闭颠倒打印模式。
当n的最低有效位为1时，打开颠倒打印模式。</td></tr></table>

<table><tr><td rowspan="2"></td><td>当颠倒打印模式关闭时。</td><td>当颠倒打印模式打开时。</td></tr><tr><td>ABCDEF012345</td><td>进纸方向</td></tr><tr><td>参数范围</td><td colspan="2">0≤n≤255</td></tr><tr><td>默认值</td><td colspan="2">n=0</td></tr><tr><td>支持型号</td><td colspan="2">所有型号</td></tr><tr><td>注意事项</td><td colspan="2">仅n的最低位有效。
该命令仅在标准模式中一行开始时输入才有效。
在颠倒打印模式，打印机先将要打印的行旋转180°然后再打印。
当ESC@、打印机复位、断电后，本指令的设置失效</td></tr><tr><td>使用示例</td><td colspan="2">1b 40 1b 7b 0030 31 32 0d 0a1b 40 1b 7b 0130 31 32 0d 0a1b 40 1b 7b 01BO AE C9 CF D7 D4 BC BA OD OA</td></tr></table>

# 设置打印对齐方式

<table><tr><td>指令名称</td><td>设置打印对齐方式(居左、居中、居右)</td></tr><tr><td>指令代码</td><td>ASCII : ESC a n十进制 : 27 97 n十六进制 : 1B 61 n</td></tr><tr><td>功能描述</td><td>对一行中的所有数据进行对齐处理,n 值意义如下:n模式0,48 居左1,49 居中2,50 居右</td></tr><tr><td>参数范围</td><td>0 ≤ n ≤ 2 或 48 ≤ n ≤ 50</td></tr><tr><td>默认值</td><td>n = 0</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>当 ESC @、打印机复位、断电后,本指令的设置失效</td></tr><tr><td>使用示例</td><td>1B 40 1B 61 0230 31 32 0D 0A1B 40 1B 61 0130 31 32 0D 0A1B 40 1B 61 0030 31 32 0D 0A</td></tr></table>


设定汉字模式


<table><tr><td>指令名称</td><td>设定汉字模式</td></tr><tr><td>指令代码</td><td>ASCII : FS &amp;
十进制 : 28 38
十六进制 : 1C 26</td></tr><tr><td>功能描述</td><td>选择汉字模式</td></tr><tr><td>参数范围</td><td>无</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>选择汉字字符模式时，打印机处理所有汉字代码，每次两个字节。
以第一字节，第二字节的顺序处理汉字代码。</td></tr><tr><td>使用示例</td><td>1b 40 1C 26 B0 AE C9 CF D7 D4 BC BA 0d 0a
1C 2E B0 AE C9 CF D7 D4 BC BA 0d 0a</td></tr></table>


设置汉字字符打印模式组合


<table><tr><td>指令名称</td><td colspan="5">设置汉字字符打印模式组合</td></tr><tr><td>指令代码</td><td colspan="5">ASCII : FS ! n十进制 : 28 33 n十六进制 : 1C 21 n</td></tr><tr><td>功能描述</td><td colspan="5">设置汉字字符打印模式</td></tr><tr><td>参数范围</td><td colspan="5">0 ≤ n ≤ 255</td></tr><tr><td>默认值</td><td colspan="5">0</td></tr><tr><td>支持型号</td><td colspan="5">所有型号</td></tr><tr><td rowspan="14">注意事项</td><td colspan="5"></td></tr><tr><td>位</td><td>关/开</td><td>十六进制</td><td>十进制</td><td>ASB状态</td></tr><tr><td>0</td><td>-</td><td>-</td><td>-</td><td>未定义。</td></tr><tr><td>1</td><td>-</td><td>-</td><td>-</td><td>未定义。</td></tr><tr><td rowspan="2">2</td><td>关</td><td>00</td><td>0</td><td>禁止倍宽模式。</td></tr><tr><td>开</td><td>04</td><td>4</td><td>允许倍宽模式。</td></tr><tr><td rowspan="2">3</td><td>关</td><td>00</td><td>0</td><td>禁止倍高模式。</td></tr><tr><td>开</td><td>08</td><td>8</td><td>允许倍高模式。</td></tr><tr><td>4</td><td>-</td><td>-</td><td>-</td><td>未定义。</td></tr><tr><td>5</td><td>-</td><td>-</td><td>-</td><td>未定义。</td></tr><tr><td>6</td><td>-</td><td>-</td><td>-</td><td>未定义。</td></tr><tr><td rowspan="2">7</td><td>关</td><td>00</td><td>0</td><td>禁止下划线模式。</td></tr><tr><td>开</td><td>80</td><td>128</td><td>允许下划线模式。</td></tr><tr><td colspan="5">未选择汉字字符模式时,所有字符代码均作为 ASCII 码,每次一个字符进行处理。在同时设置了倍宽模式和倍高模式的情况下(包括右侧和左侧字符间距),将打印四倍大小的字符。</td></tr></table>

<table><tr><td></td><td>打印机可以给所有的字符加下划线(包括右侧和左侧字符间距),但是不能给HT命令所设置的空格,以及顺时针90°旋转字符加下划线。一行中的某些字符为倍高或更高的字符时,该行中所有的字符将沿基线对齐。可以使用GS!命令粗写汉字字符,最后收到的命令的设置有效。</td></tr><tr><td>使用示例</td><td>1b 401C 26B0 AE C9 CF D7 D4 BC BA 0D 0A1C 21 00B0 AE C9 CF D7 D4 BC BA 0D 0A1C 21 01B0 AE C9 CF D7 D4 BC BA 0D 0A1C 21 02B0 AE C9 CF D7 D4 BC BA 0D 0A1C 21 04B0 AE C9 CF D7 D4 BC BA 0D 0A1C 21 08B0 AE C9 CF D7 D4 BC BA 0D 0A1C 21 10B0 AE C9 CF D7 D4 BC BA 0D 0A1C 21 20B0 AE C9 CF D7 D4 BC BA 0D 0A1C 21 40B0 AE C9 CF D7 D4 BC BA 0D 0A1C 21 80B0 AE C9 CF D7 D4 BC BA 0D 0A1C 2E B0 AE C9 CF D7 D4 BC BA 0D 0A</td></tr></table>


取消汉字模式


<table><tr><td>指令名称</td><td>取消汉字模式</td></tr><tr><td>指令代码</td><td>ASCII : FS.
十进制 : 28 46
十六进制 : 1C 2E</td></tr><tr><td>功能描述</td><td>取消汉字模式</td></tr><tr><td>参数范围</td><td>无</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>未选择汉字字符模式时，所有字符代码均作为 ASCII 码，每次一个字符进行处理。</td></tr><tr><td>使用示例</td><td>无</td></tr></table>


定义用户自定义汉字


<table><tr><td>指令名称</td><td>定义用户自定义汉字</td></tr><tr><td>指令代码</td><td>ASCII : FS 2 c1 c2 d1...dk十进制 : 28 50 c1 c2 d1...dk十六进制 : 1C 32 c1 c2 d1...dk</td></tr><tr><td>功能描述</td><td>定义由c1，c2指定的汉字。</td></tr><tr><td>参数范围</td><td>c1 ,c2 代表定义字符的字符编码c1 = FEHAlH ≤ c2 ≤ FEH0 ≤ d ≤ 255k = 72</td></tr><tr><td>默认值</td><td>没有自定义汉字</td></tr><tr><td>支持型号</td><td>部分型号</td></tr><tr><td>注意事项</td><td>cl , c2 代表用户自定义汉字的编码，cl 指定第一个字节，c2 指定第二个字节。d 代表数据。1 表示打印一个点，0 表示不打印点。最多支持32个自定义汉字。自定义汉字字型与数据之间关系见下图:24点d1 d4 d7d70d71d72最高位最低位</td></tr><tr><td>使用示例</td><td>1C 32 FE A1
FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF AA</td></tr></table>


选择国际字符集


<table><tr><td>指令名称</td><td>选择国际字符集</td></tr><tr><td>指令代码</td><td>ASCII : ESC R n十进制 : 27 82 n十六进制 : 1B 52 n</td></tr><tr><td>功能描述</td><td>按照下表选择 n 的值设置国际字符集n 字符集0 美国1 法国2 德国3 英国4 丹麦I5 瑞典6 意大利7 西班牙I8 日本</td></tr></table>

<table><tr><td></td><td>9</td><td>挪威</td></tr><tr><td></td><td>10</td><td>丹麦Ⅱ</td></tr><tr><td></td><td>11</td><td>西班牙Ⅱ</td></tr><tr><td></td><td>12</td><td>拉丁美洲</td></tr><tr><td></td><td>13</td><td>韩国</td></tr><tr><td></td><td>14</td><td>斯洛文尼亚</td></tr><tr><td></td><td>15</td><td>中国</td></tr><tr><td>参数范围</td><td colspan="2">0≤n≤15</td></tr><tr><td>默认值</td><td colspan="2">0</td></tr><tr><td>支持型号</td><td colspan="2">所有型号</td></tr><tr><td>注意事项</td><td colspan="2"></td></tr><tr><td>使用示例</td><td colspan="2">1B 40 1B 52 0020 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F 30 31 32 33 34 35 36 37 3839 3A 3B 3C 3D 3E 3F 40 41 42 43 44 45 46 47 48 49 4A 4B 4C 4D 4E 4F 5051 52 53 54 55 56 57 58 59 60 6A 6B 6C 6D 6E 6F 70 71 72 73 74 75 76 78 797A 7B 7C 7D 7E 0D 0A</td></tr></table>

# 选择字符代码页

<table><tr><td>指令名称</td><td>选择字符代码页</td></tr><tr><td>指令代码</td><td>ASCII : ESC t n十进制 : 27 116 n十六进制 : 1B 74 n</td></tr><tr><td>功能描述</td><td>从字符代码页中选择nN 代码页0 CP437 [美国,欧洲标准]1 KataKana [片假名]2 CP850 [多语言]3 CP860 [葡萄牙]4 CP863 [加拿大-法语]5 CP865 [北欧]6 WCP1251 [斯拉夫语]7 CP866 斯拉夫28 MIK[斯拉夫/保加利亚]9 CP755 [东欧,拉脱维亚2]10 [伊朗,波斯]11 保留12 保留13 保留14 保留15 CP862 [希伯来]16 WCP1252 [拉丁语 1]17 WCP1253 [希腊]</td></tr><tr><td rowspan="31"></td><td>18 CP852 [拉丁语 2]</td></tr><tr><td>19 CP858 [多种语言拉丁语1+欧符]</td></tr><tr><td>20伊朗II[波斯语]</td></tr><tr><td>21 拉脱维亚</td></tr><tr><td>22 CP864 [阿拉伯语]</td></tr><tr><td>23 ISO-8859-1 [西欧]</td></tr><tr><td>24 CP737 [希腊]</td></tr><tr><td>25 WCP1257 [波罗的海]</td></tr><tr><td>26 泰文</td></tr><tr><td>27 CP720[阿拉伯语]</td></tr><tr><td>28 CP855</td></tr><tr><td>29 CP857[土耳其语]</td></tr><tr><td>30 WCP1250[中欧]</td></tr><tr><td>31 CP775</td></tr><tr><td>32 WCP1254[土耳其语]</td></tr><tr><td>33 WCP1255[希伯来语]</td></tr><tr><td>34 WCP1256[阿拉伯语]</td></tr><tr><td>35 WCP1258[越南语]</td></tr><tr><td>36 ISO-8859-2[拉丁语 2]</td></tr><tr><td>37 ISO-8859-3[拉丁语 3]</td></tr><tr><td>38 ISO-8859-4[波罗的语]</td></tr><tr><td>39 ISO-8859-5[斯拉夫语]</td></tr><tr><td>40 ISO-8859-6[阿拉伯语]</td></tr><tr><td>41 ISO-8859-7[希腊语]</td></tr><tr><td>42 ISO-8859-8[希伯来语]</td></tr><tr><td>43 ISO-8859-9[土耳其语]</td></tr><tr><td>44 ISO-8859-15[拉丁语 9]</td></tr><tr><td>45 [泰文 2]</td></tr><tr><td>46 CP856</td></tr><tr><td>47 Cp874</td></tr><tr><td>255 GBK2312</td></tr><tr><td>参数范围</td><td>0 ≤ n ≤ 255</td></tr><tr><td>默认值</td><td>0</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td></td></tr><tr><td>使用示例</td><td>1B 40 1C 2E 1B 74 0080 81 82 83 84 85 86 87 88 89 8A 8B 8C 8D 8E 8F 90 91 92 93 94 95 96 97 989A 9B 9C 9D 9E 9F A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 AA AB AC AD AE AFB0 B1 B2 B3 B4 B5 B6 B7 B8 B9 BA BB BC BD BE BF C0 C1 C2 C3 C4 C5C6 C7 C8 C9 CA CB CC CD CE CF D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 DA</td></tr><tr><td></td><td>DB DC DD DE DF E0 E1 E2 E3 E4 E5 E6 E7 E8 E9 EA EB EC ED EE EF F0
F1 F2 F3 F4 F5 F6 F7 F8 F9 FA FB FC FD FE FF 0D 0A</td></tr></table>


切换双字节编码


<table><tr><td>指令名称</td><td>切换双字节编码</td></tr><tr><td>指令代码</td><td>ASCII : ESC 9 n十进制 : 27 56 n十六进制 : 1B 39 n</td></tr><tr><td>功能描述</td><td>n对应的编码如下表:n 编码0 GBK1 UTF82 保留3 BIG54 SHIFT-JIS5 EUC-KR</td></tr><tr><td>参数范围</td><td>0 ≤ n ≤ 5</td></tr><tr><td>默认值</td><td>0</td></tr><tr><td>支持型号</td><td>部分型号</td></tr><tr><td>注意事项</td><td>使用前需先启用汉字模式(1C 26 命令可以启用)</td></tr><tr><td>使用示例</td><td>1B 401C 261B 39 01</td></tr></table>

# $\textcircled{3}$ 图形打印指令


图形垂直取模数据填充


<table><tr><td>指令名称</td><td>图形垂直取模数据填充</td></tr><tr><td>指令代码</td><td>ASCII : ESC * m Hl Hh [d]k
十进制 : 27 42 m Hl Hh [d]k
十六进制 : 1B 2A m Hl Hh [d]k</td></tr><tr><td>功能描述</td><td>打印纵向取模图像数据，参数意义如下：
m 为点图格式：
m 模式 水平比例 垂直比例
0 8 点单密度 ×2 ×3
1 8 点双密度 ×1 ×3
32 24 点单密度 ×2 ×1
33 24 点双密度 ×1 ×1
Hl、Hh 为水平方向点数（Hl+256×Hh）
[d]k 为点图数据
k 用于指示点图数据字节数，不参加传输</td></tr><tr><td>参数范围</td><td>XX58:m=0、1、32、331≤Hl+Hh×256≤3840≤d≤255k=Hl+Hh×256(当m=0、1)k=(Hl+Hh×256)×3(当m=32、33)XX80:m=0、1、32、331≤Hl+Hh×256≤5760≤d≤255k=Hl+Hh×256(当m=0、1)k=(Hl+Hh×256)×3(当m=32、33)</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>[d]k相应位为1则表示该点打印,相应位为0,则表示该点不打印图像水平方向超出打印区域的部分将被忽略点图数据与打印效果的关系如下:8点方式d1 d2 d3 高位低位点图数据(位图)24点方式d1 d4 d7 高位低位点图数据(位图)此指令只填充打印缓存,图像的打印要在接收到打印指令后才开始,图像打印完毕后打印缓存被清空若需要打印的图像高度较大,可以先拆分为若干条高度为8(m=0、1)或24(m=32、33)点的图像分别打印填充图形数据后,可以继续填充其它信息,以使图形与其它信息一同被打印填充点图后,一般使用ESC J(n=24)指令进行打印,也可以使用LF指令进行打印,但是LF指令会引发进纸操作(按行间距进纸),使得多行图像间断不连续,可以设置行间距为0,则不会过多进纸。(针式打印机起步会偏移,如果中间出现断线,请连续发送数据)</td></tr><tr><td>使用示例</td><td>1B 401b 2a 00 0C 00 FF FF FF FF FF FF FF FF FF0A</td></tr></table>

# 图片水平取模数据打印

指令名称 图片水平取模数据打印

<table><tr><td>指令代码</td><td colspan="4">ASCII : GS v0
十进制 : 29 118 48 m xL xH yL yH [d]k
十六进制 : 1D 76 30 m xL xH yL yH [d]k</td></tr><tr><td>功能描述</td><td colspan="4">打印横向取模图像数据,参数意义如下:
m 为位图方式:
m 模式 水平比例 垂直比例
0,48 正常 ×1 ×1
1,49 倍宽 ×2 ×1
2,50 倍高 ×1 ×2
3,51 倍宽倍高 ×2 ×2
xL、xH 为水平方向字节数 (xL+xH×256)
yL、yH 为竖直方向点数 (yL+yH×256)
[d]k 为点图数据
k 为点图数据字节数,k用于示意,不用传输</td></tr><tr><td>参数范围</td><td colspan="4">XX58:
0 ≤ m ≤ 3; 48 ≤ m ≤ 51
1 ≤ xL + xH×256 ≤ 48
0 ≤ yL ≤255, 0 ≤ yH ≤255
0 ≤ d ≤ 255
k = (Hl + Hh×256)×(yL + yH×256)
XX80:
0 ≤ m ≤ 3; 48 ≤ m ≤ 51
1 ≤ xL + xH×256 ≤ 72
0 ≤ yL ≤ 255, 0 ≤ yH ≤ 255
0 ≤ d ≤ 255
k = (Hl + Hh×256)×(yL + yH×256)</td></tr><tr><td>默认值</td><td colspan="4">无</td></tr><tr><td>支持型号</td><td colspan="4">所有型号</td></tr><tr><td>注意事项</td><td colspan="4">[d]k 相应位为1 则表示该点打印,相应位为0,则表示该点不打印
若图像水平字节数超出打印区域,超出部分将被忽略
此指令执行时按图像大小进纸,不受 ESC 2、ESC 3 的行间距设置影
响
此指令执行后,打印坐标复位到左边距位置处,图像内容被清空
位图数据与打印效果的关系如下:
d1 d2 ... ... d(x)
d(x+1) d(x+2) ... ... d(x×2)
| | ... ... | | MSB LSB MSB LSB MSB LSB MSB LSB
此指令带有打印功能,边传数据边打印,不需要再使用打印指令</td></tr><tr><td>使用示例</td><td colspan="4">1B 40</td></tr><tr><td></td><td colspan="4">1d 76 30 00 03 00 09 00
FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF</td></tr></table>


定义下传位图


<table><tr><td>指令名称</td><td colspan="4">定义下传位图</td></tr><tr><td>指令代码</td><td colspan="4">ASCII : GS * x y d1...d(x×y×8)
十进制 : 2942 x y d1 ...d(x×y×8)
十六进制 : 1D 2A x y d1...d(x×y×8)</td></tr><tr><td>功能描述</td><td colspan="4">用x和y指定点数以定义下传位图。
x指定水平方向点数为8*x。
y指定垂直方向点数为8*y。</td></tr><tr><td>参数范围</td><td colspan="4">1 ≤ x ≤ 255
1 ≤ y ≤ 48
x*y ≤ 1536
0 ≤ d ≤ 255</td></tr><tr><td>默认值</td><td colspan="4">无</td></tr><tr><td>支持型号</td><td colspan="4">所有型号</td></tr><tr><td rowspan="7">注意事项</td><td colspan="4">如果x*y超出了指定范围,则该命令被禁止。
d表示位图数据。数据(d)指定打印位为1,不打印位为0。
在下列情况下清除下传位图定义:
执行ESC@。
执行ESC&amp;。
打印机复位或关闭电源。
下传位图与打印数据之间的关系如下图所示</td></tr><tr><td colspan="4">x×8点</td></tr><tr><td>d1</td><td>d1</td><td>1</td><td>2+1</td></tr><tr><td>d2</td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>dy</td><td>dy</td><td>2</td><td>dx</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td>使用示例</td><td colspan="4">1B 40</td></tr><tr><td></td><td colspan="4">1D 2A 03 03
FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF BB</td></tr></table>


打印下传位图


<table><tr><td>指令名称</td><td colspan="2">打印下传位图</td></tr><tr><td>指令代码</td><td colspan="2">ASCII : GS / m十进制 : 2947 m十六进制 : 1D 2F m</td></tr><tr><td rowspan="6">功能描述</td><td colspan="2">用m所指定的模式打印下传位图</td></tr><tr><td>m</td><td>模式</td></tr><tr><td>0,48</td><td>普通</td></tr><tr><td>1,49</td><td>倍宽</td></tr><tr><td>2,50</td><td>倍高</td></tr><tr><td>3,51</td><td>倍宽、倍高</td></tr><tr><td>参数范围</td><td colspan="2">0 ≤ m ≤ 348 ≤ m ≤ 51</td></tr><tr><td>默认值</td><td colspan="2">无</td></tr><tr><td>支持型号</td><td colspan="2">所有型号</td></tr><tr><td>注意事项</td><td colspan="2">如果位图数据没有定义,则该命令被忽略。标准模式下,该命令仅当打印缓冲区中没有数据时有效。打印模式(粗体、重叠、下划线、字符大小或反白打印)下该命令无效,颠倒打印模式除外。如果将要打印的下传位图超过了打印区域,则超出的数据不打印。</td></tr><tr><td>使用示例</td><td colspan="2">无</td></tr></table>


定义NV 位图


<table><tr><td>指令名称</td><td>定义NV位图</td></tr><tr><td>指令代码</td><td>ASCII: FS q n [xL xH yL yH d1...dk]1...[xL xH yL yH d1...dk]n十进制: 28 113 n [xL xH yL yH d1...dk]1...[xL xH yL yH d1...dk]n十六进制: 1C 71 n [xL xH yL yH d1...dk]1...[xL xH yL yH d1...dk]n</td></tr><tr><td>功能描述</td><td>用特定的n值定义NV位图。n指定定义的NV位图的数量。xL, xH为定义中的NV位图指定水平方向的点数为(xL+xH*256)*8。yL, yH为定义中的NV位图指定垂直方向的点数为(yL+yH*256)*8。</td></tr><tr><td>参数范围</td><td>1 ≤ n ≤ 2550 ≤ xL ≤ 2550 ≤ xH ≤ 3(1 ≤ (xL+xH*256) ≤ 1023)0 ≤ yL ≤ 255)0 ≤ yH ≤ 1</td></tr><tr><td></td><td>(1 ≤ (yL+yH*256) ≤ 288)
0 ≤ d ≤ 255)
k = (xL+xH*256)*(yL+yH*256)*8
和计定义的数据区=64K字节</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>频繁地执行写命令可能会损坏NV存储器。因此,建议一天对NV存储器执行不超过10次写操作。
    在将一个图象放入NV存储器的过程之后,打印机执行一个硬件复位操作。因此用户自定义字符,下传位图应在完成该命令之后定义。打印机清除接收和打印缓冲区,并复位到接通电源时有效的模式。(不支持硬件复位接口)
    该命令取消所有已用该命令定义好的NV位图。
    从这条命令开始处理到完成硬件复位期间,不能执行机械操作(包括当盖板打开时初始化打印头位置用进纸按键进纸等)。
    在这条命令处理期间,当向用户NV存储器写数据时打印机为忙并停止接收数据。因此在执行这条命令期间禁止传送数据,包括实时命令。
    NV位图是一种定义在非易失性存储器中的位图。用FSq定义FSp打印。
    在标准模式,下该命令仅在一行的开始处理时才有效。
    该命令的7个字节&lt;FS yH&gt;正常处理后命令才有效。
    当数据量超过了xL,xH,yL,yH所定义范围的左侧容量,打印机将在所定义范围之外处理xL,xH,yL,yH所定义的范围。
    在第一组位图中,当xL,xH,yL,yH中任何参数超出了定义范围时,该命令就被禁止。
    在非第一组的一组位图中,当打印机遇到xL,xH,yL,yH超出定义范围的情况时,则停止处理该命令,且开始写入NV图象。此时,还没有定义的NV位图被禁止(未定义,)但以前定义的任何NV位图仍然有效.
    d表示定义数据.在数据(d)中,一个1位指定一个要打印的点而一个0位指定一个不打印的点。
    该命令将n定义为NV位图的数量。数量从位图01H开始顺序上升。因此第一个数据组[xL xH yL yH d1...dk]是NV位图01H,最后一个数据组[xL xH yL yH d1...dk]是NV位图n。总数与FSp命令设定的NV位图数量一致。
    一个NV位图的定义数据由[xL xH yL yH d1...dk]组成。因此,当仅有一个NV位图时n=1,打印机只处理数据组[xL xH yL yH d1...dk]一次。打印机使用NV存储器的([data:(xL+xH*256)*(yL+yH*256)*8]+[header:4])个字节。
    本打印机中的定义区域为192K字节(最大)。该命令可以定义几个位图,但是不能定义总数据容量[位图数据+头]超过192K字节的位图。
    即使设定了ASB,打印机在处理该命令期间也不传送ASB状态或执行状态检测。
    一旦定义一个NV位图,它就不能被执行ESC@命令,复位,断电所删除。
    该命令仅执行NV位图的定义,不执行打印。NV位图的打印是通过FSp命令执行的。</td></tr></table>

<table><tr><td colspan="3">图解:当xL=64,xH=0,yL=96,yH=0
(xL+xH×256)×8点=512点</td></tr><tr><td>d1</td><td>d97</td><td>d49057</td></tr><tr><td>d2</td><td colspan="2">最高有效位</td></tr><tr><td>d3</td><td colspan="2">最低有效位</td></tr><tr><td>d96</td><td colspan="2">d49152</td></tr><tr><td>使用示例</td><td colspan="2">1B 40
1C 71 01 03 00 03 00
FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF ff</td></tr></table>


打印NV 位图


<table><tr><td>指令名称</td><td colspan="2">打印NV位图</td></tr><tr><td>指令代码</td><td colspan="2">ASCII : FS p n m十进制 : 28 112 n m十六进制 : 1C 70 n m</td></tr><tr><td rowspan="6">功能描述</td><td colspan="2">用m指定的模式打印NV位图n</td></tr><tr><td>m</td><td>模式</td></tr><tr><td>0,48</td><td>普通</td></tr><tr><td>1,49</td><td>倍宽</td></tr><tr><td>2,50</td><td>倍高</td></tr><tr><td>3,51</td><td>倍宽、倍高</td></tr><tr><td>参数范围</td><td colspan="2">0 ≤ m ≤ 348 ≤ m ≤ 511 ≤ n ≤ 255</td></tr><tr><td>默认值</td><td colspan="2">无</td></tr><tr><td>支持型号</td><td colspan="2">所有型号</td></tr><tr><td>注意事项</td><td colspan="2">n是NV位图的数量(用FS q命令定义)。m指定位图模式。NV位图是一种定义在非易失性存储器中的位图。用FS q定义FS p打印当指定的NV位图不存在时该命令无效。在标准模式下,仅当打印缓冲区中没有数据时,该命令才有效。该命令不受打印模式影响(粗体打印、重叠、下划线、字符大小、反白打印或字符90),旋转等颠倒打印模式除外。如果要打印的下传位图超过一行,则超出的数据不打印。在普通和倍宽模式下,该命令进纸n点(n为NV位图高度),在倍高和四倍大小模式下(该命令进纸2n点,n为NV位图高度),与ESC2或ESC3设定的行间距无关。打印位图之后,该命令将打印位置设定在一行的开始,并对后续数据按普通数据处理</td></tr><tr><td>使用示例</td><td colspan="2">无</td></tr></table>


打印光栅位图


<table><tr><td>指令名称</td><td colspan="4"></td></tr><tr><td>指令代码</td><td colspan="4">ASCII : GS v 0 m xL xH yL yH d1...dk十进制 : 29 118 48 m xL xH yL yH d1...dk十六进制 : 1D 76 30 m xL xH yL yH d1...dk</td></tr><tr><td rowspan="5">功能描述</td><td colspan="4">打印光栅位图,由m值选择光栅位图模式:</td></tr><tr><td>m</td><td>模式</td><td>纵向分辨率(DPI)</td><td>横向分辨率(DPI)</td></tr><tr><td>0,48</td><td>正常</td><td>200</td><td>200</td></tr><tr><td>1,49</td><td>倍宽</td><td>200</td><td>100</td></tr><tr><td>2,50</td><td>倍高</td><td>100</td><td>200</td></tr></table>

<table><tr><td></td><td>3,51</td><td colspan="2">倍宽，倍高</td><td colspan="3">100</td><td colspan="2">100</td></tr><tr><td>参数范围</td><td colspan="8">0 ≤ m ≤ 3 或 48 ≤ m ≤ 510 ≤ xL ≤ 2550 ≤ xH ≤ 2550 ≤ yL ≤ 2550 ≤ d ≤ 255k = (xL + xH * 256) * (yL + yH * 256) (k≠0)</td></tr><tr><td>默认值</td><td colspan="8">无</td></tr><tr><td>支持型号</td><td colspan="8">所有型号</td></tr><tr><td>注意事项</td><td colspan="8">xL、xH 表示水平方向位图字节数 (xL+xH*256)yL、yH 表示垂直方向位图点数 (yL+yH*256)在标准模式下，只有打印机缓冲区无数据时该命令才有效。字符放大、加粗、双重打印、倒置打印、下划线、黑白反显等打印模式对该命令无效。位图超出打印区域的部分不打印。ESC对光栅位图有效。宏定义的过程中，该命令将停止宏定义而执行该命令。该命令不作为宏定义的一部分。d代表位图数据。每个字节的相应位为1表示打印该点，为0不打印该点。</td></tr><tr><td>使用示例</td><td colspan="8">当xL+xH*256=64(xL+xH×256)×8点=512点→16566667676666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666最高位最低位</td></tr></table>

# 水平位置打印行线段（曲线打印命令）

<table><tr><td>指令名称</td><td>水平位置打印行线段（曲线打印命令）</td></tr><tr><td>指令代码</td><td>ASCII : GS &#x27;n x1sL x1eH x1eL x1eH ...xnsL xnsH xneL xneH
十进制 : 1D 27 n x1sL x1eH x1eL x1eH ...xnsL xnsH xneL xneH
十六进制 : 29 39 n x1sL x1eH x1eL x1eH ...xnsL xnsH xneL xneH</td></tr><tr><td>功能描述</td><td>打印放大图如下所示：每个水平曲线段可以视为由段长度为1的这些点组成。打印n行水平线段的，连续使用该命令就可以打印出所需的曲线。</td></tr></table>

![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-01/9f4f97fa-ad5f-4dcb-b225-af1e0ead5221/c8c3ccb5baeb0c61d94025943e8b6b565b51e4862b2dd17f59117bc6c001ca69.jpg)


xksL: K 线起点低阶的水平坐标；

$\mathrm { x k s H } : \mathrm { K }$ 线起点高阶的水平坐标；

xkeL: K 线结束点低阶的水平坐标；

$\mathrm { x k e H } : \mathrm { K }$ 线结束点高阶的水平坐标；

坐标开始位置通常是打印区域的左边。最小坐标坐标为（0,0），最大横坐标值 383，xkeL+xkeH*256

行数据可以不按规定范围内顺序排列；

Char SendStr[8]; 

Char SendStr2[16]; 

Float i; 

Short y1,y2,y1s,y2s; 

//打印 Y 轴（一条线）

SendStr[0]=0x1D; 

SendStr[1]=0x27; 

SendStr[2]=1； // 一行

SendStr[3]=30 

SendStr[4] $\scriptstyle = 0$ ; //开始点

SendStr[5]=104; 

SendStr[6]=1; //结束点

PreSendData(SendStr,7); 

//Print curve 

<table><tr><td></td><td>SendStr[0]=0x1D;SendStr[1]=0x27;SendStr[2]=3; //Three lines:X-axis,sin and cos function curve 三条线:X轴, sin和cos函数SendStr[3]=180; SendStr[4]=0; //X轴位置SendStr[5]=180; SendStr[6]=0;for(i=1;i&lt;1200;i++){y1=sin(i/180*3.1416)*(380-30)/2+180; //计算sin函数坐标y2=cos(i/180*3.1416)*(380-30)/2+180; //计算cos函数坐标If(i==1){y1s=y1;y2s=y2;}PreSendData(SendStr,7);If(y1s&lt;y1) {PreSendData(&amp;y1s,2); //sin函数在该行的起始点PreSendData(&amp;y1,2); //sin函数在该行的结束点}Else{PreSendData(&amp;y1,2); //sin函数在该行的起始点PreSendData(&amp;y1s,2); //sin函数在该行的结束点}If(y2s&lt;y2) {PreSendData(&amp;y2s,2); //cos函数在该行的起始点PreSendData(&amp;y2,2); //cos函数在该行的结束点}Else{PreSendData(&amp;y2,2); //cos函数在该行的起始点PreSendData(&amp;y2s,2); //cos函数在该行的结束点}y1s=y1; //当打印进入下一行，sin函数曲线起点横坐标y2s=y2; //当打印进入下一行，cos函数曲线起点横坐标}</td></tr><tr><td>参数范围</td><td>0≤n≤8</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>便携打印机</td></tr><tr><td>注意事项</td><td>打印一个点时，则xkeL=xksL,xkeH=xksH</td></tr><tr><td>使用示例</td><td>1d 27 01 00 00 00 001d 27 01 00 00 1f00</td></tr><tr><td></td><td>1d 27 01 20 00 2c 00 1d 27 01 2d 00 3a 00</td></tr><tr><td></td><td>1d 27 01 3b 00 44 00 1d 27 01 45 00 4c 00</td></tr><tr><td></td><td>1d 27 01 4d 00 54 00 1d 27 01 55 00 5c 00</td></tr><tr><td></td><td>1d 27 01 5d 00 63 00 1d 27 01 64 00 6a 00</td></tr><tr><td></td><td>1d 27 01 6b 00 71 00 1d 27 01 72 00 77 00</td></tr><tr><td></td><td>1d 27 01 78 00 7d 00 1d 27 01 7e 00 84 00</td></tr><tr><td></td><td>1d 27 01 85 00 8a 00 1d 27 01 8b 00 91 00</td></tr><tr><td></td><td>1d 27 01 92 00 97 00 1d 27 01 98 00 9d 00</td></tr><tr><td></td><td>1d 27 01 9e 00 a3 00 1d 27 01 a4 00 a9 00</td></tr><tr><td></td><td>1d 27 01 aa 00 af 00 1d 27 01 b0 00 b4 00</td></tr><tr><td></td><td>1d 27 01 b5 00 b9 00 1d 27 01 ba 00 bf 00</td></tr><tr><td></td><td>1d 27 01 c0 00 c4 00 1d 27 01 c5 00 c9 00</td></tr><tr><td></td><td>1d 27 01 ca 00 cf 00 1d 27 01 d0 00 d4 00</td></tr><tr><td></td><td>1d 27 01 d5 00 d8 00 1d 27 01 d9 00 dc 00</td></tr><tr><td></td><td>1d 27 01 dd 00 df 00 1d 27 01 e0 00 e3 00</td></tr><tr><td></td><td>1d 27 01 e4 00 e6 00 1d 27 01 e7 00 e9 00</td></tr><tr><td></td><td>1d 27 01 ea 00 ec 00 1d 27 01 ed 00 ef 00</td></tr><tr><td></td><td>1d 27 01 f0 00 f1 00 1d 27 01 f2 00 f3 00</td></tr><tr><td></td><td>1d 27 01 f4 00 f5 00 1d 27 01 f6 00 f7 00</td></tr><tr><td></td><td>1d 27 01 f8 00 f8 00 1d 27 01 f9 00 fa 00</td></tr><tr><td></td><td>1d 27 01 fb 00 fb 00 1d 27 01 fc 00 fd 00</td></tr><tr><td></td><td>1d 27 01 fe 00 fe 00 1d 27 01 ff 00 ff 00</td></tr><tr><td></td><td>1d 27 01 00 01 00 01 1d 27 01 01 01 01</td></tr><tr><td></td><td>1d 27 01 02 01 02 01 1d 27 01 03 01 03 01</td></tr><tr><td></td><td>1d 27 01 04 01 04 01 1d 27 01 05 01 05 01</td></tr><tr><td></td><td>1d 27 01 06 01 06 01 1d 27 01 06 01 06 01</td></tr><tr><td></td><td>1d 27 01 07 01 07 01 1d 27 01 07 01 07 01</td></tr><tr><td></td><td>1d 27 01 07 01 07 01 1d 27 01 07 01 07 01</td></tr><tr><td></td><td>1d 27 01 07 01 07 01 1d 27 01 06 01 06 01</td></tr><tr><td></td><td>1d 27 01 06 01 06 01 1d 27 01 05 01 05 01</td></tr><tr><td></td><td>1d 27 01 04 01 04 01 1d 27 01 04 01 04 01</td></tr><tr><td></td><td>1d 27 01 03 01 03 01 1d 27 01 02 01 02 01</td></tr><tr><td></td><td>1d 27 01 00 01 00 01 1d 27 01 ff 00 ff 00</td></tr><tr><td></td><td>1d 27 01 fe 00 fe 00 1d 27 01 fc 00 fd 00</td></tr><tr><td></td><td>1d 27 01 f9 00 fa 00 1d 27 01 f8 00 f8 00</td></tr><tr><td></td><td>1d 27 01 f6 00 f7 00 1d 27 01 f4 00 f5 00</td></tr><tr><td></td><td>1d 27 01 f2 00 f3 00 1d 27 01 f0 00 f1 00</td></tr><tr><td></td><td>1d 27 01 ed 00 ef 00 1d 27 01 ea 00 ec 00</td></tr><tr><td></td><td>1d 27 01 e7 00 e9 00 1d 27 01 e4 00 e6 00</td></tr><tr><td></td><td>1d 27 01 e0 00 e3 00 1d 27 01 dd 00 df 00</td></tr><tr><td></td><td>1d 27 01 d9 00 dc 00 1d 27 01 d5 00 d8 00</td></tr><tr><td></td><td>1d 27 01 d0 00 d4 00 1d 27 01 ca 00 cf 00</td></tr><tr><td></td><td>1d 27 01 c5 00 c9 00 1d 27 01 c0 00 c4 00</td></tr><tr><td></td><td>1d 27 01 ba 00 bf 00 1d 27 01 b5 00 b9 00</td></tr><tr><td></td><td>1d 27 01 b0 00 b4 00 1d 27 01 aa 00 af 00</td></tr><tr><td></td><td>1d 27 01 a4 00 a9 00 1d 27 01 9e 00 a3 00</td></tr><tr><td></td><td>1d 27 01 98 00 9d 00 1d 27 01 92 00 97 00</td></tr><tr><td></td><td>1d 27 01 8b 00 91 00 1d 27 01 85 00 8a 00</td></tr><tr><td></td><td>1d 27 01 7e 00 84 00 1d 27 01 78 00 7d 00</td></tr><tr><td></td><td>1d 27 01 72 00 77 00 1d 27 01 6b 00 71 00</td></tr><tr><td></td><td>1d 27 01 64 00 6a 00 1d 27 01 5d 00 63 00</td></tr><tr><td></td><td>1d 27 01 55 00 5c 00 1d 27 01 4d 00 54 00</td></tr><tr><td></td><td>1d 27 01 45 00 4c 00 1d 27 01 3b 00 44 00</td></tr><tr><td></td><td>1d 27 01 2d 00 3a 00 1d 27 01 20 00 2c 00</td></tr><tr><td></td><td>1d 27 01 10 00 1f 00 1d 27 01 01 00 of 00</td></tr><tr><td></td><td>1d 27 01 00 00 00 00 1d 27 01 00 00 00 00</td></tr><tr><td></td><td>1d 27 01 01 00 of 00 1d 27 01 10 00 1f 00</td></tr><tr><td></td><td>1d 27 01 20 00 2c 00 1d 27 01 2d 00 3a 00</td></tr><tr><td></td><td>1d 27 01 3b 00 44 00 1d 27 01 45 00 4c 00</td></tr><tr><td></td><td>1d 27 01 4d 00 54 00 1d 27 01 55 00 5c 00</td></tr><tr><td></td><td>1d 27 01 5d 00 63 00 1d 27 01 64 00 6a 00</td></tr><tr><td></td><td>1d 27 01 6b 00 71 00 1d 27 01 72 00 77 00</td></tr><tr><td></td><td>1d 27 01 78 00 7d 00 1d 27 01 7e 00 84 00</td></tr><tr><td></td><td>1d 27 01 85 00 8a 00 1d 27 01 8b 00 91 00</td></tr><tr><td></td><td>1d 27 01 92 00 97 00 1d 27 01 98 00 9d 00</td></tr><tr><td></td><td>1d 27 01 9e 00 a3 00 1d 27 01 a4 00 a9 00</td></tr><tr><td></td><td>1d 27 01 aa 00 af 00 1d 27 01 b0 00 b4 00</td></tr><tr><td></td><td>1d 27 01 b5 00 b9 00 1d 27 01 ba 00 bf 00</td></tr><tr><td></td><td>1d 27 01 c0 00 c4 00 1d 27 01 c5 00 c9 00</td></tr><tr><td></td><td>1d 27 01 ca 00 cf 00 1d 27 01 d0 00 d4 00</td></tr><tr><td></td><td>1d 27 01 d5 00 d8 00 1d 27 01 d9 00 dc 00</td></tr><tr><td></td><td>1d 27 01 dd 00 df 00 1d 27 01 e0 00 e3 00</td></tr><tr><td></td><td>1d 27 01 e4 00 e6 00 1d 27 01 e7 00 e9 00</td></tr><tr><td></td><td>1d 27 01 ea 00 ec 00 1d 27 01 ed 00 ef 00</td></tr><tr><td></td><td>1d 27 01 f0 00 f1 00 1d 27 01 f2 00 f3 00</td></tr><tr><td></td><td>1d 27 01 f4 00 f5 00 1d 27 01 f6 00 f7 00</td></tr><tr><td></td><td>1d 27 01 f8 00 f8 00 1d 27 01 f9 00 fa 00</td></tr><tr><td></td><td>1d 27 01 fb 00 fb 00 1d 27 01 fc 00 fd 00</td></tr><tr><td></td><td>1d 27 01 fe 00 fe 00 1d 27 01 ff 00 ff 00</td></tr><tr><td></td><td>1d 27 01 00 01 00 01 1d 27 01 01 01 01</td></tr><tr><td></td><td>1d 27 01 02 01 02 01 1d 27 01 03 01 03 01</td></tr><tr><td></td><td>1d 27 01 04 01 04 01 1d 27 01 05 01 05 01</td></tr><tr><td></td><td>1d 27 01 06 01 06 01 1d 27 01 06 01 06 01</td></tr><tr><td></td><td>1d 27 01 07 01 07 01 1d 27 01 07 01 07 01</td></tr><tr><td></td><td>1d 27 01 07 01 07 01 1d 27 01 07 01 07 01</td></tr><tr><td></td><td>1d 27 01 07 01 07 01 1d 27 01 06 01 06 01</td></tr><tr><td></td><td>1d 27 01 06 01 06 01 1d 27 01 05 01 05 01</td></tr><tr><td></td><td>1d 27 01 04 01 04 01 1d 27 01 04 01 04 01</td></tr><tr><td></td><td>1d 27 01 03 01 03 01 1d 27 01 02 01 02 01</td></tr><tr><td></td><td>1d 27 01 00 01 00 01 1d 27 01 ff 00 ff 00</td></tr><tr><td></td><td>1d 27 01 fe 00 fe 00 1d 27 01 fc 00 fd 00</td></tr><tr><td></td><td>1d 27 01 f9 00 fa 00 1d 27 01 f8 00 f8 00</td></tr><tr><td></td><td>1d 27 01 f6 00 f7 00 1d 27 01 f4 00 f5 00</td></tr><tr><td></td><td>1d 27 01 f2 00 f3 00 1d 27 01 f0 00 f1 00</td></tr><tr><td></td><td>1d 27 01 ed 00 ef 00 1d 27 01 ea 00 ec 00</td></tr><tr><td></td><td>1d 27 01 e7 00 e9 00 1d 27 01 e4 00 e6 00</td></tr><tr><td></td><td>1d 27 01 e0 00 e3 00 1d 27 01 dd 00 df 00</td></tr><tr><td></td><td>1d 27 01 d9 00 dc 00 1d 27 01 d5 00 d8 00</td></tr><tr><td></td><td>1d 27 01 d0 00 d4 00 1d 27 01 ca 00 cf 00</td></tr><tr><td></td><td>1d 27 01 c5 00 c9 00 1d 27 01 c0 00 c4 00</td></tr><tr><td></td><td>1d 27 01 ba 00 bf 00 1d 27 01 b5 00 b9 00</td></tr><tr><td></td><td>1d 27 01 b0 00 b4 00 1d 27 01 aa 00 af 00</td></tr><tr><td></td><td>1d 27 01 a4 00 a9 00 1d 27 01 9e 00 a3 00</td></tr><tr><td></td><td>1d 27 01 98 00 9d 00 1d 27 01 92 00 97 00</td></tr><tr><td></td><td>1d 27 01 8b 00 91 00 1d 27 01 85 00 8a 00</td></tr><tr><td></td><td>1d 27 01 7e 00 84 00 1d 27 01 78 00 7d 00</td></tr><tr><td></td><td>1d 27 01 72 00 77 00 1d 27 01 6b 00 71 00</td></tr><tr><td></td><td>1d 27 01 64 00 6a 00 1d 27 01 5d 00 63 00</td></tr><tr><td></td><td>1d 27 01 55 00 5c 00 1d 27 01 4d 00 54 00</td></tr><tr><td></td><td>1d 27 01 45 00 4c 00 1d 27 01 3b 00 44 00</td></tr><tr><td></td><td>1d 27 01 2d 00 3a 00 1d 27 01 20 00 2c 00</td></tr><tr><td></td><td>1d 27 01 10 00 1f 00 1d 27 01 01 00 0f 00</td></tr><tr><td></td><td>1d 27 01 00 00 00 00</td></tr></table>

# $\textcircled{4}$ 制表指令


水平制表


<table><tr><td>指令名称</td><td>水平制表</td></tr><tr><td>指令代码</td><td>ASCII : HT
十进制 : 9
十六进制 : 09</td></tr><tr><td>功能描述</td><td>移动打印位置至下一个制表位置</td></tr><tr><td>参数范围</td><td>无</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>制表位置由 ESC D 设定
若制表位置未设置（默认无水平制表位置），此指令将视为 LF 指令
若制表位置超出打印区域，坐标将移至下一行的起始位置（视本行数据已满，打印并换行）</td></tr><tr><td>使用示例</td><td>无</td></tr></table>


设置水平制表位置


<table><tr><td>指令名称</td><td></td></tr><tr><td>指令代码</td><td>ASCII: ESC D [d]k NUL十进制: 27 68 [d]k 0十六进制: 1B 44 [d]k 00</td></tr><tr><td>功能描述</td><td>设置水平制表位置,参数意义如下:d1 ... dk: 水平制表位置,以8点为单位,NULL为结束符</td></tr><tr><td>参数范围</td><td>XX58: 1 ≤ d ≤ 46 (d1 &lt; d2 &lt; ...... dk, 1 ≤ k ≤ 16)XX80: 1 ≤ d ≤ 70 (d1 &lt; d2 &lt; ...... dk, 1 ≤ k ≤ 16)</td></tr><tr><td>默认值</td><td>[d]k = 0(默认无水平制表位置)</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>制表位置示意如下:设置制表位置d1和d2 最多支持16个制表位置的设定使用此指令将取消以往制表位置的设置k用于示意之用,不用传输传输[d]k遇到NULL时,视为结束若dk小于或等于dk-1,视为结束,剩余数据视为普通数据处理制表位置可由HT切换当左边距改变后,制表位置同时改变当ESC@、打印机复位、断电后,本指令的设置失效</td></tr><tr><td>使用示例</td><td>1B 44 18 1E 0046 4F 44 09 50 52 49 43 45 09 49 44 0D0A0D0A1B 44 18 1E 0044 45 43 41 46 31 36 09 33 30 09 31 0D0A</td></tr></table>

# $\textcircled{5}$ 一维条码打印指令


设置一维条码可读字符（HRI）打印位置


<table><tr><td>指令名称</td><td>设置条码可读字符（HRI）打印位置</td></tr><tr><td>指令代码</td><td>ASCII : GSH n
十进制 : 2972 n
十六进制 : 1D48 n</td></tr><tr><td>功能描述</td><td>设置条码可读字符（HRI）打印位置，n参数意义如下：</td></tr><tr><td></td><td>n     打印位置
0, 48   不打印
1, 49   条码的上方
2, 50   条码的下方
3, 51   条码的上方和下方</td></tr><tr><td>参数范围</td><td>0 ≤ n ≤ 3 或 48 ≤ n ≤ 51</td></tr><tr><td>默认值</td><td>n = 0</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>当 ESC @、打印机复位、断电后，本指令的设置失效</td></tr><tr><td>使用示例</td><td>无</td></tr></table>

# 设置一维条码高度

<table><tr><td>指令名称</td><td>设置一维条码高度</td></tr><tr><td>指令代码</td><td>ASCII : GShn十进制 : 29104n十六进制 : 1D68n</td></tr><tr><td>功能描述</td><td>设置条码的高度为n点,参数n意义如下:高度为50高度为100</td></tr><tr><td>参数范围</td><td>1≤n≤255</td></tr><tr><td>默认值</td><td>n=64</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>当ESC@、打印机复位、断电后,本指令的设置失效</td></tr><tr><td>使用示例</td><td>无</td></tr></table>

# 设置一维条码宽度

<table><tr><td>指令名称</td><td>设置一维条码宽度</td></tr><tr><td>指令代码</td><td>ASCII : GS w n
十进制 : 29 119 n
十六进制 : 1D 77 n</td></tr><tr><td>功能描述</td><td>设置条码单元为 n 点, 参数 n 意义如下:宽度为 3宽度为 4</td></tr><tr><td>参数范围</td><td>1 ≤ n ≤ 6</td></tr><tr><td>默认值</td><td>n = 2</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>当 ESC @、打印机复位、断电后，本指令的设置失效</td></tr><tr><td>使用示例</td><td>无</td></tr></table>


打印一维条码


<table><tr><td>指令名称</td><td colspan="6"></td></tr><tr><td>指令代码</td><td colspan="6">(A) ASCII: GS km [d]k NUL十进制: 29 107 m [d]k NUL十六进制: 1D 6B m [d]k NUL(B) ASCII: GS km n [d]k十进制: 29 107 mn [d]k十六进制: 1D 6B mn [d]k</td></tr><tr><td rowspan="10">功能描述</td><td colspan="6">打印一维条码,各参数意义如下:m为编码方式n为编码数据长度,仅(B)方式使用,(A)与(B)指令的区别在于(A)的数据段用 NULL 字符结束,而(B)用指示数据的长度[d]k为条码数据k为条码数据的长度,用于示意,不用传输各参数之间的关系如下表所示:(指令A)</td></tr><tr><td rowspan="2">m</td><td rowspan="2">编码系统</td><td colspan="4">条码数据(SP表示空格)</td></tr><tr><td>数据长度</td><td>k</td><td>字符集</td><td>数据(d)</td></tr><tr><td>0</td><td>UPC-A</td><td>固定</td><td>k=11,12</td><td>0~9</td><td>48≤d≤57</td></tr><tr><td>1</td><td>UPC-E</td><td>固定</td><td>6≤k≤8,k=11,12</td><td>0~9</td><td>48≤d≤57[当k=7,8,11,12,d1=48]</td></tr><tr><td>2</td><td>JAN13(EAN13)</td><td>固定</td><td>k=12,13</td><td>0~9</td><td>48≤d≤57</td></tr><tr><td>3</td><td>JAN8(EAN8)</td><td>固定</td><td>k=7,8</td><td>0~9</td><td>48≤d≤57</td></tr><tr><td>4</td><td>CODE39</td><td>可变</td><td>1≤k≤255</td><td>0~9,A~ZSP,$,%+, -,.,/</td><td>48≤d≤57,65≤d≤90,d=32,36,37,42,43,45,46,47</td></tr><tr><td>5</td><td>ITF(Interleaved 2 of 5)</td><td>可变</td><td>2≤k≤255(偶数)</td><td>0~9</td><td>48≤d≤57</td></tr><tr><td>6</td><td>CODABAR(NW-7)</td><td>可变</td><td>1≤k</td><td>0~9,A~D,a-d$,+,-,.,/,:</td><td>48≤d≤57,65≤d≤68,97≤d≤100,</td></tr></table>

<table><tr><td></td><td></td><td></td><td></td><td></td><td>d = 36, 43, 45, 46, 47, 58 (65≤d1≤68, 65≤dk≤68, 97≤d1≤100, 97≤dk≤100)</td></tr></table>


(指令 B)


<table><tr><td rowspan="2">m</td><td rowspan="2">编码系统</td><td colspan="4">条码数据(SP表示空格)</td></tr><tr><td>数据长度</td><td>n</td><td>字符集</td><td>数据(d)</td></tr><tr><td>65</td><td>UPC-A</td><td>固定</td><td>n=11,12</td><td>0~9</td><td>48≤d≤57</td></tr><tr><td>66</td><td>UPC-E</td><td>固定</td><td>6≤n≤8,n=11,12</td><td>0~9</td><td>48≤d≤57[当n=7,8,11,12,d1=48]</td></tr><tr><td>67</td><td>JAN13(EAN13)</td><td>固定</td><td>n=12,13</td><td>0~9</td><td>48≤d≤57</td></tr><tr><td>68</td><td>JAN8(EAN8)</td><td>固定</td><td>n=7,8</td><td>0~9</td><td>48≤d≤57</td></tr><tr><td>69</td><td>CODE39</td><td>可变</td><td>1≤n≤255</td><td>0~9,A~ZSP, $,%+, -,/</td><td>48≤d≤57,65≤d≤90,d=32,36,37,42,43,45,46,47</td></tr><tr><td>70</td><td>ITF(Interleaved 2 of 5)</td><td>可变</td><td>1≤n≤255(偶数)</td><td>0~9</td><td>48≤d≤57</td></tr><tr><td>71</td><td>CODABAR(NW-7)</td><td>可变</td><td>1≤n≤255</td><td>0~9,A~D,a~d$,+,-,.,/,:</td><td>48≤d≤57,65≤d≤68,97≤d≤100,d=36,43,45,46,47,58(65≤d1≤68,65≤dk≤68,97≤d1≤100,97≤dk≤100)</td></tr><tr><td>72</td><td>CODE93</td><td>可变</td><td>1≤n≤255</td><td>00H~7FH</td><td>0≤d≤127</td></tr><tr><td>73</td><td>CODE128</td><td>可变</td><td>2≤n≤255</td><td>00H~7FH</td><td>0≤d≤127</td></tr><tr><td>74</td><td>UCC/EAN128</td><td>可变</td><td>2≤n≤255</td><td>00H~7FH C1H~C4H(FNC)</td><td>0≤d≤127 d=193,194,195,196</td></tr></table>

<table><tr><td>参数范围</td><td colspan="14">(A)0≤m≤6(B)65≤m≤74</td><td></td><td></td></tr><tr><td>默认值</td><td colspan="14">无</td><td></td><td></td></tr><tr><td>支持型号</td><td colspan="14">所有型号</td><td></td><td></td></tr><tr><td rowspan="10">注意事项</td><td colspan="14">若条码宽度超出可打印区域,打印机不执行条码打印此指令执行时按需要进纸,不受ESC2、ESC3行间距设置影响也不影响行间距设置此指令不受ESC!字符样式设置影响此指令执行后,打印位置恢复至打印起始位置处m参数0~6(A)和65~71(B)选择相同的编码系统,打印效果相同m参数0~6(A)时,条码数据以NULL结束m参数65~74(B)时,条码数据以n表示数据长度k用于示意,不需要传输打印UPCA(m=0或65)时,需要注意:不论输入数据长度是11还是12,校验位自动插入或纠错起始符、中间分隔符、结束符自动插入打印UPCE(m=1或66)时,需要注意:当数据长度为6时,系统字符(NSC)0自动插入当数据长度为7、8、11和12时,第一位系统字符(NSC)d1必须为0不论输入数据长度是6、7、8、11还是12,校验位自动插入或纠错不论输入数据长度是6、7、8、11还是12,条码可读字符(HRI)只显示6位数据,不包含系统字符(NSC)和校验码;传输数据与打印数据转换关系如下:</td><td></td><td></td></tr><tr><td colspan="10">传输的数据</td><td colspan="4">打印的数据</td><td></td><td></td></tr><tr><td>d2</td><td>d3</td><td>d4</td><td>d5</td><td>d6</td><td>d7</td><td>d8</td><td>d9</td><td>d10</td><td>d11</td><td>d1</td><td>d2</td><td>d3</td><td>d4</td><td>d5</td><td>d6</td></tr><tr><td>0~9</td><td>0~9</td><td>0</td><td>0</td><td>0</td><td>-</td><td>-</td><td>0~9</td><td>0~9</td><td>0~9</td><td>d2</td><td>d3</td><td>d9</td><td>d10</td><td>d11</td><td>0</td></tr><tr><td>0~9</td><td>0~9</td><td>1</td><td>0</td><td>0</td><td>-</td><td>-</td><td>0~9</td><td>0~9</td><td>0~9</td><td>d2</td><td>d3</td><td>d9</td><td>d10</td><td>d11</td><td>1</td></tr><tr><td>0~9</td><td>0~9</td><td>2</td><td>0</td><td>0</td><td>-</td><td>-</td><td>0~9</td><td>0~9</td><td>0~9</td><td>d2</td><td>d3</td><td>d9</td><td>d10</td><td>d11</td><td>2</td></tr><tr><td>0~9</td><td>0~9</td><td>3~9</td><td>0</td><td>0</td><td>-</td><td>-</td><td>-</td><td>0~9</td><td>0~9</td><td>d2</td><td>d3</td><td>d4</td><td>d10</td><td>d11</td><td>3</td></tr><tr><td>0~9</td><td>0~9</td><td>0~9</td><td>1~9</td><td>0</td><td>-</td><td>-</td><td>-</td><td>-</td><td>0~9</td><td>d2</td><td>d3</td><td>d4</td><td>d5</td><td>d11</td><td>4</td></tr><tr><td>0~9</td><td>0~9</td><td>0~9</td><td>0~9</td><td>1~9</td><td>-</td><td>-</td><td>-</td><td>-</td><td>5~9</td><td>d2</td><td>d3</td><td>d4</td><td>d5</td><td>d6</td><td>d11</td></tr><tr><td colspan="15">当d6为1~9时,应保证d7,d8,d9,d10为0,d11为5~9起始符、结束符自动插入打印EAN13(m=2或67)时,需要注意:不论输入数据长度是12还是13,校验位自动插入或纠错起始符、中间分隔符、结束符自动插入打印EAN8(m=3或68)时,需要注意:不论输入数据长度是7还是8,校验位自动插入或纠错起始符、中间分隔符、结束符自动插入打印CODE39(m=4或69)时,需要注意:</td><td></td></tr></table>

当 d1 或 dn 不为起始符/结束符“*”时，编码器自动插入“*”

当数据中间遇到“*”时，编码器视其为结束符，其余数据视为普通数据处理；

校验位不会自动计算和添加

打印 ITF25（ $\mathbf { m } = 5$ 或 70）时，需要注意：

起始符和结束符自动插入

校验位不会自动计算和添加

打印 CODABAR（NW-7）（ $\mathrm { m } = 6$ 或 71）时，需要注意：

起始符和结束符不会自动插入，需要用户手动添加，范围为“A”~“D”或“a”~“d”

校验位不会自动计算和添加

打印 CODE93（ $\mathrm { m } = 7 2$ ）时，需要注意：

起始符和结束符自动插入

两个校验码自动计算并插入

当设置条码可读字符（HRI）打印时，不设任何表示起始/结束的 HRI 字符

当设置条码可读字符（HRI）打印时，控制字符将用空格代替当选择 CODE128 ( $\mathsf { m } = 7 3 \mathrm { , }$ ) 时：

• 参考附录 A，CODE 128 的相关信息和字符集。

• 在使用 CODE 128 时，按照下列说明进行编码：

$\textcircled{1}$ 在条码数据前必须先选择字符集（CODE A、CODE B 和 CODE C 中的一个）。

$\textcircled{2}$ 选择字符集是通过发送字符“{” 和另外一个字符结合来完成的；ASCII码字符

“{” 通过连续发送字符“{”两次来完成。

特殊字符 发送数据


ASCII 码十六进制码 十进制码


<table><tr><td rowspan="2">特殊字符</td><td colspan="3">发送数据</td></tr><tr><td>ASCII码</td><td>十六进制码</td><td>十进制码</td></tr><tr><td>SHIFT</td><td>{S</td><td>7B,53</td><td>123, 83</td></tr><tr><td>CODEA</td><td>{A</td><td>7B,41</td><td>123, 65</td></tr><tr><td>CODEB</td><td>{B</td><td>7B,42</td><td>123, 66</td></tr><tr><td>CODEC</td><td>{C</td><td>7B,43</td><td>123, 67</td></tr><tr><td>FNC1</td><td>{1</td><td>7B,31</td><td>123, 49</td></tr><tr><td>FNC2</td><td>{2</td><td>7B,32</td><td>123, 50</td></tr><tr><td>FNC3</td><td>{3</td><td>7B,33</td><td>123, 51</td></tr><tr><td>FNC4</td><td>{4</td><td>7B,34</td><td>123, 52</td></tr><tr><td>“{”</td><td>{}</td><td>7B,7B</td><td>123, 123</td></tr></table>

实例 例如打印“No. 123456”

在这个实例中，打印机首先用 CODE B 打印“No.”，接着用 CODE C 打印余下的数字：

GS k 73 10 123 66 78 111 46 123 67 12 34 56 

<table><tr><td></td><td>No.123456CODE 128:1b 40 1d 48 02 1d 68 64 1d 77 031d 6b 49 0A 7B 42 4E 6F 2E 7B 43 0C 22 38如果在条码数据的最前端不是字符集选择,则打印机将停止这条命令的处理,并将余下的数据作为普通数据处理。如果“\{\}和紧接着它的那个字符不是上面所指定的组合,则打印机停止这条命令的处理,并将余下的数据作为普通数据处理。打印机打印HRI字符时,不打印shift字符和字符集选择数据。功能字符的HRI字符不打印。控制字符(&lt;00&gt;Hto &lt;1F&gt;Hand &lt;7F&gt;H)的HRI字符也不打印;&lt;其它&gt;一定要保证条码的左右间隙。间隙因条码类型不同而不同。</td></tr><tr><td>使用示例</td><td>1b 40 1d 48 02 1d 68 64 1d 77 0130 0D 0A1d 6b 00 30 31 32 33 34 35 36 37 38 39 31 0031 0D 0A1d 6b 01 30 31 32 33 34 35 36 37 38 39 31 0032 0D0A1d 6b 02 30 31 32 33 34 35 36 37 38 39 31 32 0033 0D 0A1d 6b 03 30 31 32 33 34 35 36 37 37 0034 0D 0A1D 6B 04 30 31 32 41 42 20 24 25 2B 2D 2E 2F 0035 0D 0A1d 6b 05 30 31 32 33 34 35 36 37 38 39 31 32 0036 0D 0A1d 6b 06 2D 31 32 42 24 2B 2D 2E 001d 6b 06 43 31 32 33 34 35 36 34 38 39 0036 35 0D 0A1d 6b 41 0c 31 32 33 34 35 36 37 38 39 30 31 3236 36 0D 0A1d 6b 42 0c 30 32 33 34 35 36 30 30 30 38 3936 37 0D 0A1d 6b 43 0c 30 32 33 34 35 36 30 30 30 38 39</td></tr><tr><td></td><td>36 38 0D 0A
1d 6b 44 08 30 32 33 34 35 36 30 30
36 39 20 20 4e 4f 20 24 25 2b 2d 2e 2f 31 32 33 34 35 36 30 30 0D 0A
1d 6b 45 11 4e 4f 20 24 25 2b 2d 2e 2f 31 32 33 34 35 36 30 30
37 30 20 20 20 30 32 33 34 35 36 30 30 C5 BC CA FD 0D 0A
1d 6b 46 09 30 31 32 33 34 35 36 30 30
37 31 0d 0a
1d 6b 47 05 32 33 34 35 36
37 32 0d 0a
1d 6b 48 0b 32 33 34 35 36 41 42 2e 2f 2b 2c
37 33 0d0a
1d 6b 49 0A 7B 42 4E 6F 2E 7B 43 0C 22 38
Code 128 :
1b 40 1d 48 02 1d 68 64 1d 77 03
37 33 0d0a
1d 6b 49 0A 7B 42 4E 6F 2E 7B 43 0C 22 38</td></tr></table>

# $\textcircled{6}$ 二维码打印指令

# 设置QR码的模块类型

<table><tr><td>指令名称</td><td>设置QR码的模块类型</td></tr><tr><td>指令代码</td><td>ASCII : GS ( k pL pH cn fn n十进制 : 29 40 107 pL pH cn fn n十六进制 : 1D 28 6b pL pH cn fn n</td></tr><tr><td>功能描述</td><td>设置QR码的模块类型</td></tr><tr><td>参数范围</td><td>pL=3, pH=0cn=49fn=670 ≤ n ≤ 16</td></tr><tr><td>默认值</td><td>n=3</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>设置QR码图形模块的类型到[n点×n点]。</td></tr><tr><td>使用示例</td><td>无</td></tr></table>

# 设置QR码的错误校正水平误差

<table><tr><td>指令名称</td><td colspan="3">设置QR码的错误校正水平误差</td></tr><tr><td>指令代码</td><td colspan="3">ASCII : GS ( k pL pH cn fn n 十进制 : 29 40 107 pL pH cn fn n 十六进制 : 1D 28 6b pL pH cn fn n</td></tr><tr><td>功能描述</td><td colspan="3">设置QR码的错误校正水平误差</td></tr><tr><td>参数范围</td><td colspan="3">pL=3, pH=0</td></tr><tr><td></td><td colspan="3">cn=49
fn=69
48 ≤ n ≤ 51</td></tr><tr><td>默认值</td><td colspan="3">n=48</td></tr><tr><td>支持型号</td><td colspan="3">所有型号</td></tr><tr><td rowspan="6">注意事项</td><td colspan="3">设置 QR 码的错误校正水平误差</td></tr><tr><td>n</td><td>功能</td><td>参考:
恢复的大概代表 (%)</td></tr><tr><td>48</td><td>错误校正水平误差 L</td><td>7</td></tr><tr><td>49</td><td>错误校正水平误差 m</td><td>15</td></tr><tr><td>50</td><td>错误校正水平误差 q</td><td>25</td></tr><tr><td>51</td><td>错误校正水平误差 h</td><td>30</td></tr><tr><td>使用示例</td><td colspan="3">无</td></tr></table>

# 存储QR码的数据到 QR码缓冲区

<table><tr><td>指令名称</td><td>存储QR码的数据到QR码缓冲区</td></tr><tr><td>指令代码</td><td>ASCII : GS( k pL pH cn fn md1...dk十进制 : 29 40 107 pL pH cn fn md1...dk十六进制 : 1D 28 6b pL pH cn fn md1...dk</td></tr><tr><td>功能描述</td><td>存储QR码的数据到QR码缓冲区</td></tr><tr><td>参数范围</td><td>4 ≤ (pL + pH×256) ≤ 7092 (0 ≤ pL ≤ 255, 0 ≤ pH ≤ 28)cn=49fn=80m=480 ≤ d ≤ 255k = (pL + pH×256) - 3</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>存储二维码的数据(d1...dk)到二维码缓冲区。( (pL + pH×256) -3 )的字节在 m(d1...dk)后作为图形的数据被处理。</td></tr><tr><td>使用示例</td><td>无</td></tr></table>

# 打印QR码

<table><tr><td>指令名称</td><td>打印 QR 码</td></tr><tr><td>指令代码</td><td>ASCII : GS ( k pL pH cn fn m
十进制 : 29 40 107 pL pH cn fn m
十六进制 : 1D 28 6b pL pH cn fn m</td></tr><tr><td>功能描述</td><td>打印 QR 码</td></tr><tr><td>参数范围</td><td>pL=3, pH=0
cn=49
fn=81
m=48</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>打印QR码。
用户必须考虑QR码图形的空间（QR码图形上下的间距和左右的间距被指定在规格里）。</td></tr><tr><td>使用示例</td><td>1b 40
1d 28 6b 03 00 31 43 03
1d 28 6b 03 00 31 45 30
1d 28 6b 06 00 31 50 30 41 42 43
1b 61 01
1d 28 6b 03 00 31 52 30
1d 28 6b 03 00 31 51 30</td></tr></table>


设置QR码的图形信息


<table><tr><td>指令名称</td><td colspan="5">设置QR码的图形信息</td><td></td></tr><tr><td>指令代码</td><td colspan="5">ASCII : GS ( k pL pH cn fn m十进制 : 29 40 107 pL pH cn fn m十六进制 : 1D 28 6b pL pH cn fn m</td><td></td></tr><tr><td rowspan="13">功能描述</td><td colspan="4">设置QR码的图形信息。下面是图形信息的具体细节:</td><td colspan="2" rowspan="12">宽度和高度的数据发送:图形数据的高度和宽度值是以点为单位。其他信息数据发送:“十六进制=30H/十进制=48”表示数据不被打印。“十六进制=31H/十进制=49”表示数据不被打印。</td></tr><tr><td>发送数据</td><td>十六进制</td><td>十进制</td><td>数据类型</td></tr><tr><td>Header</td><td>37H</td><td>55</td><td>1byte</td></tr><tr><td>Flag</td><td>36H</td><td>54</td><td>1byte</td></tr><tr><td>Width</td><td>30H-39H</td><td>48-57</td><td>1-5byte</td></tr><tr><td>Separator</td><td>1FH</td><td>31</td><td>1byte</td></tr><tr><td>Height</td><td>30H-39H</td><td>48-57</td><td>1-5byte</td></tr><tr><td>Separator</td><td>1FH</td><td>31</td><td>1byte</td></tr><tr><td>Fixed Value</td><td>31H</td><td>49</td><td>1byte</td></tr><tr><td>Separator</td><td>1FH</td><td>31</td><td>1byte</td></tr><tr><td>Other Information</td><td>30H or 31H</td><td>48 or 49</td><td>1byte</td></tr><tr><td>NUL</td><td>00H</td><td>0</td><td>1byte</td></tr><tr><td colspan="6">数据的高度和宽度值是以点为单位。其他信息数据发送:“十六进制=30H/十进制=48”表示数据不被打印。“十六进制=31H/十进制=49”表示数据不被打印。</td></tr><tr><td>参数范围</td><td colspan="6">pL=3, pH=0cn=49fn=82m=48</td></tr><tr><td>默认值</td><td colspan="6">无</td></tr><tr><td>支持型号</td><td colspan="6">所有型号</td></tr><tr><td>注意事项</td><td colspan="6">该命令不打印 QR 码图形。
用户必须考虑 QR 码图形的空间（QR 码图形上下的间距和左右的间距被指定在规格里）。</td></tr><tr><td>使用示例</td><td colspan="6">无</td></tr></table>


打印二维码


<table><tr><td>指令名称</td><td>打印二维码</td></tr><tr><td>指令代码</td><td>ASCII : GS k m v r nL nH d1...dk
十进制 : 29 107 97 v r nL nH d1...dk
十六进制 : 1D 6B 61 v r nl nH d1...dk</td></tr><tr><td>功能描述</td><td>打印二维码
v表示二维码的规格，v=0表示自动选择二维码的规格
r表示纠错等级
nL nH表示数据长度
d1...dk表示要打印的二维码数据</td></tr><tr><td>参数范围</td><td>0 ≤ v ≤ 17
1 ≤ r ≤ 4
k = nL + 256 * nH</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>便携打印机</td></tr><tr><td>注意事项</td><td>打印QR码。</td></tr><tr><td>使用示例</td><td>1b 40
1D 6B 61 08 02 08 00 30 31 32 33 34 35 36 37</td></tr></table>

# $\textcircled{7}$ 状态指令


传送状态


<table><tr><td>指令名称</td><td colspan="5">传送状态</td></tr><tr><td>指令代码</td><td colspan="5">ASCII : G S r n十进制 : 29114 n十六进制 : 1D72 n</td></tr><tr><td rowspan="5">功能描述</td><td colspan="5">传送由n指定的状态,如下所示:</td></tr><tr><td>n</td><td colspan="4">状态</td></tr><tr><td>1.49</td><td colspan="4">传送纸传感器状态</td></tr><tr><td></td><td colspan="4"></td></tr><tr><td></td><td colspan="4"></td></tr><tr><td>参数范围</td><td colspan="5">n = 1, 49</td></tr><tr><td>默认值</td><td colspan="5">无</td></tr><tr><td>支持型号</td><td colspan="5">所有型号</td></tr><tr><td>注意事项</td><td colspan="5">当使用串行接口时:若设定DTR/DSR控制,则打印机在确认主机接收数据就绪后(DSR信号为SPACE),仅传送一个字节。如果主计算机没有准备好接收送数据(DSR信号为MARK),则打印机等待直到主机就绪。</td></tr><tr><td rowspan="8"></td><td colspan="5">若设定XON/XOFF控制,打印机仅传送一个字节,且不确认DSR信号状态。当数据在打印缓冲区中生成时,执行该命令。因此在接收该命令和传送状态之间,可能有一个时间间隔,这取决于接收缓冲区的状态。当用GSa激活自动状态回复ASB时,用GSr传送的状态和ASB状态必须区分开。传送的状态类型如下所示:打印纸传感器状态(n=1,49):</td></tr><tr><td>位</td><td>关/开</td><td>十六进制</td><td>十进制</td><td>ASB状态</td></tr><tr><td>0,1</td><td>-</td><td>-</td><td>-</td><td>无意义。</td></tr><tr><td rowspan="2">2,3</td><td>关</td><td>00</td><td>0</td><td>纸尽传感器:打印纸充足。</td></tr><tr><td>开</td><td>(0C)</td><td>(12)</td><td>纸尽传感器缺纸。</td></tr><tr><td>4</td><td>关</td><td>00</td><td>0</td><td>未用,固定为关。</td></tr><tr><td>5,6</td><td>-</td><td>-</td><td>-</td><td>未定义。</td></tr><tr><td>7</td><td>关</td><td>00</td><td>0</td><td>未用,固定为关。</td></tr><tr><td colspan="6">位2和3:打印纸尽传感器检测到打印纸尽时,打印机进入脱机状态,且该命令不执行。因此位2和3不传送缺纸状态。</td></tr><tr><td>使用示例</td><td colspan="5">无</td></tr></table>


实时传送状态


<table><tr><td>指令名称</td><td>实时传送状态</td></tr><tr><td>指令代码</td><td>ASCII : DLE EOT n十进制 : 164 n十六进制 : 1004 n</td></tr><tr><td>功能描述</td><td>根据下列参数,实时传送打印机状态,参数n用来指定所要传送的打印机状态:n=1:传送打印机状态n=2:传送脱机状态n=3:传送错误状态n=4:传送纸传感器状态</td></tr><tr><td>参数范围</td><td>1≤n≤4</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr></table>

# 注意事项

• 打印机收到该命令后立即返回相关状态

• 该命令尽量不要插在 2个或更多字节的命令序列中。

• 即使打印机被 ESC $=$ (选择外设)命令设置为禁止，该命令依然有效。

• 打印机传送当前状态，每一状态用 1个字节数据表示。

• 打印机传送状态时并不确认主机是否收到。

• 打印机收到该命令立即执行。

• 该命令只对串口打印机有效。打印机在任何状态下收到该命令都立即执行。


$\mathrm { n } { = } 1$ ：打印机状态


<table><tr><td>位</td><td>0/1</td><td>十六进制码</td><td>十进制码</td><td>功能</td></tr><tr><td>0</td><td>0</td><td>00</td><td>0</td><td>固定为0</td></tr><tr><td>1</td><td>1</td><td>02</td><td>2</td><td>固定为1</td></tr><tr><td rowspan="2">2</td><td>0</td><td>00</td><td>0</td><td>一个或两个钱箱打开
(没有钱箱的机器该位固定为零)</td></tr><tr><td>1</td><td>04</td><td>4</td><td>两个钱箱都关闭</td></tr><tr><td rowspan="2">3</td><td>0</td><td>00</td><td>0</td><td>联机</td></tr><tr><td>1</td><td>08</td><td>8</td><td>脱机</td></tr><tr><td>4</td><td>1</td><td>10</td><td>16</td><td>固定为1</td></tr><tr><td>5,6</td><td></td><td>--</td><td>--</td><td>未定义</td></tr><tr><td rowspan="2">7</td><td>0</td><td>00</td><td>00</td><td>纸已撕走</td></tr><tr><td>1</td><td>80</td><td>96</td><td>纸未撕走</td></tr></table>


$\mathrm { \tt n } { = } 2$ ：传送脱机状态


<table><tr><td>位</td><td>0/1</td><td>十六进制码</td><td>十进制码</td><td>功能</td></tr><tr><td>0</td><td>0</td><td>00</td><td>0</td><td>固定为0</td></tr><tr><td>1</td><td>1</td><td>02</td><td>2</td><td>固定为1</td></tr><tr><td rowspan="2">2</td><td>0</td><td>00</td><td>0</td><td>上盖关</td></tr><tr><td>1</td><td>04</td><td>4</td><td>上盖开</td></tr><tr><td rowspan="2">3</td><td>0</td><td>00</td><td>0</td><td>未按走纸键</td></tr><tr><td>1</td><td>08</td><td>8</td><td>按下走纸键</td></tr><tr><td>4</td><td>1</td><td>10</td><td>16</td><td>固定为1</td></tr><tr><td rowspan="2">5</td><td>0</td><td>00</td><td>0</td><td>打印机不缺纸</td></tr><tr><td>1</td><td>20</td><td>32</td><td>打印机缺纸</td></tr><tr><td rowspan="2">6</td><td>0</td><td>00</td><td>00</td><td>没有出错情况</td></tr><tr><td>1</td><td>40</td><td>64</td><td>有错误情况</td></tr><tr><td>7</td><td>0</td><td>00</td><td>0</td><td>固定为0</td></tr></table>


$\mathrm { n } { = } 3$ ：传送错误状态


<table><tr><td>位</td><td>0/1</td><td>十六进制码</td><td>十进制码</td><td>功能</td></tr><tr><td>0</td><td>0</td><td>00</td><td>0</td><td>固定为0</td></tr><tr><td>1</td><td>1</td><td>02</td><td>2</td><td>固定为1</td></tr></table>

<table><tr><td rowspan="9"></td><td>2</td><td></td><td>--</td><td>--</td><td>未定义</td></tr><tr><td rowspan="2">3</td><td>0</td><td>00</td><td>0</td><td>切刀无错误</td></tr><tr><td>1</td><td>08</td><td>8</td><td>切刀有错误</td></tr><tr><td>4</td><td>1</td><td>10</td><td>16</td><td>固定为1</td></tr><tr><td rowspan="2">5</td><td>0</td><td>00</td><td>0</td><td>无不可恢复错误</td></tr><tr><td>1</td><td>20</td><td>32</td><td>有不可恢复错误</td></tr><tr><td rowspan="2">6</td><td>0</td><td>00</td><td>00</td><td>打印头温度和电压正常</td></tr><tr><td>1</td><td>40</td><td>64</td><td>打印头温度或电压超出范围</td></tr><tr><td>7</td><td>0</td><td>00</td><td>0</td><td>固定为0</td></tr><tr><td colspan="6">n=4:传送纸传感器状态</td></tr><tr><td></td><td>位</td><td>0/1</td><td>十六进制码</td><td>十进制码</td><td>功能</td></tr><tr><td></td><td>0</td><td>0</td><td>00</td><td>0</td><td>固定为0</td></tr><tr><td></td><td>1</td><td>1</td><td>02</td><td>2</td><td>固定为1</td></tr><tr><td></td><td rowspan="2">2,3</td><td>0</td><td>00</td><td>0</td><td>有纸</td></tr><tr><td></td><td>1</td><td>0C</td><td>12</td><td>纸将近</td></tr><tr><td></td><td>4</td><td>1</td><td>10</td><td>16</td><td>固定为1</td></tr><tr><td></td><td rowspan="2">5,6</td><td>0</td><td>00</td><td>0</td><td>有纸</td></tr><tr><td></td><td>1</td><td>60</td><td>96</td><td>纸尽</td></tr><tr><td></td><td>7</td><td>0</td><td>00</td><td>0</td><td>固定为0</td></tr><tr><td colspan="6"></td></tr><tr><td>使用示例</td><td colspan="5">10 04 0110 04 0210 04 0310 04 04</td></tr></table>


实时打印机请求


<table><tr><td>指令名称</td><td colspan="2">实时打印机请求</td></tr><tr><td>指令代码</td><td colspan="2">ASCII : DLE ENQ n十进制 : 165 n十六进制 : 1005 n</td></tr><tr><td rowspan="5">功能描述</td><td colspan="2">打印机响应主机的请求。n指定下列请求:</td></tr><tr><td>n</td><td>请求</td></tr><tr><td>1</td><td>从错误恢复并从错误出现的行开始重新开始打印。</td></tr><tr><td>2</td><td>在清除接收和打印缓冲区后从错误恢复。</td></tr><tr><td></td><td></td></tr><tr><td>参数范围</td><td colspan="2">n = 1, 2</td></tr><tr><td>默认值</td><td colspan="2">无</td></tr><tr><td>支持型号</td><td colspan="2">所有型号</td></tr><tr><td>注意事项</td><td colspan="2">仅当自动切纸器错误,盖板打开错误出现时,此命令才有效。打印机一接到此命令就开始处理数据。即使打印机处于脱机状态,打印缓冲区满或出现串行接口模式错误时,仍然执行该命令。在并行接口模式下,当打印机忙时,此命令不能执行。无论何时收到&lt;H&gt;&lt;05&gt;H&lt;n&gt;(1≤n≤2)数据序列,都将发送状态。例如:ESC * m nL nH dk , d1 = &lt;10&gt;H , d2 = &lt;05&gt;H , d3 = &lt;01&gt;H在一个含有2个或者更多字节的命令的数据中,不能使用该命令。例如:如果想要发送 ESC 3n 到打印机,但是在n被发送前,DTR(对于主机是DSR)会变为MARK ,于是在n被接收前,发生DLE ENQ 2中断。DLE ENQ 2 的代码 &lt;10&gt;H 会被当作 ESC 3 的代码&lt;10&gt;H 处理。DLE ENQ 2 允许打印机在清除接收缓冲区和打印缓冲区中的数据后,从错误状态恢复。打印机保留错误出现时处于有效状态的设置(如ESC !,ESC3 等。)可用此命令和ESC @ 完全初始化打印机,此命令只对有可能恢复的错误有效,打印头温度错误除外。</td></tr><tr><td>使用示例</td><td colspan="2">10 05 01</td></tr></table>


允许、禁止自动状态回复（ASB）


<table><tr><td>指令名称</td><td colspan="5">允许、禁止自动状态回复(ASB)</td></tr><tr><td>指令代码</td><td colspan="5">ASCII : GS a n十进制 : 29 97 n十六进制 : 1d 61 n</td></tr><tr><td rowspan="16">功能描述</td><td>允许或禁止 ASB 并且用 n 指定包括的状态项,如下所示:位</td><td>关/开</td><td>十六进制码</td><td>十进制码</td><td>ASB 状态</td></tr><tr><td>0</td><td>-</td><td>-</td><td>-</td><td>未定义</td></tr><tr><td>1</td><td>-</td><td>-</td><td>-</td><td>未定义</td></tr><tr><td rowspan="2">2</td><td>关</td><td>00</td><td>0</td><td>错误状态禁止</td></tr><tr><td>开</td><td>04</td><td>4</td><td>错误状态允许</td></tr><tr><td rowspan="2">3</td><td>关</td><td>00</td><td>0</td><td>打印纸卷传感器状态禁止</td></tr><tr><td>开</td><td>08</td><td>8</td><td>打印纸卷传感器状态允许</td></tr><tr><td>4-7</td><td>-</td><td>-</td><td>-</td><td>未定义</td></tr><tr><td colspan="5">第一个字节(打印机信息):</td></tr><tr><td>位</td><td>关/开</td><td>十六进制码</td><td>十进制码</td><td>ASB 状态</td></tr><tr><td>0,1</td><td>关</td><td>00</td><td>0</td><td>没有定义。固定为 0。</td></tr><tr><td>2</td><td>开</td><td>04</td><td>0</td><td>没有定义。固定为 1。</td></tr><tr><td>3</td><td>关</td><td>00</td><td>0</td><td>没有定义。固定为 0。</td></tr><tr><td>4</td><td>开</td><td>10</td><td>16</td><td>没有定义。固定为 1。</td></tr><tr><td>5</td><td>关</td><td>00</td><td>0</td><td>没有定义。固定为 0。</td></tr><tr><td>6</td><td>关</td><td>00</td><td>0</td><td>未通过按进纸纸键走纸</td></tr><tr><td rowspan="20"></td><td rowspan="2">7</td><td>开</td><td>40</td><td>64</td><td>正在通过按进纸纸键走纸。</td></tr><tr><td></td><td>00</td><td>0</td><td>没有定义。固定为0。</td></tr><tr><td colspan="5">第二个字节(打印机信息):</td></tr><tr><td>位</td><td>关/开</td><td>十六进制码</td><td>十进制码</td><td>ASB状态</td></tr><tr><td>0-4</td><td>关</td><td>00</td><td>0</td><td>没有定义。固定为0。</td></tr><tr><td rowspan="2">5</td><td>关</td><td>00</td><td>0</td><td>没有不可恢复错误发生。</td></tr><tr><td>开</td><td>20</td><td>32</td><td>有不可恢复错误发生。</td></tr><tr><td rowspan="2">6</td><td>关</td><td>00</td><td>0</td><td>没有可自动恢复错误发生。</td></tr><tr><td>开</td><td>40</td><td>64</td><td>有可自动恢复错误发生。</td></tr><tr><td>7</td><td>关</td><td>00</td><td>0</td><td>没有定义。固定为0。</td></tr><tr><td colspan="5">第三个字节(纸传感器信息):</td></tr><tr><td>位</td><td>关/开</td><td>十六进制码</td><td>十进制码</td><td>ASB状态</td></tr><tr><td>0,1</td><td>关</td><td>00</td><td>0</td><td>没有定义。固定为0。</td></tr><tr><td rowspan="2">2,3</td><td>关</td><td>00</td><td>0</td><td>打印机有纸。</td></tr><tr><td>开</td><td>0c</td><td>12</td><td>打印机缺纸。</td></tr><tr><td>4-7</td><td>关</td><td>00</td><td>0</td><td>没有定义。固定为0。</td></tr><tr><td colspan="5">第四个字节(纸传感器信息):</td></tr><tr><td>位</td><td>关/开</td><td>十六进制码</td><td>十进制码</td><td>ASB状态</td></tr><tr><td>0-3</td><td>-</td><td>-</td><td>-</td><td>没有定义。</td></tr><tr><td>4-7</td><td>关闭</td><td>00</td><td>0</td><td>没有定义。固定为0。</td></tr><tr><td>参数范围</td><td colspan="5">0≤n≤255</td></tr><tr><td>默认值</td><td colspan="5">无</td></tr><tr><td>支持型号</td><td colspan="5">所有型号</td></tr><tr><td>注意事项</td><td colspan="5">如果在上表中的任何一个状态项是被允许的,那么当执行该命令时打印机输状态。一旦“允许”的状态项改变了,打印机便自动传输状态。因为每个状态传输表示了当前的状态,因此禁止的状态项可以改变。如果所有的状态项都被禁止,那么也禁止 ASB功能。如果将 ASB允许作为缺省设定,那么从打印机打开第一次可以接收和传输打印机数据时,打印机就传输状态。传输以下四个状态字节,不用确定是否主机准备接收数据。四个状态字节必须是连续的,除XOFF码之外。因为命令数据在接收缓冲区里被处理后执行,因此在数据接收和状态传输之间可能有一段滞后时间。当使用DLE EOT时,必须区分由这些命令传输的状态和ASB状态。</td></tr><tr><td>使用示例</td><td colspan="5">1D 61 08</td></tr></table>

# $\textcircled{8}$ 其他指令


初始化打印机


<table><tr><td>指令名称</td><td>初始化打印机</td></tr><tr><td>指令代码</td><td>ASCII : ESC @</td></tr><tr><td></td><td>十进制 : 27 64十六进制 : 1B 40</td></tr><tr><td>功能描述</td><td>初始化打印机下列内容:清除打印缓存各参数恢复默认值</td></tr><tr><td>参数范围</td><td>无</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>无</td></tr><tr><td>使用示例</td><td>无</td></tr></table>


打印自测页


<table><tr><td>指令名称</td><td>打印自测页</td></tr><tr><td>指令代码</td><td>ASCII : DC2 T
十进制 : 18 94
十六进制 : 12 54</td></tr><tr><td>功能描述</td><td>打印机打印一张自测页，上面包含打印机的程序版本，通讯接口类型，代码页和其他一些数据</td></tr><tr><td>参数范围</td><td>无</td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>无</td></tr><tr><td>使用示例</td><td>1B 40 12 54</td></tr></table>


设置打印浓度


<table><tr><td>指令名称</td><td>设置打印浓度</td></tr><tr><td>指令代码</td><td>ASCII : ESC 7 n1 n2 n3十进制 : 27 55 n1 n2 n3十六进制 : 1B 37 n1 n2 n3</td></tr><tr><td>功能描述</td><td>设置打印的最多加热点,加热时间、间隔时间:n1 = 0-255 最多加热点数,单位(8dots),默认值9(80点);n2 = 0-255 加热的时间,单位(10us),默认值80;n3 = 0-255 加热间隔时间,单位(10us),默认值2;加热点数多,则控制板的最大耗电电流大,打印速度快。最大加热点数为8×(n1+1);加热时间越长,则打印黑度高,打印速度越慢。加热时间过短,则可能出现打印空白;间隔时间越长,打印越清晰,打印速度变慢;</td></tr><tr><td>参数范围</td><td></td></tr><tr><td>默认值</td><td>无</td></tr><tr><td>支持型号</td><td>所有型号</td></tr><tr><td>注意事项</td><td>“加热时间”、“加热间隔”控制板会根据输入电压而自动调整。</td></tr><tr><td>使用示例</td><td>加热点数:80点,加热时间:800us,间隔时间200us。</td></tr></table>

<table><tr><td>1B 40
1B 37 09 50 02
12 54
加热点数：80点，加热时间：1600us，间隔时间200us。
1B 40
1B 37 09 A0 02
12 54
可以看出，加热时间拉长之后，打印浓度明显变黑了。</td></tr></table>

# 产生钱箱脉冲（OnlyForDrawer）

<table><tr><td>指令名称</td><td colspan="2">产生钱箱脉冲</td></tr><tr><td>指令代码</td><td colspan="2">ASCII : ESC p m t1 t2十进制 : 27 112 m t1 t2十六进制 : 1B 70 m t1 t2</td></tr><tr><td>功能描述</td><td colspan="2">输出脉冲（脉冲由t1和t2指定）到m指定的引脚</td></tr><tr><td>参数范围</td><td colspan="2">m=0,1,48,490 ≤ t1 ≤ 2550 ≤ t2 ≤ 255</td></tr><tr><td>默认值</td><td colspan="2">无</td></tr><tr><td>支持型号</td><td colspan="2">所有型号</td></tr><tr><td rowspan="5">注意事项</td><td colspan="2">1、钱箱引脚由m指定</td></tr><tr><td>m</td><td>功能</td></tr><tr><td>0,48</td><td>钱箱打开/关闭信号（连接引脚2）</td></tr><tr><td>1,49</td><td>钱箱打开/关闭信号（连接引脚5）</td></tr><tr><td colspan="2">2、钱箱打开时时[t1×2ms]，而关闭时是[t2×2ms]。3、如果t2＜t1，则关闭时是[t1×2ms]。</td></tr><tr><td>使用示例</td><td colspan="2">1B 401B 70 00 60 601B 70 01 60 60</td></tr></table>