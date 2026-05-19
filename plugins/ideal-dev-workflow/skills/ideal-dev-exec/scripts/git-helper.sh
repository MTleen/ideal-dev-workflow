#!/bin/bash

# Git 辅助脚本
# 用于 ideal-dev-exec skill

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印帮助
print_help() {
    echo "用法: $0 <命令> [参数]"
    echo ""
    echo "命令:"
    echo "  create-branch <name>     创建并切换到新分支"
    echo "  commit <type> <msg>      提交代码（自动生成格式化消息）"
    echo "  push                      推送当前分支到远程"
    echo "  create-mr <title> <desc> 创建 Merge Request"
    echo "  status                    显示当前分支状态"
    echo ""
    echo "示例:"
    echo "  $0 create-branch feature/user-login"
    echo "  $0 commit feat '实现用户登录功能'"
    echo "  $0 push"
    echo "  $0 create-mr '用户登录功能' '实现邮箱和密码登录'"
}

# 创建分支
create_branch() {
    local branch_name="$1"

    if [ -z "$branch_name" ]; then
        echo -e "${RED}错误: 请提供分支名称${NC}"
        exit 1
    fi

    # 检查分支是否已存在
    if git show-ref --verify --quiet "refs/heads/$branch_name"; then
        echo -e "${YELLOW}分支 $branch_name 已存在，切换到该分支${NC}"
        git checkout "$branch_name"
    else
        echo -e "${GREEN}创建并切换到分支: $branch_name${NC}"
        git checkout -b "$branch_name"
    fi
}

# 提交代码
commit_code() {
    local commit_type="$1"
    local commit_msg="$2"

    if [ -z "$commit_type" ] || [ -z "$commit_msg" ]; then
        echo -e "${RED}错误: 请提供提交类型和消息${NC}"
        echo "类型: feat, fix, refactor, test, docs, style, chore"
        exit 1
    fi

    # 验证提交类型
    case "$commit_type" in
        feat|fix|refactor|test|docs|style|chore)
            ;;
        *)
            echo -e "${YELLOW}警告: 非标准提交类型 '$commit_type'${NC}"
            echo "建议使用: feat, fix, refactor, test, docs, style, chore"
            ;;
    esac

    # 获取当前分支名作为 scope
    local branch=$(git rev-parse --abbrev-ref HEAD)
    local scope=$(echo "$branch" | sed 's/.*\///' | sed 's/-/ /g')

    local full_msg="$commit_type($scope): $commit_msg"

    echo -e "${GREEN}提交: $full_msg${NC}"
    git add -A
    git commit -m "$full_msg"
}

# 推送分支
push_branch() {
    local branch=$(git rev-parse --abbrev-ref HEAD)
    local remote=$(git remote | head -1)

    echo -e "${GREEN}推送分支 $branch 到 $remote${NC}"
    git push -u "$remote" "$branch"
}

# 创建 MR (Gitea)
create_mr() {
    local title="$1"
    local description="$2"

    if [ -z "$title" ]; then
        echo -e "${RED}错误: 请提供 MR 标题${NC}"
        exit 1
    fi

    local branch=$(git rev-parse --abbrev-ref HEAD)
    local remote_url=$(git remote get-url origin)

    # 解析 Gitea URL
    # 格式: https://gitea.example.com/owner/repo.git 或 git@gitea.example.com:owner/repo.git
    local base_url=$(echo "$remote_url" | sed -E 's|.*@([^:]+):(.+)\.git|https://\1/\2|' | sed -E 's|https://(.+)/(.+)\.git|https://\1/\2|')

    local mr_url="$base_url/compare/main...$branch"

    echo -e "${GREEN}请在浏览器中创建 MR:${NC}"
    echo ""
    echo "  URL: $mr_url"
    echo ""
    echo "标题: $title"
    echo "描述: $description"
    echo ""
    echo -e "${YELLOW}注意: 请确保已推送分支到远程${NC}"
}

# 显示状态
show_status() {
    local branch=$(git rev-parse --abbrev-ref HEAD)
    local status=$(git status --short)

    echo -e "${GREEN}当前分支: $branch${NC}"
    echo ""

    if [ -z "$status" ]; then
        echo "工作目录干净"
    else
        echo "待提交文件:"
        echo "$status"
    fi
}

# 主入口
case "$1" in
    create-branch)
        create_branch "$2"
        ;;
    commit)
        commit_code "$2" "$3"
        ;;
    push)
        push_branch
        ;;
    create-mr)
        create_mr "$2" "$3"
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        print_help
        ;;
    *)
        print_help
        exit 1
        ;;
esac
