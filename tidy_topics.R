library(tidyverse)
library(amcat4r)
library(topicmodels)
library(corpustools)
library(tidytext)
library(ggplot2)
library(dplyr)
library(tidyr)

#install.packages("ggwordcloud")
library(ggwordcloud)
library(udpipe)
library(amcatr)

#login 

conn = amcat.connect('https://eur.amcat.nl')
d = amcatr::amcat.hits(conn, queries='*', project=4, sets=177, col = c('id','date','publisher', 'title','text'))   
head(d)
table(d$publisher)



d1=d|>
  mutate(text = paste0(title,text))

#it needs a dataframe containing text and doc_id
d2 = d1|>
  rename(doc_id=id)|>
  select(doc_id, text)



# this assumes that the data frame contains rows called doc_id and text
#this takes a while!
tokens = udpipe(d2, "dutch", parser="none")

#### Preprocess data  
library(stopwords)
mystopwords = stopwords(language = 'nl', source = 'snowball')

tokens = tokens |> 
  select(-sentence)

tokens2 = tokens|>
  filter(upos %in% c("NOUN", "PROPN"))|>
  filter(! lemma %in% mystopwords)|>
  rename(word=lemma)|>
  select(doc_id,word)

dtm = tokens2 |> 
  group_by(doc_id, word) |>
  summarize(n=n()) |>
  filter(n>5) |>
  cast_dtm(doc_id, word, n)

quantum_lda <- LDA(dtm, k = 10, control = list(seed = 1234))
quantum_topics <- tidy(quantum_lda, matrix = "beta")
quantum_topics


quantum_top_terms <- quantum_topics %>%
  group_by(topic) %>%
  slice_max(beta, n = 10) %>% 
  ungroup() %>%
  arrange(topic, -beta)

quantum_top_terms %>%
  mutate(term = reorder_within(term, beta, topic)) %>%
  ggplot(aes(beta, term, fill = factor(topic))) +
  geom_col(show.legend = FALSE) +
  facet_wrap(~ topic, scales = "free") +
  scale_y_reordered()


beta_wide <- quantum_topics %>%
  mutate(topic = paste0("topic", topic)) %>%
  pivot_wider(names_from = topic, values_from = beta) %>% 
  filter(topic1 > .001 | topic2 > .001) %>%
  mutate(log_ratio = log2(topic2 / topic1))
