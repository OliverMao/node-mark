## Docker

### Docker中安装Nginx

在Docker中安装并配置Nginx进行域名反向代理，需要执行以下步骤：

1. **拉取Nginx镜像**：
   使用Docker命令拉取官方的Nginx镜像。

   ```sh
   docker pull nginx
   ```

2. **创建Nginx配置文件**：
   创建一个自定义的Nginx配置文件，用于设置反向代理。

   ```sh
   cat <<EOF > /path/to/nginx.conf
   server {
       listen 80;
       server_name memos.yoobit.cn;
   
       location / {
           proxy_pass http://172.17.0.1:5230;
           proxy_set_header Host $host:$server_port;
           proxy_set_header X-Real-Ip $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   EOF
   ```
   
   请将`/path/to/nginx.conf`替换成你想要保存Nginx配置文件的实际路径。
   
3. **运行Nginx容器**：
   使用Docker命令运行Nginx容器，并挂载你的配置文件。

   ```sh
   docker run -d --name nginx-container -p 80:80 -v /path/to/nginx.conf:/etc/nginx/conf.d/default.conf:ro nginx
   ```

   这里`-d`表示以detached模式运行容器，`--name nginx-container`给容器命名，`-p 80:80`将容器的80端口映射到宿主机的80端口，`-v`用于挂载卷，将你的Nginx配置文件挂载到容器中。

4. **配置DNS**：
   确保域名`memos.yoobit.cn`的DNS解析指向运行Docker宿主机的公网IP地址。

5. **确保防火墙设置**：
   如果宿主机有防火墙，确保80端口对外开放。

6. **测试配置**：
   在浏览器中输入`http://memos.yoobit.cn`，如果一切配置正确，你应该会看到通过5230端口服务的内容。

请注意，这个示例中没有涉及SSL/TLS配置，如果你需要HTTPS支持，还需要额外配置SSL证书，并相应地调整Nginx配置文件中的`listen`指令为`listen 443 ssl;`以及添加SSL证书相关的配置。

另外，如果你的5230端口服务不是运行在本机上，而是运行在另一台服务器上，你需要确保`proxy_pass`后面跟的是那台服务器的IP地址或域名，并且相应端口是可访问的。

在执行以上步骤时，请确保你有足够的权限来执行Docker命令，并且已经正确安装了Docker。如果你遇到任何问题，需要根据你的具体环境进行调整。





