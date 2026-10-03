# Hi, I'm Fang Fengxiang 👋

Backend engineer based in Singapore 🇸🇬 · PHP / Lua / Go · OpenResty & RPC infrastructure

> 履道坦坦，幽人贞吉

---

### 🔭 What I'm building

The **yar-group** stack — bringing the [Yar](https://github.com/laruence/yar) RPC protocol to the Lua/OpenResty ecosystem, in three layers:

| Layer | Repo | What it is |
|-------|------|-----------|
| Protocol library | [lua-yar](https://github.com/fangfengxiang/lua-yar) | Pure Lua, runtime-agnostic implementation of the Yar protocol — compatible with PHP Yar & yar-c. Works in OpenResty, Skynet, and standalone Lua. |
| Framework | [lua-resty-yar](https://github.com/fangfengxiang/lua-resty-yar) | High-performance Yar RPC server for OpenResty — HTTP + TCP dual transport, cosocket non-blocking I/O, connection pooling. |
| Platform | [lua-resty-yar-gateway](https://github.com/fangfengxiang/lua-resty-yar-gateway) | PHP microservice gateway on OpenResty — service discovery, health checking, config-driven governance. |

Also:

- **[lua-resty-yar-grpc-bridge](https://github.com/fangfengxiang/lua-resty-yar-grpc-bridge)** — gRPC ↔ YAR bidirectional protocol bridge, transparently proxying gRPC clients to PHP Yar services
- **[lua-yar-grpc](https://github.com/fangfengxiang/lua-yar-grpc)** — gRPC ↔ Yar protocol stream converter in pure Lua
- **[revid-engine](https://github.com/fangfengxiang/revid-engine)** — a zero-dependency, in-process distributed ID generation engine for Go
- **[php-proto-lint](https://github.com/fangfengxiang/php-proto-lint)** — Schema-first PHP CLI: lint .proto contracts against PHP source, audit shadow traffic, inject attributes

### 🛠 Tech stack

![PHP](https://img.shields.io/badge/PHP-777BB4?style=flat-square&logo=php&logoColor=white)
![Lua](https://img.shields.io/badge/Lua-2C2D72?style=flat-square&logo=lua&logoColor=white)
![Go](https://img.shields.io/badge/Go-00ADD8?style=flat-square&logo=go&logoColor=white)
![OpenResty](https://img.shields.io/badge/OpenResty-2E8B57?style=flat-square&logo=nginx&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat-square&logo=nginx&logoColor=white)

### 📊 GitHub stats

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats.vercel.app/api?username=fangfengxiang&show_icons=true&theme=github_dark&hide_border=true&include_all_commits=true">
  <img src="https://github-readme-stats.vercel.app/api?username=fangfengxiang&show_icons=true&hide_border=true&include_all_commits=true">
</picture>

### 📫 Find me

- 掘金: [juejin.cn/user/5860901dac502e00](https://juejin.cn/user/5860901dac502e00)
- Email: 823911836@qq.com
