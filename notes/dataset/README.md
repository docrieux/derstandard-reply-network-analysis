This file has been last edited on 15-06-2026 by Emma Fraxanet.

# GENERAL INFORMATION

## 1. Dataset title
**A Decade of News Forum Interactions: Threaded Conversations, Signed Votes, and Topical Tags**

## 2. Authorship

**Name:** Emma Fraxanet  
**Institution:** Barcelona Supercomputing Center   
**Email:** emma.fraxanet@upf.edu  
**ORCID:** 0000-0002-1647-7300

**Name:** Andreas Kaltenbrunner  
**Institution:** Universitat Pompeu Fabra  
**ORCID:** 0000-0002-2271-3066

**Name:** Vicenç Gómez  
**Institution:** Universitat Pompeu Fabra 
**ORCID:** 0000-0001-5146-7645

**Name:** Max Pellert  
**Institution:** Barcelona Supercomputing Center 
**Email:** max.pellert@bsc.es  
**ORCID:** 0000-0002-6557-7607

# DESCRIPTION

## 1. Dataset language
German, Metadata in English

## 2. Abstract

This dataset contains a longitudinal record of user activity on the Austrian newspaper DerStandard.at from 2013 to 2022. It includes: the data records for User-level metadata, Comment-level data, Voting behavior, Article metadata, and Pre-computed text embeddings. Additionally, it includes: Annotated subsets related to previous work, Derived Summary metadata, Supplementary files addressing data inconsistencies, Usage notes for reading and decompressing the files, and Basic example code for accessing and processing the data. All data files are provided in compressed TSV format, organized by type and temporal resolution (monthly or yearly). Structured to enable network, behavioral, and linguistic analysis, the data supports a range of computational social science and NLP applications

## 3. Keywords
Online discourse, Networks, Text Embeddings, Social Media Platforms, Signed Networks, Discussion Threads, Longitudinal Data, German language, news media

## 4. Time span of dataset
01-01-2013 – 31-12-2022

## 5. Data collection
01-06-2021 – 31-12-2022

## 6. Publication Date
27-06-2025

## 7. Grant information
Not applicable

## 8. Geographical location/s of data collection
Austria (Online platform: DerStandard.at)

# ACCESS INFORMATION

## 1. Creative Commons License of the dataset

This dataset is licensed under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) license.

You are free to:
- **Share** — copy and redistribute the material in any medium or format  
- **Adapt** — remix, transform, and build upon the material  

Under the following conditions:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.  

## 2. Dataset DOI
[10.82201/RVQGUG](https://doi.org/10.82201/RVQGUG)

## 3. Related publications
The data descriptor of this dataset can be found in:
- Fraxanet, E., Gómez, V., Kaltenbrunner, A. et al. *A Decade of News Forum Interactions: Threaded Conversations, Signed Votes, and Topical Tags*. Sci Data (2026). https://doi.org/10.1038/s41597-026-07267-3

This work is part of the Doctoral Thesis of Emma Fraxanet: 
- Fraxanet Morales, E. (2025). Computational Analysis of Online Polarization in Longitudinal Social Interaction Data. Universitat Pompeu Fabra. https://hdl.handle.net/10803/696160

## 4. Link to related datasets
- One Million Post Corpus: https://ofai.github.io/resources/omp/  
- GERMS-AT: https://ofai.github.io/GermEval2024-GerMS/

# VERSIONING AND PROVENANCE

## 1. Last modification date
15-06-2026

# METHODOLOGICAL INFORMATION

## 1. Description of the methods used to collect and generate the data
Data was collected via HTML requests and scraping the public website derstandard.at using curl and parsing tools (xidel, jq). The dataset includes comment metadata and text embedding, votes, and article metadata.

## 2. Data processing methods
Identifiers were anonymized using BLAKE2s with a fixed salt. Metadata was structured into TSV files. Additional features (e.g., thread structure, user activity stats, and pre-computed text embeddings) were generated using custom scripts.

## 3. Software or instruments needed to interpret the data
- Compatible with any software that supports `.tsv` formats
- Embeddings generated with [`KaLM-embedding-multilingual-mini-v1`](https://huggingface)

# PRACTICAL INFORMATION

## 1. Files and Documentation

In this repository you can find the following main files of the dataset:
- Comments_files
- Votes_files
- Articles_files
- Users_files
- Embeddings

The file Codebook.md describes the variables and files found inside each of these folders. 

Secondary folders provide additional information. The most relevant of these files are:

- Summary_files
    - inconsistent_comment_metadata.tsv: Addresses data inconsistencies
    - faction_users.tsv: Annotated subset related to previous work
    - Other files: Derived Summary metadata
    - get_standard_v0_2_5.sh: Script to scrape forum comments (postings) from derstandard.at articles. Outputs HTML pages containing paginated forum postings.
    - get_votes.sh: Script to scrape rating/voting data (up/downvotes) for individual forum postings on derstandard.at articles. Outputs HTML containing the voting log.
    - Other files: Derived Summary metadata
- Scripts: Example code for collecting, cleaning, and processing the data, organized by purpose. Most scripts are written in bash and awk rather than Python/pandas; this choice was made for performance, as bash/awk handle the large TSV files in this dataset far more efficiently than pandas-based approaches.
    - **Data collection**
        - `get_standard_v0_2_5.sh`: Scrapes forum comments (postings) from derstandard.at articles, outputting paginated HTML pages of postings.
        - `get_votes.sh`: Scrapes rating/voting data (up/downvotes) for individual forum postings, outputting HTML containing the voting log.
    - **Data cleaning and validation**
        - `check_inconsistent_timestamps.sh`: Checks comment and vote records for inconsistent or malformed timestamps.
        - `count_na_comments.sh`: Counts missing (NA) values across comment fields.
        - `counts_na_votes.sh`: Counts missing (NA) values across vote fields.
        - `hash_tsv_new.py`: Applies the BLAKE2s hashing scheme used to anonymize user and comment identifiers in the TSV files. The salt used is not published, so this script illustrates the anonymization method but cannot be used to reverse it.
    - **Summary and aggregate statistics**
        - `basic_stats.sh`: Computes basic descriptive statistics (counts, distributions) across the dataset.
        - `generate_users_file.sh`: Aggregates comment and voting activity into the user-level metadata file (Users_files).
        - `summarize_articles.sh`: Generates summary statistics at the article level (e.g., comments and votes per article).
        - `summarize_comments_per_topic.sh`: Aggregates comment counts and statistics by article topic.
        - `summary_comments.sh`: Produces overall summary statistics for the comments dataset.
        - `summary_votes.sh`: Produces overall summary statistics for the votes dataset.
    - **Network construction**
        - `create_signed_networks.sh`: Builds signed interaction networks (positive/negative edges) from voting data.
        - `extract_vote_network.sh`: Extracts the underlying vote network structure from the voting data.
    - **Embeddings and similarity**
        - `sample_embeddings.sh`: Draws a sample subset of pre-computed text embeddings for inspection or testing.
        - `compute_cos_sim.py`: Computes pairwise cosine similarity between comment embeddings.
        - `compute_cos_sim_1list.py`: Computes cosine similarity within a single list/set of embeddings.
        - `compute_cos_sim_cross_topics.py`: Computes cosine similarity between embeddings across different topics.
        - `sample_baseline_average.sh`: Generates a random baseline sample, averaged over multiple draws.
        - `sample_baseline_pairs.sh`: Samples random comment pairs to serve as a baseline for similarity comparisons.
        - `sample_pairs_article.sh`: Samples comment pairs from within the same article.
        - `sample_pairs_thread.sh`: Samples comment pairs from within the same discussion thread.
        - `sample_comment_reply_crossthread.sh`: Samples comment-reply pairs that span across different threads.

## 4. Handling the Split Embedding Archives

To facilitate distribution, the monthly embedding files were compressed and split into parts. Follow these steps to reconstruct and extract them:

### 4.1. Recombine the split `.tar.xz` parts

Use the command below to concatenate all `.part00?` chunks into full archive files:

```bash
for i in {01..12}_{13..22}; do 
  if [ -e "embeddings_${i}.tar.xz.part000" ]; then 
    cat embeddings_${i}.tar.xz.part00? > embeddings_${i}.tar.xz
  fi 
done
```

This will produce files like `embeddings_01_13.tar.xz`.

### 4.2. Clean up the split part files

Once combined, you can safely remove the `.part00?` fragments:

```bash
for i in {01..12}_{13..22}; do 
  if [ -e "embeddings_${i}.tar.xz.part000" ]; then 
    rm embeddings_${i}.tar.xz.part00?
  fi 
done
```

### 4.3. Extract the embedding archives

Finally, extract the `.tar.xz` files to retrieve the original `.tsv` embedding files:

```bash
for i in {01..12}_{13..22}; do 
  tar xJf embeddings_${i}.tar.xz
done
```

Each archive contains `.tsv` files with pre-computed 896-dimensional embedding vectors for comments from that month.
