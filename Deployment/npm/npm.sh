下载安装脚本
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

上述命令安装后，退出终端再进行node.js安装

最新稳定版: nvm install stable

设置镜像源: npm config set registry https://registry.npmmirror.com

查看镜像源: npm config get registry

缓存路径：npm config get cache

清除缓存:  npm cache clean --force


################################用NPM安装promptfoo##############
目录准备: mkdir promptfoo-demo && cd promptfoo-demo

初始化: npm init -y

执行安装: npm install promptfoo --save-dev  

允许权限: npm approve-scripts promptfoo
