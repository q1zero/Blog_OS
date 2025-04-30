# Blog_OS

## 如何创建 GitHub 个人访问令牌（Personal Access Token）

1. 登录 GitHub 账户  
   - 打开 [GitHub](https://github.com) 并登录您的账户  
   - 点击右上角头像，选择 **Settings**

2. 进入开发者设置  
   - 滚动到页面底部，点击 **Developer settings**

3. 创建个人访问令牌  
   1. 在左侧菜单中选择 **Personal access tokens**  
   2. 点击 **Tokens (classic)**  
   3. 点击 **Generate new token**（生成新令牌）  
   4. 如有安全验证提示，请完成验证

4. 配置令牌信息  
   - **Note**：输入描述性名称，例如 `Blog_OS PR合并自动化`  
   - **过期时间**（Expiration）：选择合适的期限（建议 90 天）  
   - **Scopes**：勾选以下权限：  
     - `repo`（完整仓库访问权限）  
     - `workflow`（工作流权限）  
     - `read:org`（组织读取权限，仅在组织仓库时需勾选）  
   - 点击 **Generate token**  
   > **重要提示**：生成后请立即复制令牌，页面关闭后无法再次查看

---

## 将令牌添加到仓库密钥

1. 进入 Blog_OS 仓库设置  
2. 在左侧菜单点击 **Secrets and variables** → **Actions**  
3. 点击 **New repository secret**  
4. 填写密钥信息：  
   - **Name**：`CUSTOM_GITHUB_TOKEN`  
   - **Value**：粘贴刚才复制的个人访问令牌  
5. 点击 **Add secret**

完成上述步骤后，GitHub Actions 工作流即可使用此自定义令牌进行 PR 合并操作，确保拥有足够权限。
