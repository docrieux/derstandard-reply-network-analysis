
### Comments Codebook - comments_files/comments_file_MM_YY

| Variable | Type | Description | Labels |
|----------|------|-------------|--------|
| Comment_Id | string | Unique anonymized identifier of the comment | |
| Author_Id | string | Anonymized identifier of the user who authored the comment | NA = deleted user |
| Is_Reply | boolean | Whether the comment is a reply | 1 = TRUE or 0 = FALSE |
| Parent_Id | string | Identifier of the comment being replied to | NA if top-level |
| Thread_Level | int | Depth in the thread hierarchy | 0 = root |
| Origin_Parent_Id | string | ID of the root comment in the thread | Comment_Id = root |
| Timestamp | datetime | unix timestamp when the comment was posted |  |
| Article_Id | int | Identifier of the article the comment is attached to |  |
| Votes_Pos | int | Number of upvotes received |  |
| Votes_Neg | int | Number of downvotes received |  |

### Votes Codebook - votes_files/votes_file_MM_YY

| Variable | Type | Description | Labels |
|----------|------|-------------|--------|
| Comment_Id | string | Identifier of the comment being voted on |  |
| Voter_Id | string | Anonymized ID of the user who cast the vote | NA = deleted user |
| Author_Id | string | Anonymized ID of the comment's author | NA = deleted user |
| Pos | int | Indicator of positive vote cast by the voter for this comment | 0 or 1 |
| Neg | int | Indicator of negative vote cast by the voter for this comment | 0 or 1 |

### Articles Codebook - articles_files/articles_file_YY

| Variable | Type | Description | Labels |
|----------|------|-------------|--------|
| Article_Id | int | Unique identifier of the article |  |
| Topic_1 | string | Main editorial topic |  |
| Topic_2 | string | Sub-topic label |  |
| Topic_3 | string | Specific topic label |  |
| Topic_Labels | string | Comma-separated topic hierarchy with internal;shown tags |  |
| Timestamp | datetime | unix publication time of the article |  |

### Users Codebook

| Variable | Type | Description | Labels |
|----------|------|-------------|--------|
| User_Id | string | Anonymized identifier of the user |  |
| N_comments | int | Total number of comments authored |  |
| First_Comment | datetime | unix Timestamp of user's first comment |  |
| Last_Comment | datetime | unix Timestamp of user's last comment |  |
| R_pos | int | Number of upvotes received |  |
| R_neg | int | Number of downvotes received |  |
| G_pos | int | Number of upvotes given |  |
| G_neg | int | Number of downvotes given |  |
| First_vote | datetime | Timestamp of user's first vote |  |
| Last_vote | datetime | Timestamp of user's last vote |  |

### Embeddings Codebook

| Variable | Type | Description | Labels |
|----------|------|-------------|--------|
| Post_Id | string | Identifier of the comment |  |
| dim_1 to dim_896 | float[896] | Dense vector embeddings of the comment text |  |
