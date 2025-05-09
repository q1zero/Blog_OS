# replit.nix
# 有关更多信息，请参阅 https://docs.replit.com/programming-ide/configuring-repl#nix
{ pkgs }: {
  # 指定 Nix 包集合。
  # pkgs.python312 表示使用 Python 3.12.x 系列的最新版本。
  # pkgs.uv 用于安装 uv 包管理器。
  # pkgs.zlib, pkgs.libjpeg, pkgs.freetype 是 Pillow 常见的编译时依赖。
  # pkgs.pkg-config 是一个帮助找到库文件的工具。
  # 如果您的项目有其他系统级依赖（例如数据库客户端库），
  # 您可以在这里添加它们。
  deps = [
    pkgs.python312
    pkgs.uv
    pkgs.zlib
    pkgs.libjpeg
    pkgs.freetype
    pkgs.pkg-config
    pkgs.redis # 添加 Redis 包
    # 如果 pymysql 需要编译且没有提供合适的 wheel，可能需要添加 MySQL 客户端开发库，
    # 例如 pkgs.mysql.client (或类似名称，具体取决于 Nixpkgs 中的包名)
    # 但通常 uv/pip 会处理好这个。
  ];

  # 可选：为环境设置环境变量。
  # 这些变量在 Nix shell 中可用。
  # [env]
  # MY_VARIABLE = "my_value";
}