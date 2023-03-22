install.packages("~/Downloads/grafzahl.tgz", dependencies = TRUE, repos = NULL)
install.packages("reticulate")
install.packages("pdftools")
require(grafzahl)
require(readtext)
require(quanteda)
library(tidyverse)
library(amcat4r)
library(topicmodels)
library(corpustools)
library(tidytext)
library(ggplot2)
library(dplyr)
library(tidyr)

library (readr)

setup_grafzahl(cuda = TRUE, force=T)

urlfile="https://raw.githubusercontent.com/vanatteveldt/ecosent/master/data/intermediate/sentences_ml.csv"

data<-read_csv(url(urlfile))


#login 
login("https://amcat4.amcat.nl/api", "admin")

data = query_documents(index = "quantum", queries = "*", fields = c("id","date","title","text"))

input <- readtext(urlfile, text_field = "headline") %>%
  corpus


training_corpus <- corpus_subset(input, !gold)
library(cuda.ml)
model <- grafzahl(x = training_corpus,
                  y = "value",
                  model_name = "GroNLP/bert-base-dutch-cased")
