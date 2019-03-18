## 基本思路
1. 选定一批随机用户作为种子，去重并加入到user_queue中。
2. 对于user_queue中的每个user, 记录其所有下属的repos，过滤掉fork的项目后下载并存储，同时记录所有star了这些repos的用户id, 去重后加入到user_queue。
3. 针对每个user, 记录下他star了的所有repo，去重后加入到repo_queue
3. 重复步骤2-3


## 关键GithubAPI
所有返回的都是json格式的数据

1. 获取某个user的repos信息: https://api.github.com/users/{user_name}/repos
3. 获取某个repo的star用户的信息: https://api.github.com/repos/{user_name}/{repo_name}/stargazers
3. 获取某用户所有star了的repo的信息(和2相反):https://api.github.com/users/{user_name}/starred



## 表格数据
1. user表:
user_id, user_name, user_url
2. repo表(要过滤掉fork==True的项目):
user_id, repo_id, repo_name, repo_url, description,default_branch,
language, local_save_path,
create_time, update_time,
star_cnt, fork_cnt,
file_cnt, token_cnt, snippet_cnt

