CREATE TABLE public."user"
(
  user_id varchar DEFAULT 128 NOT NULL,
  user_name varchar DEFAULT 128 NOT NULL,
  user_url varchar DEFAULT 258 NOT NULL
);
CREATE UNIQUE INDEX user_user_id_uindex ON public."user" (user_id);


CREATE TABLE public.repo
(
  user_id varchar DEFAULT 128 NOT NULL,
  repo_id varchar DEFAULT 128 NOT NULL,
  repo_name varchar DEFAULT 128 NOT NULL,
  repo_url varchar DEFAULT 256 NOT NULL,
  description varchar DEFAULT 1024,
  default_branch varchar DEFAULT 128,
  language varchar DEFAULT 32 NOT NULL,
  local_save_path varchar DEFAULT 256 NOT NULL,
  create_time time,
  update_time time,
  star_cnt int DEFAULT 0,
  fork_cnt int DEFAULT 0,
  file_cnt int DEFAULT -1,
  token_cnt int DEFAULT -1,
  snippet_cnt int DEFAULT -1
);
CREATE UNIQUE INDEX repo_user_id_uindex ON public.repo (user_id);
CREATE UNIQUE INDEX repo_repo_id_uindex ON public.repo (repo_id);