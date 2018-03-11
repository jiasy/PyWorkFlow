# PyWorkFlow
	说明 : Excel提供参数配置的python脚本工作流
	目标 : 每一个py脚本负责一个单一的功能，通过脚本的排列组合，Excel的参数替换，制作出复杂强大的工作流。
	文档 : 暂时，先看help_1.png，挺简单的，下载之后，打开Excel，找到 复制命令行 这一个格子，把它贴到命令行里敲回车。<执行失败看Log，可能是没装环境，比如TexturePacker的命令行等等>
	前提条件 : 把py脚本import的那些都先下载一下，我本机是MAC + python2.7，windows上没试过，只保证MAC下可运行。
	好处 : Excel虽然比json重，但是会用的人多，尤其是策划。往往策划美术不会执行脚本，Excel给他们提供了一个复制粘贴就能运行脚本的能力。
    用处 : 前端打包，热更新推送，后端服务器代码上传，图标分发到工程，小图合并大图等等，只要是支持命令行的，都支持。
    复杂用途 : 可以自己配置一整套流程例如以下流程[可以从各个实例Excel中复制粘贴成一个全新的Excel]
                    生成携带SDK的参数的代码
                    生成配置文件
                    图标变更
                    根据游戏换图
                    Info.plist、mainfest.xml的参数替换
                    Xcode打包，AndroidStudio打包
                    上传蒲公英、fir、testFlight
                    推送后端配置，重启服务器
              Jenkis 下，用 pythonCode/CommonTools/Jenkins/ExcuteWorkFlowByExcel.py 可以根据Excel名，直接执行它所配置的工作流